package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"auth-service/internal/services"
	"auth-service/pkg/jwt"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockAuthService struct {
	mock.Mock
}

func (m *MockAuthService) Register(req *services.RegisterRequest) (*services.LoginResponse, error) {
	args := m.Called(req)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*services.LoginResponse), args.Error(1)
}

func (m *MockAuthService) Login(req *services.LoginRequest, ip, userAgent string) (*services.LoginResponse, error) {
	args := m.Called(req, ip, userAgent)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*services.LoginResponse), args.Error(1)
}

func (m *MockAuthService) Logout(token string) error {
	args := m.Called(token)
	return args.Error(0)
}

func (m *MockAuthService) RefreshToken(refreshToken string) (*jwt.TokenPair, error) {
	args := m.Called(refreshToken)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*jwt.TokenPair), args.Error(1)
}

func (m *MockAuthService) GetProfile(userID uint) (interface{}, error) {
	args := m.Called(userID)
	return args.Get(0), args.Error(1)
}

func (m *MockAuthService) UpdateProfile(userID uint, req *services.UpdateProfileRequest) (interface{}, error) {
	args := m.Called(userID, req)
	return args.Get(0), args.Error(1)
}

func (m *MockAuthService) ChangePassword(userID uint, oldPassword, newPassword string) error {
	args := m.Called(userID, oldPassword, newPassword)
	return args.Error(0)
}

func TestAuthHandler_Register_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	reqBody := services.RegisterRequest{
		Username: "testuser",
		Password: "password123",
		Email:    "test@example.com",
	}
	
	body, _ := json.Marshal(reqBody)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/register", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	
	handler.Register(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestAuthHandler_Register_InvalidRequest(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/register", bytes.NewBuffer([]byte("{}")))
	c.Request.Header.Set("Content-Type", "application/json")
	
	handler.Register(c)
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
}

func TestAuthHandler_Login_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	reqBody := services.LoginRequest{
		Username: "testuser",
		Password: "password123",
	}
	
	body, _ := json.Marshal(reqBody)
	
	mockService.On("Login", &reqBody, "192.168.1.1", "test-agent").Return(&services.LoginResponse{}, nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/login", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Request.Header.Set("User-Agent", "test-agent")
	
	handler.Login(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestAuthHandler_Login_InvalidCredentials(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	reqBody := services.LoginRequest{
		Username: "testuser",
		Password: "wrongpassword",
	}
	
	body, _ := json.Marshal(reqBody)
	
	mockService.On("Login", &reqBody, mock.Anything, mock.Anything).Return(nil, assert.AnError)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/login", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	
	handler.Login(c)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
	mockService.AssertExpectations(t)
}

func TestAuthHandler_Logout_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	mockService.On("Logout", "test-token").Return(nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/logout", nil)
	c.Request.Header.Set("Authorization", "Bearer test-token")
	
	handler.Logout(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestAuthHandler_Logout_MissingAuthHeader(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/logout", nil)
	
	handler.Logout(c)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestAuthHandler_RefreshToken_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	tokenPair := &jwt.TokenPair{
		AccessToken:  "new-access-token",
		RefreshToken: "new-refresh-token",
	}
	
	mockService.On("RefreshToken", "refresh-token").Return(tokenPair, nil)
	
	reqBody := map[string]string{"refresh_token": "refresh-token"}
	body, _ := json.Marshal(reqBody)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/refresh", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	
	handler.RefreshToken(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestAuthHandler_GetProfile_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	mockService.On("GetProfile", uint(1)).Return(map[string]interface{}{"id": 1}, nil)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodGet, "/profile", nil)
	c.Set("user_id", uint(1))
	
	handler.GetProfile(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestAuthHandler_GetProfile_Unauthorized(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodGet, "/profile", nil)
	
	handler.GetProfile(c)
	
	assert.Equal(t, http.StatusUnauthorized, w.Code)
}

func TestAuthHandler_ChangePassword_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockService := new(MockAuthService)
	mockJWT := &jwt.JWTService{}
	handler := NewAuthHandler(mockService, mockJWT)
	
	mockService.On("ChangePassword", uint(1), "oldpass", "newpass123").Return(nil)
	
	reqBody := map[string]string{
		"old_password": "oldpass",
		"new_password": "newpass123",
	}
	body, _ := json.Marshal(reqBody)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodPost, "/change-password", bytes.NewBuffer(body))
	c.Request.Header.Set("Content-Type", "application/json")
	c.Set("user_id", uint(1))
	
	handler.ChangePassword(c)
	
	assert.Equal(t, http.StatusOK, w.Code)
	mockService.AssertExpectations(t)
}

func TestSuccess(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	Success(c, map[string]string{"message": "test"})
	
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestError(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	
	Error(c, http.StatusBadRequest, "test error")
	
	assert.Equal(t, http.StatusBadRequest, w.Code)
}
