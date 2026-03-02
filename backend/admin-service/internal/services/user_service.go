package services

import (
	"errors"

	"admin-service/internal/models"
	"admin-service/internal/repositories"

	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

var (
	ErrUserNotFound      = errors.New("user not found")
	ErrUserExists        = errors.New("username already exists")
	ErrInvalidRole       = errors.New("invalid role")
)

type UserService struct {
	userRepo *repositories.UserRepository
}

func NewUserService(userRepo *repositories.UserRepository) *UserService {
	return &UserService{
		userRepo: userRepo,
	}
}

type CreateUserRequest struct {
	Username string `json:"username" binding:"required,min=3,max=50"`
	Password string `json:"password" binding:"required,min=6"`
	RealName string `json:"real_name" binding:"required"`
	Role     string `json:"role" binding:"required"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	ClassID  *uint  `json:"class_id"`
}

type UpdateUserRequest struct {
	RealName string `json:"real_name"`
	Email    string `json:"email"`
	Phone    string `json:"phone"`
	ClassID  *uint  `json:"class_id"`
	Status   *int   `json:"status"`
}

type ChangePasswordRequest struct {
	NewPassword string `json:"new_password" binding:"required,min=6"`
}

var validRoles = map[string]bool{
	"student": true,
	"teacher": true,
	"admin":   true,
}

func (s *UserService) Create(req *CreateUserRequest) (*models.User, error) {
	if !validRoles[req.Role] {
		return nil, ErrInvalidRole
	}

	exists, err := s.userRepo.ExistsByUsername(req.Username)
	if err != nil {
		return nil, err
	}
	if exists {
		return nil, ErrUserExists
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	user := &models.User{
		Username: req.Username,
		Password: string(hashedPassword),
		RealName: req.RealName,
		Role:     req.Role,
		Email:    req.Email,
		Phone:    req.Phone,
		ClassID:  req.ClassID,
		Status:   1,
	}

	if err := s.userRepo.Create(user); err != nil {
		return nil, err
	}

	return user, nil
}

func (s *UserService) Update(id uint, req *UpdateUserRequest) (*models.User, error) {
	user, err := s.userRepo.FindByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}

	if req.RealName != "" {
		user.RealName = req.RealName
	}
	if req.Email != "" {
		user.Email = req.Email
	}
	if req.Phone != "" {
		user.Phone = req.Phone
	}
	if req.ClassID != nil {
		user.ClassID = req.ClassID
	}
	if req.Status != nil {
		user.Status = *req.Status
	}

	if err := s.userRepo.Update(user); err != nil {
		return nil, err
	}

	return user, nil
}

func (s *UserService) Delete(id uint) error {
	_, err := s.userRepo.FindByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return ErrUserNotFound
		}
		return err
	}

	return s.userRepo.Delete(id)
}

func (s *UserService) GetByID(id uint) (*models.User, error) {
	user, err := s.userRepo.FindByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, ErrUserNotFound
		}
		return nil, err
	}
	return user, nil
}

func (s *UserService) List(filter *models.UserFilter) (*models.UserListResponse, error) {
	users, total, err := s.userRepo.List(filter)
	if err != nil {
		return nil, err
	}

	return &models.UserListResponse{
		Total: int(total),
		List:  users,
	}, nil
}

func (s *UserService) ChangePassword(id uint, newPassword string) error {
	user, err := s.userRepo.FindByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return ErrUserNotFound
		}
		return err
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(newPassword), bcrypt.DefaultCost)
	if err != nil {
		return err
	}

	user.Password = string(hashedPassword)
	return s.userRepo.Update(user)
}

func (s *UserService) CreateBatch(users []*models.User) error {
	for _, user := range users {
		hashedPassword, err := bcrypt.GenerateFromPassword([]byte(user.Password), bcrypt.DefaultCost)
		if err != nil {
			return err
		}
		user.Password = string(hashedPassword)
		user.Status = 1
	}
	return s.userRepo.CreateBatch(users)
}
