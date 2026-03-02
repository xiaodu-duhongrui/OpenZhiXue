package models

import (
	"time"

	"golang.org/x/crypto/bcrypt"
	"gorm.io/gorm"
)

type Admin struct {
	ID        uint           `gorm:"primaryKey" json:"id"`
	Username  string         `gorm:"uniqueIndex;size:50;not null" json:"username"`
	Password  string         `gorm:"size:255;not null" json:"-"`
	RealName  string         `gorm:"size:50" json:"real_name"`
	Email     string         `gorm:"size:100" json:"email"`
	Phone     string         `gorm:"size:20" json:"phone"`
	Role      string         `gorm:"size:20;default:'admin'" json:"role"`
	Status    int            `gorm:"default:1" json:"status"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`
}

func (a *Admin) SetPassword(password string) error {
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return err
	}
	a.Password = string(hashedPassword)
	return nil
}

func (a *Admin) CheckPassword(password string) bool {
	err := bcrypt.CompareHashAndPassword([]byte(a.Password), []byte(password))
	return err == nil
}

func GetDefaultAdmin() *Admin {
	admin := &Admin{
		Username: "admin",
		RealName: "系统管理员",
		Email:    "admin@openzhixue.com",
		Role:     "super_admin",
		Status:   1,
	}
	admin.SetPassword("admin123")
	return admin
}
