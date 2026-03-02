package services

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"math"
	"sort"
	"time"

	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/repositories"
)

var (
	ErrAnswerNotFound      = errors.New("answer not found")
	ErrCannotGrade         = errors.New("cannot grade answer in current state")
	ErrInvalidScore        = errors.New("invalid score")
)

type GradingService struct {
	answerRepo  *repositories.AnswerRepository
	sessionRepo *repositories.SessionRepository
	questionRepo *repositories.QuestionRepository
	examRepo    *repositories.ExamRepository
}

func NewGradingService(
	answerRepo *repositories.AnswerRepository,
	sessionRepo *repositories.SessionRepository,
	questionRepo *repositories.QuestionRepository,
	examRepo *repositories.ExamRepository,
) *GradingService {
	return &GradingService{
		answerRepo:   answerRepo,
		sessionRepo:  sessionRepo,
		questionRepo: questionRepo,
		examRepo:     examRepo,
	}
}

func (s *GradingService) AutoGradeSession(ctx context.Context, sessionID uuid.UUID) error {
	session, err := s.sessionRepo.GetByID(ctx, sessionID)
	if err != nil {
		return fmt.Errorf("failed to get session: %w", err)
	}

	if session.Status != models.SessionStatusSubmitted {
		return ErrCannotGrade
	}

	answers, err := s.answerRepo.GetBySessionID(ctx, sessionID)
	if err != nil {
		return fmt.Errorf("failed to get answers: %w", err)
	}

	questions, err := s.questionRepo.GetByExamID(ctx, session.ExamID)
	if err != nil {
		return fmt.Errorf("failed to get questions: %w", err)
	}

	questionMap := make(map[uuid.UUID]models.Question)
	for _, q := range questions {
		questionMap[q.ID] = q
	}

	for _, answer := range answers {
		question, ok := questionMap[answer.QuestionID]
		if !ok {
			continue
		}

		if question.IsObjective() {
			isCorrect, score := question.CheckAnswer(answer.Answer)
			answer.Score = score
			answer.AutoGraded = true
			answer.UpdatedAt = time.Now()

			if isCorrect {
				answer.Status = models.AnswerStatusCorrect
			} else {
				answer.Status = models.AnswerStatusWrong
			}

			if err := s.answerRepo.Update(ctx, &answer); err != nil {
				return fmt.Errorf("failed to update answer: %w", err)
			}
		}
	}

	totalScore, err := s.answerRepo.GetTotalScoreBySession(ctx, sessionID)
	if err != nil {
		return fmt.Errorf("failed to get total score: %w", err)
	}

	session.TotalScore = totalScore
	allGraded, err := s.isFullyGraded(ctx, sessionID)
	if err != nil {
		return err
	}

	if allGraded {
		session.Status = models.SessionStatusGraded
	}

	return s.sessionRepo.Update(ctx, session)
}

func (s *GradingService) GradeAnswer(ctx context.Context, req *models.GradeAnswerRequest, graderID uuid.UUID) (*models.GradeResponse, error) {
	sessionID, err := uuid.Parse(req.SessionID)
	if err != nil {
		return nil, fmt.Errorf("invalid session id: %w", err)
	}

	questionID, err := uuid.Parse(req.QuestionID)
	if err != nil {
		return nil, fmt.Errorf("invalid question id: %w", err)
	}

	session, err := s.sessionRepo.GetByID(ctx, sessionID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrSessionNotFound
		}
		return nil, fmt.Errorf("failed to get session: %w", err)
	}

	if session.Status != models.SessionStatusSubmitted && session.Status != models.SessionStatusGraded {
		return nil, ErrCannotGrade
	}

	answer, err := s.answerRepo.GetBySessionAndQuestion(ctx, sessionID, questionID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrAnswerNotFound
		}
		return nil, fmt.Errorf("failed to get answer: %w", err)
	}

	question, err := s.questionRepo.GetByID(ctx, questionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get question: %w", err)
	}

	if req.Score < 0 || req.Score > question.Score {
		return nil, ErrInvalidScore
	}

	status := models.AnswerStatusGraded
	if req.Score == question.Score {
		status = models.AnswerStatusCorrect
	} else if req.Score == 0 {
		status = models.AnswerStatusWrong
	} else {
		status = models.AnswerStatusPartial
	}

	if err := s.answerRepo.UpdateScore(ctx, answer.ID, req.Score, status, graderID, req.Feedback); err != nil {
		return nil, fmt.Errorf("failed to update score: %w", err)
	}

	totalScore, err := s.answerRepo.GetTotalScoreBySession(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get total score: %w", err)
	}

	gradedCount, err := s.answerRepo.CountGradedBySession(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to count graded: %w", err)
	}

	totalCount, err := s.answerRepo.CountTotalBySession(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to count total: %w", err)
	}

	session.TotalScore = totalScore
	if gradedCount == totalCount {
		session.Status = models.SessionStatusGraded
	}
	s.sessionRepo.Update(ctx, session)

	return &models.GradeResponse{
		SessionID:   sessionID,
		TotalScore:  totalScore,
		GradedCount: gradedCount,
		TotalCount:  totalCount,
		IsComplete:  gradedCount == totalCount,
	}, nil
}

