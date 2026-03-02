package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/openzhixue/exam-service/internal/models"
	"github.com/openzhixue/exam-service/internal/services"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockExamService struct {
	mock.Mock
}

func (m *MockExamService) CreateExam(ctx interface{}, req *models.ExamCreateRequest, creatorID uuid.UUID) (*models.Exam, error) {
	args := m.Called(ctx, req, creatorID)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Exam), args.Error(1)
}

func (m *MockExamService) GetExam(ctx interface{}, id uuid.UUID) (*models.Exam, error) {
	args := m.Called(ctx, id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Exam), args.Error(1)
}

func (m *MockExamService) GetExamWithQuestions(ctx interface{}, id uuid.UUID) (*models.Exam, []models.Question, error) {
	args := m.Called(ctx, id)
	return args.Get(0).(*models.Exam), args.Get(1).([]models.Question), args.Error(2)
}

func (m *MockExamService) UpdateExam(ctx interface{}, id uuid.UUID, req *models.ExamUpdateRequest) (*models.Exam, error) {
	args := m.Called(ctx, id, req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Exam), args.Error(1)
}

func (m *MockExamService) DeleteExam(ctx interface{}, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func (m *MockExamService) ListExams(ctx interface{}, filter *models.ExamFilter) (*models.ExamListResponse, error) {
	args := m.Called(ctx, filter)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.ExamListResponse), args.Error(1)
}

func (m *MockExamService) PublishExam(ctx interface{}, id uuid.UUID) error {
	args := m.Called(ctx, id)
	return args.Error(0)
}

func TestExamHandler_CreateExam_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	userID := uuid.New()
	req := models.ExamCreateRequest{
		Name:      "Test Exam",
		Type:      "midterm",
		StartTime: "2024-01-01T00:00:00Z",
		EndTime:   "2024-01-02T00:00:00Z",
		Duration:  120,
	}
	
	body, _ := json.Marshal(req)
	
	expectedExam := &models.Exam{
		ID:   uuid.New(),
		Name: "Test Exam",
	}
	
	mockService.On("CreateExam", mock.Anything, &req, userID).Return(expectedExam, nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/exams", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Set("userID", userID)
	
	handler.CreateExam(c)
	
	assert.Equal(t, http.StatusCreated, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_CreateExam_InvalidRequest(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/exams", bytes.NewBuffer([]byte("{}")))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Set("userID", uuid.New())
	
	handler.CreateExam(c)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestExamHandler_CreateExam_Unauthorized(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	req := models.ExamCreateRequest{
		Name: "Test Exam",
	}
	
	body, _ := json.Marshal(req)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/exams", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	
	handler.CreateExam(c)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestExamHandler_GetExam_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	expectedExam := &models.Exam{
		ID:   examID,
		Name: "Test Exam",
	}
	
	mockService.On("GetExam", mock.Anything, examID).Return(expectedExam, nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodGet, "/exams/"+examID.String(), nil)
	
	handler.GetExam(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_GetExam_InvalidID(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: "invalid-uuid"}}
	c.Request = httptest.NewRequest(http.MethodGet, "/exams/invalid-uuid", nil)
	
	handler.GetExam(c)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestExamHandler_GetExam_NotFound(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	
	mockService.On("GetExam", mock.Anything, examID).Return(nil, services.ErrExamNotFound)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodGet, "/exams/"+examID.String(), nil)
	
	handler.GetExam(c)
	
	assert.Equal(t, http.StatusNotFound, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_ListExams_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	response := &models.ExamListResponse{
		Exams: []models.Exam{
			{ID: uuid.New(), Name: "Exam 1"},
		},
		Total:      1,
		Page:       1,
		PageSize:   10,
		TotalPages: 1,
	}
	
	mockService.On("ListExams", mock.Anything, mock.AnythingOfType("*models.ExamFilter")).Return(response, nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodGet, "/exams", nil)
	
	handler.ListExams(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_UpdateExam_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	req := models.ExamUpdateRequest{
		Name: "Updated Name",
	}
	
	body, _ := json.Marshal(req)
	
	expectedExam := &models.Exam{
		ID:   examID,
		Name: "Updated Name",
	}
	
	mockService.On("UpdateExam", mock.Anything, examID, &req).Return(expectedExam, nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodPut, "/exams/"+examID.String(), bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	
	handler.UpdateExam(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_UpdateExam_CannotModify(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	req := models.ExamUpdateRequest{
		Name: "Updated Name",
	}
	
	body, _ := json.Marshal(req)
	
	mockService.On("UpdateExam", mock.Anything, examID, &req).Return(nil, services.ErrExamCannotModify)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodPut, "/exams/"+examID.String(), bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	
	handler.UpdateExam(c)
	
	assert.Equal(t, http.StatusForbidden, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_DeleteExam_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	
	mockService.On("DeleteExam", mock.Anything, examID).Return(nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodDelete, "/exams/"+examID.String(), nil)
	
	handler.DeleteExam(c)
	
	assert.Equal(t, http.StatusNoContent, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_DeleteExam_CannotDelete(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	
	mockService.On("DeleteExam", mock.Anything, examID).Return(services.ErrExamCannotDelete)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodDelete, "/exams/"+examID.String(), nil)
	
	handler.DeleteExam(c)
	
	assert.Equal(t, http.StatusForbidden, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_PublishExam_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	
	mockService.On("PublishExam", mock.Anything, examID).Return(nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodPost, "/exams/"+examID.String()+"/publish", nil)
	
	handler.PublishExam(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_PublishExam_NoQuestions(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	
	mockService.On("PublishExam", mock.Anything, examID).Return(services.ErrNoQuestions)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodPost, "/exams/"+examID.String()+"/publish", nil)
	
	handler.PublishExam(c)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
	mockService.AssertExpectations(t)
}

func TestExamHandler_GetExamDetail_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockExamService)
	handler := NewExamHandler(mockService)
	
	examID := uuid.New()
	exam := &models.Exam{
		ID:   examID,
		Name: "Test Exam",
	}
	
	questions := []models.Question{
		{ID: uuid.New(), Content: "Question 1"},
	}
	
	mockService.On("GetExamWithQuestions", mock.Anything, examID).Return(exam, questions, nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Params = gin.Params{{Key: "id", Value: examID.String()}}
	c.Request = httptest.NewRequest(http.MethodGet, "/exams/"+examID.String()+"/detail", nil)
	
	handler.GetExamDetail(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}
