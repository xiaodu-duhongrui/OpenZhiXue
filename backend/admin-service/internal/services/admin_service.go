package services

import (
	"errors"

	"admin-service/internal/models"
	"admin-service/internal/repositories"
	"admin-service/pkg/jwt"

	"gorm.io/gorm"
)

var (
	ErrAdminNotFound      = errors.New("admin not found")
	ErrInvalidCredentials = errors.New("invalid credentials")
	ErrAdminDisabled      = errors.New("admin account is disabled")
)

type AdminService struct {
	adminRepo  *repositories.AdminRepository
	jwtService *jwt.JWTService
}

func NewAdminService(adminRepo *repositories.AdminRepository, jwtService *jwt.JWTService) *AdminService {
	return &AdminService{
		adminRepo:  adminRepo,
		jwtService: jwtService,
	}
}

type LoginRequest struct {
	Username string `json:"username" binding:"required"`
	Password string `json:"password" binding:"required"`
}

type LoginResponse struct {
	Token     string      `json:"token"`
	ExpiresIn int64       `json:"expires_in"`
	Admin     *AdminInfo  `json:"admin"`
}

type AdminInfo struct {
	ID       uint   `json:"id"`
	Username string `json:"username"`
	RealName string `json:"real_name"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	Role     string `json:"role"`
}

func (s *AdminService) Login(req *LoginRequest) (*LoginResponse, error) {
	admin, err := s.adminRepo.FindByUsername(req.Username)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrInvalidCredentials
		}
		return nil, err
	}

	if !admin.CheckPassword(req.Password) {
		return nil, ErrInvalidCredentials
	}

	if admin.Status != 1 {
		return nil, ErrAdminDisabled
	}

	token, err := s.jwtService.GenerateToken(admin.ID, admin.Username, admin.Role)
	if err != nil {
		return nil, err
	}

	return &LoginResponse{
		Token:     token,
		ExpiresIn: 7200,
		Admin: &AdminInfo{
			ID:       admin.ID,
			Username: admin.Username,
			RealName: admin.RealName,
			Email:    admin.Email,
			Phone:    admin.Phone,
			Role:     admin.Role,
		},
	}, nil
}

func (s *AdminService) GetAdminByID(id uint) (*models.Admin, error) {
	admin, err := s.adminRepo.FindByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrAdminNotFound
		}
		return nil, err
	}
	return admin, nil
}

func (s *AdminService) GetAdminInfo(id uint) (*AdminInfo, error) {
	admin, err := s.GetAdminByID(id)
	if err != nil {
		return nil, err
	}
	return &AdminInfo{
		ID:       admin.ID,
		Username: admin.Username,
		RealName: admin.RealName,
		Email:    admin.Email,
		Phone:    admin.Phone,
		Role:     admin.Role,
	}, nil
}

func (s *AdminService) ChangePassword(id uint, oldPassword, newPassword string) error {
	admin, err := s.GetAdminByID(id)
	if err != nil {
		return err
	}

	if !admin.CheckPassword(oldPassword) {
		return ErrInvalidCredentials
	}

	return admin.SetPassword(newPassword)
}
