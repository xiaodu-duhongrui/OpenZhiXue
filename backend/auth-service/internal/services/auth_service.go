package services

import (
	"errors"
	"time"

	"auth-service/internal/models"
	"auth-service/internal/repositories"
	"auth-service/pkg/crypto"
	"auth-service/pkg/jwt"

	"gorm.io/gorm"
)

type AuthService struct {
	userRepo    *repositories.UserRepository
	roleRepo    *repositories.RoleRepository
	sessionRepo *repositories.SessionRepository
	jwtService  *jwt.JWTService
}

func NewAuthService(
	userRepo *repositories.UserRepository,
	roleRepo *repositories.RoleRepository,
	sessionRepo *repositories.SessionRepository,
	jwtService *jwt.JWTService,
) *AuthService {
	return &AuthService{
		userRepo:    userRepo,
		roleRepo:    roleRepo,
		sessionRepo: sessionRepo,
		jwtService:  jwtService,
	}
}

type RegisterRequest struct {
	Username string `json:"username" binding:"required,min=3,max=50"`
	Password string `json:"password" binding:"required,min=6,max=100"`
	Email    string `json:"email" binding:"required,email"`
	Phone    string `json:"phone"`
	RoleCode string `json:"role_code"`
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginResponse struct {
	Token *jwt.TokenPair `json:"token"`
	User  *models.User   `json:"user"`
}

type UpdateProfileRequest struct {
	Email    string `json:"email" binding:"omitempty,email"`
	Phone    string `json:"phone"`
	Nickname string `json:"nickname" binding:"omitempty,max=50"`
	Avatar   string `json:"avatar" binding:"omitempty,url"`
}

func (s *AuthService) Register(req *RegisterRequest) (*models.User, error) {
	exists, err := s.userRepo.ExistsByUsername(req.Username)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, errors.New("username already exists")
	}

	exists, err = s.userRepo.ExistsByEmail(req.Email)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, errors.New("email already exists")
	}

	if req.Phone != "" {
		exists, err = s.userRepo.ExistsByPhone(req.Phone)
		if err != nil {
			return nil, err
		}
		if exists {
			return nil, errors.New("phone already exists")
		}
	}

	roleCode := req.RoleCode
	if roleCode == "" {
		roleCode = "student"
	}

	role, err := s.roleRepo.FindByCode(roleCode)
	if err != nil {
		return nil, errors.New("invalid role")
	}

	passwordHash, err := crypto.HashPassword(req.Password)
	if err != nil {
		return nil, err
	}

	user := &models.User{
		Username:     req.Username,
		PasswordHash: passwordHash,
		Email:        req.Email,
		Phone:        req.Phone,
		RoleID:       role.ID,
		Status:       models.UserStatusActive,
	}

	if err := s.userRepo.Create(user); err != nil {
		return nil, err
	}

	user.Role = role
	return user, nil
}

func (s *AuthService) Login(req *LoginRequest, ip, userAgent string) (*LoginResponse, error) {
	user, err := s.userRepo.FindByUsername(req.Username)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("invalid credentials")
		}
		return nil, err
	}

	if !crypto.CheckPassword(req.Password, user.PasswordHash) {
		return nil, errors.New("invalid credentials")
	}

	if user.Status != models.UserStatusActive {
		return nil, errors.New("user account is not active")
	}

	var permissions []string
	if user.Role != nil {
		for _, perm := range user.Role.Permissions {
			permissions = append(permissions, perm.Code)
		}
	}

	tokenPair, err := s.jwtService.GenerateToken(user.ID, user.Username, user.RoleID, user.Role.Code, permissions)
	if err != nil {
		return nil, err
	}

	expiresAt := time.Now().Add(time.Duration(s.jwtService.RefreshTokenExpire()) * time.Second)
	session := &models.Session{
		UserID:       user.ID,
		Token:        tokenPair.AccessToken,
		RefreshToken: tokenPair.RefreshToken,
		IPAddress:    ip,
		UserAgent:    userAgent,
		ExpiresAt:    expiresAt,
	}

	if err := s.sessionRepo.Create(session); err != nil {
		return nil, err
	}

	if err := s.userRepo.UpdateLastLogin(user.ID, ip); err != nil {
		return nil, err
	}

	return &LoginResponse{
		Token: tokenPair,
		User:  user,
	}, nil
}

func (s *AuthService) Logout(token string) error {
	return s.sessionRepo.DeleteByToken(token)
}

func (s *AuthService) RefreshToken(refreshToken string) (*jwt.TokenPair, error) {
	session, err := s.sessionRepo.FindByRefreshToken(refreshToken)
	if err != nil {
		return nil, errors.New("invalid refresh token")
	}

	if session.ExpiresAt.Before(time.Now()) {
		return nil, errors.New("refresh token expired")
	}

	user := session.User
	var permissions []string
	if user.Role != nil {
		for _, perm := range user.Role.Permissions {
			permissions = append(permissions, perm.Code)
		}
	}

	tokenPair, err := s.jwtService.GenerateToken(user.ID, user.Username, user.RoleID, user.Role.Code, permissions)
	if err != nil {
		return nil, err
	}

	session.Token = tokenPair.AccessToken
	session.RefreshToken = tokenPair.RefreshToken
	session.ExpiresAt = time.Now().Add(time.Duration(s.jwtService.RefreshTokenExpire()) * time.Second)

	if err := s.sessionRepo.Update(session); err != nil {
		return nil, err
	}

	return tokenPair, nil
}

func (s *AuthService) GetProfile(userID uint) (*models.User, error) {
	return s.userRepo.FindByID(userID)
}

func (s *AuthService) UpdateProfile(userID uint, req *UpdateProfileRequest) (*models.User, error) {
	user, err := s.userRepo.FindByID(userID)
	if err != nil {
		return nil, err
	}

	if req.Email != "" && req.Email != user.Email {
		exists, err := s.userRepo.ExistsByEmail(req.Email)
		if err != nil {
			return nil, err
		}
		if exists {
			return nil, errors.New("email already exists")
		}
		user.Email = req.Email
	}

	if req.Phone != "" && req.Phone != user.Phone {
		exists, err := s.userRepo.ExistsByPhone(req.Phone)
		if err != nil {
			return nil, err
		}
		if exists {
			return nil, errors.New("phone already exists")
		}
		user.Phone = req.Phone
	}

	if req.Nickname != "" {
		user.Nickname = req.Nickname
	}

	if req.Avatar != "" {
		user.Avatar = req.Avatar
	}

	if err := s.userRepo.Update(user); err != nil {
		return nil, err
	}

	return user, nil
}

func (s *AuthService) ChangePassword(userID uint, oldPassword, newPassword string) error {
	user, err := s.userRepo.FindByID(userID)
	if err != nil {
		return err
	}

	if !crypto.CheckPassword(oldPassword, user.PasswordHash) {
		return errors.New("invalid old password")
	}

	passwordHash, err := crypto.HashPassword(newPassword)
	if err != nil {
		return err
	}

	user.PasswordHash = passwordHash
	return s.userRepo.Update(user)
}

func (s *AuthService) ValidateToken(tokenString string) (*jwt.Claims, error) {
	return s.jwtService.ValidateToken(tokenString)
}