func (s *GradingService) isFullyGraded(ctx context.Context, sessionID uuid.UUID) (bool, error) {
	gradedCount, err := s.answerRepo.CountGradedBySession(ctx, sessionID)
	if err != nil {
		return false, err
	}

	totalCount, err := s.answerRepo.CountTotalBySession(ctx, sessionID)
	if err != nil {
		return false, err
	}

	return gradedCount == totalCount, nil
}

func (s *GradingService) GetStudentResult(ctx context.Context, sessionID uuid.UUID) (*models.StudentResult, error) {
	session, err := s.sessionRepo.GetByID(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get session: %w", err)
	}

	exam, err := s.examRepo.GetByID(ctx, session.ExamID)
	if err != nil {
		return nil, fmt.Errorf("failed to get exam: %w", err)
	}

	answers, err := s.answerRepo.GetBySessionID(ctx, sessionID)
	if err != nil {
		return nil, fmt.Errorf("failed to get answers: %w", err)
	}

	questions, err := s.questionRepo.GetByExamID(ctx, session.ExamID)
	if err != nil {
		return nil, fmt.Errorf("failed to get questions: %w", err)
	}

	questionMap := make(map[uuid.UUID]models.Question)
	for _, q := range questions {
		questionMap[q.ID] = q
	}

	answerResults := make([]models.AnswerResult, len(answers))
	for i, a := range answers {
		q := questionMap[a.QuestionID]
		answerResults[i] = models.AnswerResult{
			QuestionID:    a.QuestionID,
			QuestionOrder: q.Order,
			QuestionType:  string(q.Type),
			StudentAnswer: a.Answer,
			CorrectAnswer: q.Answer,
			Score:         a.Score,
			MaxScore:      a.MaxScore,
			IsCorrect:     a.Status == models.AnswerStatusCorrect,
			Feedback:      a.Feedback,
		}
	}

	sort.Slice(answerResults, func(i, j int) bool {
		return answerResults[i].QuestionOrder < answerResults[j].QuestionOrder
	})

	percentage := 0.0
	if exam.TotalScore > 0 {
		percentage = (session.TotalScore / exam.TotalScore) * 100
	}

	result := &models.StudentResult{
		SessionID:   session.ID,
		ExamID:      session.ExamID,
		StudentID:   session.StudentID,
		TotalScore:  session.TotalScore,
		MaxScore:    exam.TotalScore,
		Percentage:  math.Round(percentage*100) / 100,
		Passed:      session.TotalScore >= exam.PassScore,
		Answers:     answerResults,
		Duration:    session.ElapsedTime,
	}

	if session.SubmitTime != nil {
		result.SubmittedAt = *session.SubmitTime
	}

	scores, err := s.sessionRepo.GetScoresByExamID(ctx, session.ExamID)
	if err == nil && len(scores) > 0 {
		sort.Float64s(scores)
		for i, score := range scores {
			if score == session.TotalScore {
				result.Rank = len(scores) - i
				break
			}
		}
		result.Percentile = float64(result.Rank) / float64(len(scores)) * 100
	}

	return result, nil
}
