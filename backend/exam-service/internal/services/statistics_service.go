package services

import (
	"context"
	"math"
	"sort"

	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/repositories"
)

type StatisticsService struct {
	examRepo    *repositories.ExamRepository
	sessionRepo *repositories.SessionRepository
	answerRepo  *repositories.AnswerRepository
	questionRepo *repositories.QuestionRepository
}

func NewStatisticsService(
	examRepo *repositories.ExamRepository,
	sessionRepo *repositories.SessionRepository,
	answerRepo *repositories.AnswerRepository,
	questionRepo *repositories.QuestionRepository,
) *StatisticsService {
	return &StatisticsService{
		examRepo:     examRepo,
		sessionRepo:  sessionRepo,
		answerRepo:   answerRepo,
		questionRepo: questionRepo,
	}
}

func (s *StatisticsService) GetExamStatistics(ctx context.Context, examID uuid.UUID) (*models.ExamStatistics, error) {
	exam, err := s.examRepo.GetByID(ctx, examID)
	if err != nil {
		return nil, err
	}

	sessions, err := s.sessionRepo.GetByExamID(ctx, examID)
	if err != nil {
		return nil, err
	}

	stats := &models.ExamStatistics{
		ExamID:            examID,
		TotalParticipants: len(sessions),
		GeneratedAt:       exam.CreatedAt,
	}

	scores := []float64{}
	totalDuration := 0
	passCount := 0

	for _, session := range sessions {
		if session.Status == models.SessionStatusSubmitted || session.Status == models.SessionStatusGraded {
			stats.SubmittedCount++
			scores = append(scores, session.TotalScore)
			totalDuration += session.ElapsedTime

			if session.TotalScore >= exam.PassScore {
				passCount++
			}
		}
	}

	if len(scores) > 0 {
		stats.AverageScore = calculateAverage(scores)
		stats.MaxScore = calculateMax(scores)
		stats.MinScore = calculateMin(scores)
		stats.MedianScore = calculateMedian(scores)
		stats.StandardDeviation = calculateStdDev(scores)
		stats.AverageDuration = totalDuration / len(scores)
	}

	if stats.SubmittedCount > 0 {
		stats.PassRate = float64(passCount) / float64(stats.SubmittedCount) * 100
	}

	if stats.TotalParticipants > 0 {
		stats.CompletionRate = float64(stats.SubmittedCount) / float64(stats.TotalParticipants) * 100
	}

	return stats, nil
}

func (s *StatisticsService) GetQuestionStatistics(ctx context.Context, examID uuid.UUID) ([]models.QuestionStatistics, error) {
	questions, err := s.questionRepo.GetByExamID(ctx, examID)
	if err != nil {
		return nil, err
	}

	stats := make([]models.QuestionStatistics, len(questions))
	for i, q := range questions {
		questionStats, err := s.answerRepo.GetQuestionStats(ctx, q.ID)
		if err != nil {
			continue
		}
		questionStats.QuestionOrder = q.Order
		questionStats.QuestionType = string(q.Type)
		stats[i] = *questionStats
	}

	sort.Slice(stats, func(i, j int) bool {
		return stats[i].QuestionOrder < stats[j].QuestionOrder
	})

	return stats, nil
}

func (s *StatisticsService) GetScoreDistribution(ctx context.Context, examID uuid.UUID) ([]models.ScoreDistribution, error) {
	sessions, err := s.sessionRepo.GetByExamID(ctx, examID)
	if err != nil {
		return nil, err
	}

	exam, err := s.examRepo.GetByID(ctx, examID)
	if err != nil {
		return nil, err
	}

	ranges := []struct {
		min, max float64
		label    string
	}{
		{0, 59, "0-59"},
		{60, 69, "60-69"},
		{70, 79, "70-79"},
		{80, 89, "80-89"},
		{90, 100, "90-100"},
	}

	distribution := make([]models.ScoreDistribution, len(ranges))
	for i, r := range ranges {
		distribution[i] = models.ScoreDistribution{
			ScoreRange: r.label,
			Count:      0,
		}
	}

	totalSubmitted := 0
	for _, session := range sessions {
		if session.Status == models.SessionStatusSubmitted || session.Status == models.SessionStatusGraded {
			totalSubmitted++
			percentage := (session.TotalScore / exam.TotalScore) * 100

			for i, r := range ranges {
				if percentage >= r.min && percentage <= r.max {
					distribution[i].Count++
					break
				}
			}
		}
	}

	for i := range distribution {
		if totalSubmitted > 0 {
			distribution[i].Percentage = float64(distribution[i].Count) / float64(totalSubmitted) * 100
		}
	}

	return distribution, nil
}

