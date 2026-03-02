package repositories

import (
	"admin-service/internal/models"

	"gorm.io/gorm"
)

type UserRepository struct {
	db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) Create(user *models.User) error {
	return r.db.Create(user).Error
}

func (r *UserRepository) Update(user *models.User) error {
	return r.db.Save(user).Error
}

func (r *UserRepository) Delete(id uint) error {
	return r.db.Delete(&models.User{}, id).Error
}

func (r *UserRepository) FindByID(id uint) (*models.User, error) {
	var user models.User
	err := r.db.First(&user, id).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) FindByUsername(username string) (*models.User, error) {
	var user models.User
	err := r.db.Where("username = ?", username).First(&user).Error
	if err != nil {
		return nil, err
	}
	return &user, nil
}

func (r *UserRepository) List(filter *models.UserFilter) ([]*models.User, int64, error) {
	var users []*models.User
	var total int64

	query := r.db.Model(&models.User{})

	if filter.Username != "" {
		query = query.Where("username LIKE ?", "%"+filter.Username+"%")
	}
	if filter.RealName != "" {
		query = query.Where("real_name LIKE ?", "%"+filter.RealName+"%")
	}
	if filter.Role != "" {
		query = query.Where("role = ?", filter.Role)
	}
	if filter.Status != nil {
		query = query.Where("status = ?", *filter.Status)
	}
	if filter.ClassID != nil {
		query = query.Where("class_id = ?", *filter.ClassID)
	}

	query.Count(&total)

	offset := filter.GetOffset()
	limit := filter.GetLimit()
	err := query.Offset(offset).Limit(limit).Order("id DESC").Find(&users).Error
	if err != nil {
		return nil, 0, err
	}

	return users, total, nil
}

func (r *UserRepository) ExistsByUsername(username string) (bool, error) {
	var count int64
	err := r.db.Model(&models.User{}).Where("username = ?", username).Count(&count).Error
	if err != nil {
		return false, err
	}
	return count > 0, nil
}

func (r *UserRepository) CreateBatch(users []*models.User) error {
	if len(users) == 0 {
		return nil
	}
	return r.db.Create(&users).Error
}

func (r *UserRepository) FindByUsernames(usernames []string) ([]*models.User, error) {
	var users []*models.User
	err := r.db.Where("username IN ?", usernames).Find(&users).Error
	if err != nil {
		return nil, err
	}
	return users, nil
}
