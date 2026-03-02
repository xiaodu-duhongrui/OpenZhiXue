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
	ErrQuestionNotFound = errors.New("question not found")
	ErrInvalidOrder     = errors.New("invalid question order")
)

type QuestionService struct {
	questionRepo *repositories.QuestionRepository
	examRepo     *repositories.ExamRepository
}

func NewQuestionService(
	questionRepo *repositories.QuestionRepository,
	examRepo *repositories.ExamRepository,
) *QuestionService {
	return &QuestionService{
		questionRepo: questionRepo,
		examRepo:     examRepo,
	}
}

func (s *QuestionService) CreateQuestion(ctx context.Context, req *models.QuestionCreateRequest) (*models.Question, error) {
	examID, err := uuid.Parse(req.ExamID)
	if err != nil {
		return nil, fmt.Errorf("invalid exam id: %w", err)
	}

	exam, err := s.examRepo.GetByID(ctx, examID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrExamNotFound
		}
		return nil, fmt.Errorf("failed to get exam: %w", err)
	}

	if exam.Status != models.ExamStatusDraft {
		return nil, ErrExamCannotModify
	}

	question := models.NewQuestion()
	question.ExamID = examID
	question.Type = req.Type
	question.Content = req.Content
	question.Options = req.Options
	question.Answer = req.Answer
	question.Score = req.Score
	question.Order = req.Order
	question.Analysis = req.Analysis
	question.Difficulty = req.Difficulty
	if question.Difficulty == 0 {
		question.Difficulty = 3
	}

	if question.Order == 0 {
		count, err := s.questionRepo.CountByExamID(ctx, examID)
		if err != nil {
			return nil, fmt.Errorf("failed to count questions: %w", err)
		}
		question.Order = count + 1
	}

	if err := s.questionRepo.Create(ctx, question); err != nil {
		return nil, fmt.Errorf("failed to create question: %w", err)
	}

	return question, nil
}

func (s *QuestionService) CreateQuestionsBatch(ctx context.Context, req *models.QuestionBatchCreateRequest) ([]models.Question, error) {
	examID, err := uuid.Parse(req.ExamID)
	if err != nil {
		return nil, fmt.Errorf("invalid exam id: %w", err)
	}

	exam, err := s.examRepo.GetByID(ctx, examID)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrExamNotFound
		}
		return nil, fmt.Errorf("failed to get exam: %w", err)
	}

	if exam.Status != models.ExamStatusDraft {
		return nil, ErrExamCannotModify
	}

	existingCount, err := s.questionRepo.CountByExamID(ctx, examID)
	if err != nil {
		return nil, fmt.Errorf("failed to count questions: %w", err)
	}

	questions := make([]models.Question, len(req.Questions))
	now := time.Now()

	for i, q := range req.Questions {
		questions[i] = models.Question{
			ID:         uuid.New(),
			ExamID:     examID,
			Type:       q.Type,
			Content:    q.Content,
			Options:    q.Options,
			Answer:     q.Answer,
			Score:      q.Score,
			Order:      existingCount + i + 1,
			Analysis:   q.Analysis,
			Difficulty: q.Difficulty,
			CreatedAt:  now,
			UpdatedAt:  now,
		}
		if questions[i].Difficulty == 0 {
			questions[i].Difficulty = 3
		}
	}

	if err := s.questionRepo.CreateBatch(ctx, questions); err != nil {
		return nil, fmt.Errorf("failed to create questions: %w", err)
	}

	return questions, nil
}

func (s *QuestionService) GetQuestion(ctx context.Context, id uuid.UUID) (*models.Question, error) {
	question, err := s.questionRepo.GetByID(ctx, id)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, ErrQuestionNotFound
		}
		return nil, fmt.Errorf("failed to get question: %w", err)
	}
	return question, nil
}

func (s *QuestionService) GetQuestionsByExam(ctx context.Context, examID uuid.UUID) ([]models.Question, error) {
	return s.questionRepo.GetByExamID(ctx, examID)
}

func (s *QuestionService) GetQuestionsForStudent(ctx context.Context, examID uuid.UUID) ([]models.Question, error) {
	return s.questionRepo.GetByExamIDWithoutAnswers(ctx, examID)
}

func (s *QuestionService) UpdateQuestion(ctx context.Context, id uuid.UUID, req *models.QuestionUpdateRequest) (*models.Question, error) {
	question, err := s.GetQuestion(ctx, id)
	if err != nil {
		return nil, err
	}

	exam, err := s.examRepo.GetByID(ctx, question.ExamID)
	if err != nil {
		return nil, fmt.Errorf("failed to get exam: %w", err)
	}

	if exam.Status != models.ExamStatusDraft {
		return nil, ErrExamCannotModify
	}

	if req.Type != "" {
		question.Type = req.Type
	}
	if req.Content != "" {
		question.Content = req.Content
	}
	if req.Options != nil {
		question.Options = req.Options
	}
	if req.Answer != "" {
		question.Answer = req.Answer
	}
	if req.Score > 0 {
		question.Score = req.Score
	}
	if req.Order > 0 {
		question.Order = req.Order
	}
	if req.Analysis != "" {
		question.Analysis = req.Analysis
	}
	if req.Difficulty > 0 {
		question.Difficulty = req.Difficulty
	}

	question.UpdatedAt = time.Now()

	if err := s.questionRepo.Update(ctx, question); err != nil {
		return nil, fmt.Errorf("failed to update question: %w", err)
	}

	return question, nil
}

func (s *QuestionService) DeleteQuestion(ctx context.Context, id uuid.UUID) error {
	question, err := s.GetQuestion(ctx, id)
	if err != nil {
		return err
	}

	exam, err := s.examRepo.GetByID(ctx, question.ExamID)
	if err != nil {
		return fmt.Errorf("failed to get exam: %w", err)
	}

	if exam.Status != models.ExamStatusDraft {
		return ErrExamCannotModify
	}

	return s.questionRepo.Delete(ctx, id)
}

func (s *QuestionService) DeleteQuestionsByExam(ctx context.Context, examID uuid.UUID) error {
	return s.questionRepo.DeleteByExamID(ctx, examID)
}
