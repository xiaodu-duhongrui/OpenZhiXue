package services

import (
	"errors"
	"testing"
	"time"

	"auth-service/internal/models"
	"auth-service/pkg/jwt"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"
)

type MockUserRepository struct {
	mock.Mock
}

func (m *MockUserRepository) Create(user *models.User) error {
	args := m.Called(user)
	return args.Error(0)
}

func (m *MockUserRepository) Update(user *models.User) error {
	args := m.Called(user)
	return args.Error(0)
}

func (m *MockUserRepository) FindByID(id uint) (*models.User, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) FindByUsername(username string) (*models.User, error) {
	args := m.Called(username)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.User), args.Error(1)
}

func (m *MockUserRepository) ExistsByUsername(username string) (bool, error) {
	args := m.Called(username)
	return args.Bool(0), args.Error(1)
}

func (m *MockUserRepository) ExistsByEmail(email string) (bool, error) {
	args := m.Called(email)
	return args.Bool(0), args.Error(1)
}

func (m *MockUserRepository) ExistsByPhone(phone string) (bool, error) {
	args := m.Called(phone)
	return args.Bool(0), args.Error(1)
}

func (m *MockUserRepository) UpdateLastLogin(id uint, ip string) error {
	args := m.Called(id, ip)
	return args.Error(0)
}

type MockRoleRepository struct {
	mock.Mock
}

func (m *MockRoleRepository) FindByCode(code string) (*models.Role, error) {
	args := m.Called(code)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Role), args.Error(1)
}

func (m *MockRoleRepository) FindByID(id uint) (*models.Role, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Role), args.Error(1)
}

type MockSessionRepository struct {
	mock.Mock
}

func (m *MockSessionRepository) Create(session *models.Session) error {
	args := m.Called(session)
	return args.Error(0)
}

func (m *MockSessionRepository) Update(session *models.Session) error {
	args := m.Called(session)
	return args.Error(0)
}

func (m *MockSessionRepository) DeleteByToken(token string) error {
	args := m.Called(token)
	return args.Error(0)
}

func (m *MockSessionRepository) FindByRefreshToken(token string) (*models.Session, error) {
	args := m.Called(token)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*models.Session), args.Error(1)
}

type MockJWTService struct {
	mock.Mock
}

func (m *MockJWTService) GenerateToken(userID uint, username string, roleID uint, roleCode string, permissions []string) (*jwt.TokenPair, error) {
	args := m.Called(userID, username, roleID, roleCode, permissions)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*jwt.TokenPair), args.Error(1)
}

func (m *MockJWTService) ValidateToken(tokenString string) (*jwt.Claims, error) {
	args := m.Called(tokenString)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*jwt.Claims), args.Error(1)
}

func (m *MockJWTService) RefreshTokenExpire() int {
	args := m.Called()
	return args.Int(0)
}

func TestAuthService_Register_Success(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	userRepo.On("ExistsByUsername", "testuser").Return(false, nil)
	userRepo.On("ExistsByEmail", "test@example.com").Return(false, nil)
	
	role := &models.Role{
		ID:   1,
		Code: "student",
	}
	roleRepo.On("FindByCode", "student").Return(role, nil)
	
	userRepo.On("Create", mock.AnythingOfType("*models.User")).Return(nil)
	
	req := &RegisterRequest{
		Username: "testuser",
		Password: "password123",
		Email:    "test@example.com",
		Phone:    "",
		RoleCode: "student",
	}
	
	user, err := service.Register(req)
	
	assert.NoError(t, err)
	assert.NotNil(t, user)
	assert.Equal(t, "testuser", user.Username)
	assert.Equal(t, "test@example.com", user.Email)
	
	userRepo.AssertExpectations(t)
	roleRepo.AssertExpectations(t)
}

func TestAuthService_Register_UsernameExists(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	userRepo.On("ExistsByUsername", "existinguser").Return(true, nil)
	
	req := &RegisterRequest{
		Username: "existinguser",
		Password: "password123",
		Email:    "test@example.com",
	}
	
	user, err := service.Register(req)
	
	assert.Error(t, err)
	assert.Nil(t, user)
	assert.Equal(t, "username already exists", err.Error())
	
	userRepo.AssertExpectations(t)
}

func TestAuthService_Register_EmailExists(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	userRepo.On("ExistsByUsername", "testuser").Return(false, nil)
	userRepo.On("ExistsByEmail", "existing@example.com").Return(true, nil)
	
	req := &RegisterRequest{
		Username: "testuser",
		Password: "password123",
		Email:    "existing@example.com",
	}
	
	user, err := service.Register(req)
	
	assert.Error(t, err)
	assert.Nil(t, user)
	assert.Equal(t, "email already exists", err.Error())
	
	userRepo.AssertExpectations(t)
}

