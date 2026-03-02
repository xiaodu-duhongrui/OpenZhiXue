package services

import (
	"context"
	"database/sql"
	"errors"
	"testing"
	"time"

	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockExamRepository struct {
	mock.Mock
}

func (m *MockExamRepository) Create(ctx context.Context, exam *models.Exam) error {
	args := m.Called(ctx, exam)
	return args.Error(0)
}

func (m *MockExamRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.Exam, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Exam), args.Error(1)
}

func (m *MockExamRepository) Update(ctx context.Context, exam *models.Exam) error {
	args := m.Called(ctx, exam)
	return args.Error(0)
}

func (m *MockExamRepository) Delete(ctx context.Context, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockExamRepository) List(ctx context.Context, filter *models.ExamFilter) ([]models.Exam, int64, error) {
	args := m.Called(ctx, filter)
	return args.Get(0).([]models.Exam), args.Get(1).(int64), args.Error(2)
}

func (m *MockExamRepository) UpdateStatus(ctx context.Context, id uuid.UUID, status models.ExamStatus) error {
	args := m.Called(ctx, id, status)
	return args.Error(0)
}

func (m *MockExamRepository) GetByClassID(ctx context.Context, classID string) ([]models.Exam, error) {
	args := m.Called(ctx, classID)
	return args.Get(0).([]models.Exam), args.Error(1)
}

type MockQuestionRepository struct {
	mock.Mock
}

func (m *MockQuestionRepository) GetByExamID(ctx context.Context, examID uuid.UUID) ([]models.Question, error) {
	args := m.Called(ctx, examID)
	return args.Get(0).([]models.Question), args.Error(1)
}

func (m *MockQuestionRepository) CountByExamID(ctx context.Context, examID uuid.UUID) (int, error) {
	args := m.Called(ctx, examID)
	return args.Int(0), args.Error(1)
}

func (m *MockQuestionRepository) GetTotalScoreByExamID(ctx context.Context, examID uuid.UUID) (float64, error) {
	args := m.Called(ctx, examID)
	return args.Get(0).(float64), args.Error(1)
}

func (m *MockQuestionRepository) Create(ctx context.Context, question *models.Question) error {
	args := m.Called(ctx, question)
	return args.Error(0)
}

type MockSessionRepository struct {
	mock.Mock
}

func (m *MockSessionRepository) Create(ctx context.Context, session *models.ExamSession) error {
	args := m.Called(ctx, session)
	return args.Error(0)
}

func (m *MockSessionRepository) GetByID(ctx context.Context, id uuid.UUID) (*models.ExamSession, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.ExamSession), args.Error(1)
}

func (m *MockSessionRepository) Update(ctx context.Context, session *models.ExamSession) error {
	args := m.Called(ctx, session)
	return args.Error(0)
}

