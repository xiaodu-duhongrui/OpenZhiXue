package repositories

import (
	"admin-service/internal/models"
	"time"

	"gorm.io/gorm"
)

type LogRepository struct {
	db *gorm.DB
}

func NewLogRepository(db *gorm.DB) *LogRepository {
	return &LogRepository{db: db}
}

func (r *LogRepository) Create(log *models.OperationLog) error {
	return r.db.Create(log).Error
}

func (r *LogRepository) FindByID(id uint) (*models.OperationLog, error) {
	var log models.OperationLog
	err := r.db.First(&log, id).Error
	if err != nil {
		return nil, err
	}
	return &log, nil
}

func (r *LogRepository) List(filter *models.OperationLogFilter) ([]*models.OperationLog, int64, error) {
	var logs []*models.OperationLog
	var total int64

	query := r.db.Model(&models.OperationLog{})

	if filter.AdminID != 0 {
		query = query.Where("admin_id = ?", filter.AdminID)
	}
	if filter.Action != "" {
		query = query.Where("action = ?", filter.Action)
	}
	if filter.Module != "" {
		query = query.Where("module = ?", filter.Module)
	}
	if filter.StartDate != "" {
		startTime, err := time.Parse("2006-01-02", filter.StartDate)
		if err == nil {
			query = query.Where("created_at >= ?", startTime)
		}
	}
	if filter.EndDate != "" {
		endTime, err := time.Parse("2006-01-02", filter.EndDate)
		if err == nil {
			query = query.Where("created_at <= ?", endTime.Add(24*time.Hour))
		}
	}

	query.Count(&total)

	offset := filter.GetOffset()
	limit := filter.GetLimit()
	err := query.Offset(offset).Limit(limit).Order("id DESC").Find(&logs).Error
	if err != nil {
		return nil, 0, err
	}

	return logs, total, nil
}

func (r *LogRepository) DeleteOlderThan(days int) error {
	cutoff := time.Now().AddDate(0, 0, -days)
	return r.db.Where("created_at < ?", cutoff).Delete(&models.OperationLog{}).Error
}
