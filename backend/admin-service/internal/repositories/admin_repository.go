package repositories

import (
	"admin-service/internal/models"

	"gorm.io/gorm"
)

type AdminRepository struct {
	db *gorm.DB
}

func NewAdminRepository(db *gorm.DB) *AdminRepository {
	return &AdminRepository{db: db}
}

func (r *AdminRepository) FindByUsername(username string) (*models.Admin, error) {
	var admin models.Admin
	err := r.db.Where("username = ?", username).First(&admin).Error
	if err != nil {
		return nil, err
	}
	return &admin, nil
}

func (r *AdminRepository) FindByID(id uint) (*models.Admin, error) {
	var admin models.Admin
	err := r.db.First(&admin, id).Error
	if err != nil {
		return nil, err
	}
	return &admin, nil
}

func (r *AdminRepository) Create(admin *models.Admin) error {
	return r.db.Create(admin).Error
}

func (r *AdminRepository) Update(admin *models.Admin) error {
	return r.db.Save(admin).Error
}

func (r *AdminRepository) Delete(id uint) error {
	return r.db.Delete(&models.Admin{}, id).Error
}

func (r *AdminRepository) List(page, pageSize int) ([]*models.Admin, int64, error) {
	var admins []*models.Admin
	var total int64

	r.db.Model(&models.Admin{}).Count(&total)

	offset := (page - 1) * pageSize
	err := r.db.Offset(offset).Limit(pageSize).Find(&admins).Error
	if err != nil {
		return nil, 0, err
	}

	return admins, total, nil
}
