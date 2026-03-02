package services

import (
	"auth-service/internal/models"
	"auth-service/internal/repositories"
)

type RBACService struct {
	roleRepo       *repositories.RoleRepository
	permissionRepo *repositories.PermissionRepository
}

func NewRBACService(
	roleRepo *repositories.RoleRepository,
	permissionRepo *repositories.PermissionRepository,
) *RBACService {
	return &RBACService{
		roleRepo:       roleRepo,
		permissionRepo: permissionRepo,
	}
}

func (s *RBACService) GetAllRoles() ([]models.Role, error) {
	return s.roleRepo.FindAll()
}

func (s *RBACService) GetRoleByID(id uint) (*models.Role, error) {
	return s.roleRepo.FindByID(id)
}

func (s *RBACService) GetRoleByCode(code string) (*models.Role, error) {
	return s.roleRepo.FindByCode(code)
}

func (s *RBACService) CreateRole(role *models.Role) error {
	return s.roleRepo.Create(role)
}

func (s *RBACService) UpdateRole(role *models.Role) error {
	return s.roleRepo.Update(role)
}

func (s *RBACService) DeleteRole(id uint) error {
	return s.roleRepo.Delete(id)
}

func (s *RBACService) AssignPermissions(roleID uint, permissionIDs []uint) error {
	return s.roleRepo.AssignPermissions(roleID, permissionIDs)
}

func (s *RBACService) GetAllPermissions() ([]models.Permission, error) {
	return s.permissionRepo.FindAll()
}

func (s *RBACService) GetPermissionsByRoleID(roleID uint) ([]models.Permission, error) {
	return s.roleRepo.GetPermissionsByRoleID(roleID)
}

func (s *RBACService) HasPermission(roleID uint, permissionCode string) (bool, error) {
	permissions, err := s.roleRepo.GetPermissionsByRoleID(roleID)
	if err != nil {
		return false, err
	}

	for _, perm := range permissions {
		if perm.Code == permissionCode {
			return true, nil
		}
	}

	return false, nil
}

func (s *RBACService) HasAnyPermission(roleID uint, permissionCodes []string) (bool, error) {
	permissions, err := s.roleRepo.GetPermissionsByRoleID(roleID)
	if err != nil {
		return false, err
	}

	permissionMap := make(map[string]bool)
	for _, perm := range permissions {
		permissionMap[perm.Code] = true
	}

	for _, code := range permissionCodes {
		if permissionMap[code] {
			return true, nil
		}
	}

	return false, nil
}

func (s *RBACService) HasAllPermissions(roleID uint, permissionCodes []string) (bool, error) {
	permissions, err := s.roleRepo.GetPermissionsByRoleID(roleID)
	if err != nil {
		return false, err
	}

	permissionMap := make(map[string]bool)
	for _, perm := range permissions {
		permissionMap[perm.Code] = true
	}

	for _, code := range permissionCodes {
		if !permissionMap[code] {
			return false, nil
		}
	}

	return true, nil
}