func TestAuthService_Login_Success(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	hashedPassword, _ := hashPassword("password123")
	user := &models.User{
		ID:           1,
		Username:     "testuser",
		PasswordHash: hashedPassword,
		Email:        "test@example.com",
		Status:       models.UserStatusActive,
		Role: &models.Role{
			ID:          1,
			Code:        "student",
			Permissions: []models.Permission{},
		},
	}
	
	userRepo.On("FindByUsername", "testuser").Return(user, nil)
	
	tokenPair := &jwt.TokenPair{
		AccessToken:  "access-token",
		RefreshToken: "refresh-token",
	}
	jwtService.On("GenerateToken", uint(1), "testuser", uint(1), "student", []string{}).Return(tokenPair, nil)
	jwtService.On("RefreshTokenExpire").Return(86400)
	
	sessionRepo.On("Create", mock.AnythingOfType("*models.Session")).Return(nil)
	userRepo.On("UpdateLastLogin", uint(1), "127.0.0.1").Return(nil)
	
	req := &LoginRequest{
		Username: "testuser",
		Password: "password123",
	}
	
	resp, err := service.Login(req, "127.0.0.1", "test-agent")
	
	assert.NoError(t, err)
	assert.NotNil(t, resp)
	assert.Equal(t, tokenPair, resp.Token)
	assert.Equal(t, user, resp.User)
	
	userRepo.AssertExpectations(t)
	jwtService.AssertExpectations(t)
	sessionRepo.AssertExpectations(t)
}

func TestAuthService_Login_InvalidCredentials(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	hashedPassword, _ := hashPassword("correctpassword")
	user := &models.User{
		ID:           1,
		Username:     "testuser",
		PasswordHash: hashedPassword,
		Status:       models.UserStatusActive,
	}
	
	userRepo.On("FindByUsername", "testuser").Return(user, nil)
	
	req := &LoginRequest{
		Username: "testuser",
		Password: "wrongpassword",
	}
	
	resp, err := service.Login(req, "127.0.0.1", "test-agent")
	
	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Equal(t, "invalid credentials", err.Error())
	
	userRepo.AssertExpectations(t)
}

func TestAuthService_Login_UserNotFound(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	userRepo.On("FindByUsername", "nonexistent").Return(nil, errors.New("record not found"))
	
	req := &LoginRequest{
		Username: "nonexistent",
		Password: "password123",
	}
	
	resp, err := service.Login(req, "127.0.0.1", "test-agent")
	
	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Equal(t, "invalid credentials", err.Error())
	
	userRepo.AssertExpectations(t)
}

func TestAuthService_Login_InactiveUser(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	hashedPassword, _ := hashPassword("password123")
	user := &models.User{
		ID:           1,
		Username:     "testuser",
		PasswordHash: hashedPassword,
		Status:       models.UserStatusInactive,
	}
	
	userRepo.On("FindByUsername", "testuser").Return(user, nil)
	
	req := &LoginRequest{
		Username: "testuser",
		Password: "password123",
	}
	
	resp, err := service.Login(req, "127.0.0.1", "test-agent")
	
	assert.Error(t, err)
	assert.Nil(t, resp)
	assert.Equal(t, "user account is not active", err.Error())
	
	userRepo.AssertExpectations(t)
}

func TestAuthService_Logout(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	sessionRepo.On("DeleteByToken", "test-token").Return(nil)
	
	err := service.Logout("test-token")
	
	assert.NoError(t, err)
	sessionRepo.AssertExpectations(t)
}

func TestAuthService_GetProfile(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	user := &models.User{
		ID:       1,
		Username: "testuser",
		Email:    "test@example.com",
	}
	
	userRepo.On("FindByID", uint(1)).Return(user, nil)
	
	result, err := service.GetProfile(1)
	
	assert.NoError(t, err)
	assert.Equal(t, user, result)
	
	userRepo.AssertExpectations(t)
}

func TestAuthService_ChangePassword_Success(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	hashedPassword, _ := hashPassword("oldpassword")
	user := &models.User{
		ID:           1,
		PasswordHash: hashedPassword,
	}
	
	userRepo.On("FindByID", uint(1)).Return(user, nil)
	userRepo.On("Update", mock.AnythingOfType("*models.User")).Return(nil)
	
	err := service.ChangePassword(1, "oldpassword", "newpassword123")
	
	assert.NoError(t, err)
	
	userRepo.AssertExpectations(t)
}

func TestAuthService_ChangePassword_InvalidOldPassword(t *testing.T) {
	userRepo := new(MockUserRepository)
	roleRepo := new(MockRoleRepository)
	sessionRepo := new(MockSessionRepository)
	jwtService := new(MockJWTService)
	
	service := NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	
	hashedPassword, _ := hashPassword("correctpassword")
	user := &models.User{
		ID:           1,
		PasswordHash: hashedPassword,
	}
	
	userRepo.On("FindByID", uint(1)).Return(user, nil)
	
	err := service.ChangePassword(1, "wrongpassword", "newpassword123")
	
	assert.Error(t, err)
	assert.Equal(t, "invalid old password", err.Error())
	
	userRepo.AssertExpectations(t)
}

func hashPassword(password string) (string, error) {
	return "$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZRGdjGj/n3.iW8jY9D6aV3xV9xK2i", nil
}