func (s *StatisticsService) GetExamAnalysis(ctx context.Context, examID uuid.UUID) (*models.ExamAnalysis, error) {
	stats, err := s.GetExamStatistics(ctx, examID)
	if err != nil {
		return nil, err
	}

	questionStats, err := s.GetQuestionStatistics(ctx, examID)
	if err != nil {
		return nil, err
	}

	scoreDistribution, err := s.GetScoreDistribution(ctx, examID)
	if err != nil {
		return nil, err
	}

	topPerformers, err := s.GetTopPerformers(ctx, examID, 10)
	if err != nil {
		return nil, err
	}

	bottomPerformers, err := s.GetBottomPerformers(ctx, examID, 10)
	if err != nil {
		return nil, err
	}

	return &models.ExamAnalysis{
		ExamID:            examID,
		Statistics:        *stats,
		QuestionStats:     questionStats,
		ScoreDistribution: scoreDistribution,
		TopPerformers:     topPerformers,
		BottomPerformers:  bottomPerformers,
		GeneratedAt:       stats.GeneratedAt,
	}, nil
}

func (s *StatisticsService) GetTopPerformers(ctx context.Context, examID uuid.UUID, limit int) ([]models.StudentScore, error) {
	sessions, err := s.sessionRepo.GetByExamID(ctx, examID)
	if err != nil {
		return nil, err
	}

	sort.Slice(sessions, func(i, j int) bool {
		return sessions[i].TotalScore > sessions[j].TotalScore
	})

	performers := []models.StudentScore{}
	for i, session := range sessions {
		if len(performers) >= limit {
			break
		}
		if session.Status == models.SessionStatusSubmitted || session.Status == models.SessionStatusGraded {
			performers = append(performers, models.StudentScore{
				StudentID:  session.StudentID,
				Score:      session.TotalScore,
				Rank:       i + 1,
				Percentile: float64(len(sessions)-i) / float64(len(sessions)) * 100,
			})
		}
	}

	return performers, nil
}

func (s *StatisticsService) GetBottomPerformers(ctx context.Context, examID uuid.UUID, limit int) ([]models.StudentScore, error) {
	sessions, err := s.sessionRepo.GetByExamID(ctx, examID)
	if err != nil {
		return nil, err
	}

	sort.Slice(sessions, func(i, j int) bool {
		return sessions[i].TotalScore < sessions[j].TotalScore
	})

	performers := []models.StudentScore{}
	for i, session := range sessions {
		if len(performers) >= limit {
			break
		}
		if session.Status == models.SessionStatusSubmitted || session.Status == models.SessionStatusGraded {
			performers = append(performers, models.StudentScore{
				StudentID:  session.StudentID,
				Score:      session.TotalScore,
				Rank:       len(sessions) - i,
				Percentile: float64(i+1) / float64(len(sessions)) * 100,
			})
		}
	}

	return performers, nil
}

func (s *StatisticsService) GetRanking(ctx context.Context, examID uuid.UUID, page, pageSize int) (*models.RankingResponse, error) {
	sessions, err := s.sessionRepo.GetByExamID(ctx, examID)
	if err != nil {
		return nil, err
	}

	sort.Slice(sessions, func(i, j int) bool {
		return sessions[i].TotalScore > sessions[j].TotalScore
	})

	submittedSessions := []models.ExamSession{}
	for _, session := range sessions {
		if session.Status == models.SessionStatusSubmitted || session.Status == models.SessionStatusGraded {
			submittedSessions = append(submittedSessions, session)
		}
	}

	total := len(submittedSessions)
	start := (page - 1) * pageSize
	end := start + pageSize
	if start > total {
		start = total
	}
	if end > total {
		end = total
	}

	rankings := []models.StudentScore{}
	for i := start; i < end; i++ {
		rankings = append(rankings, models.StudentScore{
			StudentID:  submittedSessions[i].StudentID,
			Score:      submittedSessions[i].TotalScore,
			Rank:       i + 1,
			Percentile: float64(total-i) / float64(total) * 100,
		})
	}

	return &models.RankingResponse{
		Rankings: rankings,
		Total:    total,
		Page:     page,
		PageSize: pageSize,
	}, nil
}

func calculateAverage(scores []float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	sum := 0.0
	for _, s := range scores {
		sum += s
	}
	return math.Round(sum/float64(len(scores))*100) / 100
}

func calculateMax(scores []float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	max := scores[0]
	for _, s := range scores {
		if s > max {
			max = s
		}
	}
	return max
}

func calculateMin(scores []float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	min := scores[0]
	for _, s := range scores {
		if s < min {
			min = s
		}
	}
	return min
}

func calculateMedian(scores []float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	sort.Float64s(scores)
	n := len(scores)
	if n%2 == 0 {
		return (scores[n/2-1] + scores[n/2]) / 2
	}
	return scores[n/2]
}

func calculateStdDev(scores []float64) float64 {
	if len(scores) == 0 {
		return 0
	}
	mean := calculateAverage(scores)
	variance := 0.0
	for _, s := range scores {
		variance += math.Pow(s-mean, 2)
	}
	variance /= float64(len(scores))
	return math.Round(math.Sqrt(variance)*100) / 100
}
