package models

import (
	"time"

	"gorm.io/gorm"
)

type User struct {
	ID        uint           `gorm:"primaryKey" json:"id"`
	Username  string         `gorm:"uniqueIndex;size:50;not null" json:"username"`
	Password  string         `gorm:"size:255;not null" json:"-"`
	RealName  string         `gorm:"size:50" json:"real_name"`
	Role      string         `gorm:"size:20;not null;index" json:"role"`
	Email     string         `gorm:"size:100" json:"email"`
	Phone     string         `gorm:"size:20" json:"phone"`
	ClassID   *uint          `gorm:"index" json:"class_id"`
	ClassName string         `gorm:"size:50" json:"class_name,omitempty"`
	Status    int            `gorm:"default:1" json:"status"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

type UserListResponse struct {
	Total int     `json:"total"`
	List  []*User `json:"list"`
}

type UserFilter struct {
	Page     int    `form:"page" json:"page"`
	PageSize int    `form:"page_size" json:"page_size"`
	Username string `form:"username" json:"username"`
	RealName string `form:"real_name" json:"real_name"`
	Role     string `form:"role" json:"role"`
	Status   *int   `form:"status" json:"status"`
	ClassID  *uint  `form:"class_id" json:"class_id"`
}

func (f *UserFilter) GetOffset() int {
	if f.Page <= 0 {
		f.Page = 1
	}
	if f.PageSize <= 0 {
		f.PageSize = 10
	}
	return (f.Page - 1) * f.PageSize
}

func (f *UserFilter) GetLimit() int {
	if f.PageSize <= 0 {
		f.PageSize = 10
	}
	return f.PageSize
}
