package services

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/repositories"
)

var (
	ErrExamNotFound       = errors.New("exam not found")
	ErrExamAlreadyExists  = errors.New("exam already exists")
	ErrExamCannotModify   = errors.New("exam cannot be modified in current status")
	ErrExamCannotDelete   = errors.New("exam cannot be deleted in current status")
	ErrExamCannotPublish  = errors.New("exam cannot be published")
	ErrInvalidTimeRange   = errors.New("invalid time range")
	ErrNoQuestions        = errors.New("exam has no questions")
)

type ExamService struct {
	examRepo     *repositories.ExamRepository
	questionRepo *repositories.QuestionRepository
	sessionRepo  *repositories.SessionRepository
}

func NewExamService(
	examRepo *repositories.ExamRepository,
	questionRepo *repositories.QuestionRepository,
	sessionRepo *repositories.SessionRepository,
) *ExamService {
	return &ExamService{
		examRepo:     examRepo,
		questionRepo: questionRepo,
		sessionRepo:  sessionRepo,
	}
}

func (s *ExamService) CreateExam(ctx context.Context, req *models.ExamCreateRequest, creatorID uuid.UUID) (*models.Exam, error) {
	startTime, err := time.Parse(time.RFC3339, req.StartTime)
	if err != nil {
		return nil, fmt.Errorf("invalid start time format: %w", err)
	}

	endTime, err := time.Parse(time.RFC3339, req.EndTime)
	if err != nil {
		return nil, fmt.Errorf("invalid end time format: %w", err)
	}

	if endTime.Before(startTime) {
		return nil, ErrInvalidTimeRange
	}

	exam := models.NewExam()
	exam.Name = req.Name
	exam.Type = req.Type
	exam.SubjectIDs = req.SubjectIDs
	exam.ClassIDs = req.ClassIDs
	exam.StartTime = startTime
	exam.EndTime = endTime
	exam.Duration = req.Duration
	exam.TotalScore = req.TotalScore
	exam.PassScore = req.PassScore
	if exam.PassScore == 0 {
		exam.PassScore = 60
	}
	exam.Description = req.Description
	exam.CreatedBy = creatorID

	if err := s.examRepo.Create(ctx, exam); err != nil {
		return nil, fmt.Errorf("failed to create exam: %w", err)
	}

	return exam, nil
}

func (s *ExamService) GetExam(ctx context.Context, id uuid.UUID) (*models.Exam, error) {
	exam, err := s.examRepo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrExamNotFound
		}
		return nil, fmt.Errorf("failed to get exam: %w", err)
	}
	return exam, nil
}

func (s *ExamService) GetExamWithQuestions(ctx context.Context, id uuid.UUID) (*models.Exam, []models.Question, error) {
	exam, err := s.GetExam(ctx, id)
	if err != nil {
		return nil, nil, err
	}

	questions, err := s.questionRepo.GetByExamID(ctx, id)
	if err != nil {
		return nil, nil, fmt.Errorf("failed to get questions: %w", err)
	}

	return exam, questions, nil
}

func (s *ExamService) UpdateExam(ctx context.Context, id uuid.UUID, req *models.ExamUpdateRequest) (*models.Exam, error) {
	exam, err := s.GetExam(ctx, id)
	if err != nil {
		return nil, err
	}

	if exam.Status != models.ExamStatusDraft {
		return nil, ErrExamCannotModify
	}

	if req.Name != "" {
		exam.Name = req.Name
	}
	if req.Type != "" {
		exam.Type = req.Type
	}
	if len(req.SubjectIDs) > 0 {
		exam.SubjectIDs = req.SubjectIDs
	}
	if len(req.ClassIDs) > 0 {
		exam.ClassIDs = req.ClassIDs
	}
	if req.StartTime != "" {
		startTime, err := time.Parse(time.RFC3339, req.StartTime)
		if err != nil {
			return nil, fmt.Errorf("invalid start time format: %w", err)
		}
		exam.StartTime = startTime
	}
	if req.EndTime != "" {
		endTime, err := time.Parse(time.RFC3339, req.EndTime)
		if err != nil {
			return nil, fmt.Errorf("invalid end time format: %w", err)
		}
		exam.EndTime = endTime
	}
	if exam.EndTime.Before(exam.StartTime) {
		return nil, ErrInvalidTimeRange
	}
	if req.Duration > 0 {
		exam.Duration = req.Duration
	}
	if req.TotalScore > 0 {
		exam.TotalScore = req.TotalScore
	}
	if req.PassScore > 0 {
		exam.PassScore = req.PassScore
	}
	if req.Description != "" {
		exam.Description = req.Description
	}

	if err := s.examRepo.Update(ctx, exam); err != nil {
		return nil, fmt.Errorf("failed to update exam: %w", err)
	}

	return exam, nil
}

func (s *ExamService) DeleteExam(ctx context.Context, id uuid.UUID) error {
	exam, err := s.GetExam(ctx, id)
	if err != nil {
		return err
	}

	if exam.Status != models.ExamStatusDraft {
		return ErrExamCannotDelete
	}

	return s.examRepo.Delete(ctx, id)
}

func (s *ExamService) ListExams(ctx context.Context, filter *models.ExamFilter) (*models.ExamListResponse, error) {
	if filter.Page < 1 {
		filter.Page = 1
	}
	if filter.PageSize < 1 {
		filter.PageSize = 10
	}

	exams, total, err := s.examRepo.List(ctx, filter)
	if err != nil {
		return nil, fmt.Errorf("failed to list exams: %w", err)
	}

	totalPages := int(total) / filter.PageSize
	if int(total)%filter.PageSize > 0 {
		totalPages++
	}

	return &models.ExamListResponse{
		Exams:      exams,
		Total:      total,
		Page:       filter.Page,
		PageSize:   filter.PageSize,
		TotalPages: totalPages,
	}, nil
}

func (s *ExamService) PublishExam(ctx context.Context, id uuid.UUID) error {
	exam, err := s.GetExam(ctx, id)
	if err != nil {
		return err
	}

	if exam.Status != models.ExamStatusDraft {
		return ErrExamCannotPublish
	}

	questionCount, err := s.questionRepo.CountByExamID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to count questions: %w", err)
	}

	if questionCount == 0 {
		return ErrNoQuestions
	}

	totalScore, err := s.questionRepo.GetTotalScoreByExamID(ctx, id)
	if err != nil {
		return fmt.Errorf("failed to get total score: %w", err)
	}

	exam.TotalScore = totalScore
	exam.Status = models.ExamStatusPublished

	if err := s.examRepo.Update(ctx, exam); err != nil {
		return fmt.Errorf("failed to publish exam: %w", err)
	}

	return nil
}

func (s *ExamService) UpdateExamStatus(ctx context.Context, id uuid.UUID, status models.ExamStatus) error {
	return s.examRepo.UpdateStatus(ctx, id, status)
}

func (s *ExamService) GetExamsByClass(ctx context.Context, classID string) ([]models.Exam, error) {
	return s.examRepo.GetByClassID(ctx, classID)
}

func (s *ExamService) RecalculateTotalScore(ctx context.Context, id uuid.UUID) error {
	totalScore, err := s.questionRepo.GetTotalScoreByExamID(ctx, id)
	if err != nil {
		return err
	}

	exam, err := s.GetExam(ctx, id)
	if err != nil {
		return err
	}

	exam.TotalScore = totalScore
	return s.examRepo.Update(ctx, exam)
}
