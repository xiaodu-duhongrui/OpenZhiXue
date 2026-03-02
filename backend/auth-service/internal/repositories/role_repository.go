package repositories

import (
	"auth-service/internal/database"
	"auth-service/internal/models"

	"gorm.io/gorm"
)

type RoleRepository struct {
	db *gorm.DB
}

func NewRoleRepository() *RoleRepository {
	return &RoleRepository{db: database.GetDB()}
}

func (r *RoleRepository) Create(role *models.Role) error {
	return r.db.Create(role).Error
}

func (r *RoleRepository) Update(role *models.Role) error {
	return r.db.Save(role).Error
}

func (r *RoleRepository) Delete(id uint) error {
	return r.db.Delete(&models.Role{}, id).Error
}

func (r *RoleRepository) FindByID(id uint) (*models.Role, error) {
	var role models.Role
	err := r.db.Preload("Permissions").First(&role, id).Error
	if err != nil {
		return nil, err
	}
	return &role, nil
}

func (r *RoleRepository) FindByCode(code string) (*models.Role, error) {
	var role models.Role
	err := r.db.Preload("Permissions").Where("code = ?", code).First(&role).Error
	if err != nil {
		return nil, err
	}
	return &role, nil
}

func (r *RoleRepository) FindAll() ([]models.Role, error) {
	var roles []models.Role
	err := r.db.Preload("Permissions").Find(&roles).Error
	return roles, err
}

func (r *RoleRepository) AssignPermissions(roleID uint, permissionIDs []uint) error {
	var permissions []models.Permission
	if err := r.db.Find(&permissions, permissionIDs).Error; err != nil {
		return err
	}

	return r.db.Model(&models.Role{ID: roleID}).Association("Permissions").Replace(permissions)
}

func (r *RoleRepository) GetPermissionsByRoleID(roleID uint) ([]models.Permission, error) {
	var role models.Role
	err := r.db.Preload("Permissions").First(&role, roleID).Error
	if err != nil {
		return nil, err
	}
	return role.Permissions, nil
}

type PermissionRepository struct {
	db *gorm.DB
}

func NewPermissionRepository() *PermissionRepository {
	return &PermissionRepository{db: database.GetDB()}
}

func (r *PermissionRepository) FindAll() ([]models.Permission, error) {
	var permissions []models.Permission
	err := r.db.Find(&permissions).Error
	return permissions, err
}

func (r *PermissionRepository) FindByCode(code string) (*models.Permission, error) {
	var permission models.Permission
	err := r.db.Where("code = ?", code).First(&permission).Error
	if err != nil {
		return nil, err
	}
	return &permission, nil
}

func (r *PermissionRepository) FindByCodes(codes []string) ([]models.Permission, error) {
	var permissions []models.Permission
	err := r.db.Where("code IN ?", codes).Find(&permissions).Error
	return permissions, err
}
