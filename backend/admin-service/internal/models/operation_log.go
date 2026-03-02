package models

import (
	"time"
)

type OperationLog struct {
	ID         uint      `gorm:"primaryKey" json:"id"`
	AdminID    uint      `gorm:"not null;index" json:"admin_id"`
	AdminName  string    `gorm:"size:50" json:"admin_name"`
	Action     string    `gorm:"size:50;not null;index" json:"action"`
	Module     string    `gorm:"size:50" json:"module"`
	TargetType string    `gorm:"size:50" json:"target_type"`
	TargetID   uint      `json:"target_id"`
	Detail     string    `gorm:"type:text" json:"detail"`
	IP         string    `gorm:"size:50" json:"ip"`
	UserAgent  string    `gorm:"size:255" json:"user_agent"`
	CreatedAt  time.Time `json:"created_at"`
}

type OperationLogFilter struct {
	Page     int    `form:"page" json:"page"`
	PageSize int    `form:"page_size" json:"page_size"`
	AdminID  uint   `form:"admin_id" json:"admin_id"`
	Action   string `form:"action" json:"action"`
	Module   string `form:"module" json:"module"`
	StartDate string `form:"start_date" json:"start_date"`
	EndDate   string `form:"end_date" json:"end_date"`
}

func (f *OperationLogFilter) GetOffset() int {
	if f.Page <= 0 {
		f.Page = 1
	}
	if f.PageSize <= 0 {
		f.PageSize = 10
	}
	return (f.Page - 1) * f.PageSize
}

func (f *OperationLogFilter) GetLimit() int {
	if f.PageSize <= 0 {
		f.PageSize = 10
	}
	return f.PageSize
}

type OperationLogListResponse struct {
	Total int              `json:"total"`
	List  []*OperationLog `json:"list"`
}