func TestExamService_CreateExam_Success(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	creatorID := uuid.New()
	
	req := &models.ExamCreateRequest{
		Name:       "Test Exam",
		Type:       "midterm",
		StartTime:  time.Now().Add(24 * time.Hour).Format(time.RFC3339),
		EndTime:    time.Now().Add(48 * time.Hour).Format(time.RFC3339),
		Duration:   120,
		TotalScore: 100,
		PassScore:  60,
	}
	
	examRepo.On("Create", ctx, mock.AnythingOfType("*models.Exam")).Return(nil)
	
	exam, err := service.CreateExam(ctx, req, creatorID)
	
	assert.NoError(t, err)
	assert.NotNil(t, exam)
	assert.Equal(t, "Test Exam", exam.Name)
	assert.Equal(t, models.ExamStatusDraft, exam.Status)
	assert.Equal(t, creatorID, exam.CreatedBy)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_CreateExam_InvalidTimeRange(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	creatorID := uuid.New()
	
	req := &models.ExamCreateRequest{
		Name:      "Test Exam",
		Type:      "midterm",
		StartTime: time.Now().Add(48 * time.Hour).Format(time.RFC3339),
		EndTime:   time.Now().Add(24 * time.Hour).Format(time.RFC3339),
		Duration:  120,
	}
	
	exam, err := service.CreateExam(ctx, req, creatorID)
	
	assert.Error(t, err)
	assert.Equal(t, ErrInvalidTimeRange, err)
	assert.Nil(t, exam)
}

func TestExamService_GetExam_Success(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	expectedExam := &models.Exam{
		ID:     examID,
		Name:   "Test Exam",
		Status: models.ExamStatusDraft,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(expectedExam, nil)
	
	exam, err := service.GetExam(ctx, examID)
	
	assert.NoError(t, err)
	assert.Equal(t, expectedExam, exam)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_GetExam_NotFound(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	examRepo.On("GetByID", ctx, examID).Return(nil, sql.ErrNoRows)
	
	exam, err := service.GetExam(ctx, examID)
	
	assert.Error(t, err)
	assert.Equal(t, ErrExamNotFound, err)
	assert.Nil(t, exam)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_UpdateExam_Success(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	existingExam := &models.Exam{
		ID:     examID,
		Name:   "Old Name",
		Status: models.ExamStatusDraft,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(existingExam, nil)
	examRepo.On("Update", ctx, existingExam).Return(nil)
	
	req := &models.ExamUpdateRequest{
		Name: "New Name",
	}
	
	exam, err := service.UpdateExam(ctx, examID, req)
	
	assert.NoError(t, err)
	assert.Equal(t, "New Name", exam.Name)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_UpdateExam_CannotModify(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	existingExam := &models.Exam{
		ID:     examID,
		Name:   "Test Exam",
		Status: models.ExamStatusPublished,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(existingExam, nil)
	
	req := &models.ExamUpdateRequest{
		Name: "New Name",
	}
	
	exam, err := service.UpdateExam(ctx, examID, req)
	
	assert.Error(t, err)
	assert.Equal(t, ErrExamCannotModify, err)
	assert.Nil(t, exam)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_DeleteExam_Success(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	existingExam := &models.Exam{
		ID:     examID,
		Status: models.ExamStatusDraft,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(existingExam, nil)
	examRepo.On("Delete", ctx, examID).Return(nil)
	
	err := service.DeleteExam(ctx, examID)
	
	assert.NoError(t, err)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_DeleteExam_CannotDelete(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	existingExam := &models.Exam{
		ID:     examID,
		Status: models.ExamStatusPublished,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(existingExam, nil)
	
	err := service.DeleteExam(ctx, examID)
	
	assert.Error(t, err)
	assert.Equal(t, ErrExamCannotDelete, err)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_PublishExam_Success(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	existingExam := &models.Exam{
		ID:     examID,
		Status: models.ExamStatusDraft,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(existingExam, nil)
	questionRepo.On("CountByExamID", ctx, examID).Return(10, nil)
	questionRepo.On("GetTotalScoreByExamID", ctx, examID).Return(100.0, nil)
	examRepo.On("Update", ctx, existingExam).Return(nil)
	
	err := service.PublishExam(ctx, examID)
	
	assert.NoError(t, err)
	assert.Equal(t, models.ExamStatusPublished, existingExam.Status)
	
	examRepo.AssertExpectations(t)
	questionRepo.AssertExpectations(t)
}

func TestExamService_PublishExam_NoQuestions(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	existingExam := &models.Exam{
		ID:     examID,
		Status: models.ExamStatusDraft,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(existingExam, nil)
	questionRepo.On("CountByExamID", ctx, examID).Return(0, nil)
	
	err := service.PublishExam(ctx, examID)
	
	assert.Error(t, err)
	assert.Equal(t, ErrNoQuestions, err)
	
	examRepo.AssertExpectations(t)
	questionRepo.AssertExpectations(t)
}

func TestExamService_PublishExam_CannotPublish(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	existingExam := &models.Exam{
		ID:     examID,
		Status: models.ExamStatusPublished,
	}
	
	examRepo.On("GetByID", ctx, examID).Return(existingExam, nil)
	
	err := service.PublishExam(ctx, examID)
	
	assert.Error(t, err)
	assert.Equal(t, ErrExamCannotPublish, err)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_ListExams(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	
	exams := []models.Exam{
		{ID: uuid.New(), Name: "Exam 1"},
		{ID: uuid.New(), Name: "Exam 2"},
	}
	
	filter := &models.ExamFilter{
		Page:     1,
		PageSize: 10,
	}
	
	examRepo.On("List", ctx, filter).Return(exams, int64(2), nil)
	
	response, err := service.ListExams(ctx, filter)
	
	assert.NoError(t, err)
	assert.NotNil(t, response)
	assert.Len(t, response.Exams, 2)
	assert.Equal(t, int64(2), response.Total)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_ListExams_DefaultPagination(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	
	filter := &models.ExamFilter{}
	
	examRepo.On("List", ctx, filter).Return([]models.Exam{}, int64(0), nil)
	
	response, err := service.ListExams(ctx, filter)
	
	assert.NoError(t, err)
	assert.Equal(t, 1, filter.Page)
	assert.Equal(t, 10, filter.PageSize)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_GetExamWithQuestions(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	exam := &models.Exam{
		ID:   examID,
		Name: "Test Exam",
	}
	
	questions := []models.Question{
		{ID: uuid.New(), Content: "Question 1"},
		{ID: uuid.New(), Content: "Question 2"},
	}
	
	examRepo.On("GetByID", ctx, examID).Return(exam, nil)
	questionRepo.On("GetByExamID", ctx, examID).Return(questions, nil)
	
	resultExam, resultQuestions, err := service.GetExamWithQuestions(ctx, examID)
	
	assert.NoError(t, err)
	assert.Equal(t, exam, resultExam)
	assert.Len(t, resultQuestions, 2)
	
	examRepo.AssertExpectations(t)
	questionRepo.AssertExpectations(t)
}

func TestExamService_UpdateExamStatus(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	examRepo.On("UpdateStatus", ctx, examID, models.ExamStatusInProgress).Return(nil)
	
	err := service.UpdateExamStatus(ctx, examID, models.ExamStatusInProgress)
	
	assert.NoError(t, err)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_GetExamsByClass(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	classID := "class-123"
	
	exams := []models.Exam{
		{ID: uuid.New(), Name: "Exam 1"},
	}
	
	examRepo.On("GetByClassID", ctx, classID).Return(exams, nil)
	
	result, err := service.GetExamsByClass(ctx, classID)
	
	assert.NoError(t, err)
	assert.Len(t, result, 1)
	
	examRepo.AssertExpectations(t)
}

func TestExamService_RecalculateTotalScore(t *testing.T) {
	examRepo := new(MockExamRepository)
	questionRepo := new(MockQuestionRepository)
	sessionRepo := new(MockSessionRepository)
	
	service := NewExamService(examRepo, questionRepo, sessionRepo)
	
	ctx := context.Background()
	examID := uuid.New()
	
	exam := &models.Exam{
		ID:         examID,
		TotalScore: 0,
	}
	
	questionRepo.On("GetTotalScoreByExamID", ctx, examID).Return(150.0, nil)
	examRepo.On("GetByID", ctx, examID).Return(exam, nil)
	examRepo.On("Update", ctx, exam).Return(nil)
	
	err := service.RecalculateTotalScore(ctx, examID)
	
	assert.NoError(t, err)
	assert.Equal(t, 150.0, exam.TotalScore)
	
	questionRepo.AssertExpectations(t)
	examRepo.AssertExpectations(t)
}
