package models

import (
	"time"

	"gorm.io/gorm"
)

type UserStatus int

const (
	UserStatusInactive UserStatus = 0
	UserStatusActive   UserStatus = 1
	UserStatusBanned   UserStatus = 2
)

type User struct {
	ID           uint           `gorm:"primaryKey" json:"id"`
	Username     string         `gorm:"uniqueIndex;size:50;not null" json:"username"`
	PasswordHash string         `gorm:"size:255;not null" json:"-"`
	Email        string         `gorm:"uniqueIndex;size:100" json:"email"`
	Phone        string         `gorm:"uniqueIndex;size:20" json:"phone"`
	RoleID       uint           `gorm:"not null;default:1" json:"role_id"`
	Role         *Role          `gorm:"foreignKey:RoleID" json:"role,omitempty"`
	Status       UserStatus     `gorm:"type:tinyint;not null;default:1" json:"status"`
	Avatar       string         `gorm:"size:255" json:"avatar"`
	Nickname     string         `gorm:"size:50" json:"nickname"`
	LastLoginAt  *time.Time     `json:"last_login_at"`
	LastLoginIP  string         `gorm:"size:45" json:"last_login_ip"`
	CreatedAt    time.Time      `json:"created_at"`
	UpdatedAt    time.Time      `json:"updated_at"`
	DeletedAt    gorm.DeletedAt `gorm:"index" json:"-"`
}

func (User) TableName() string {
	return "users"
}

type Role struct {
	ID          uint           `gorm:"primaryKey" json:"id"`
	Name        string         `gorm:"uniqueIndex;size:50;not null" json:"name"`
	Code        string         `gorm:"uniqueIndex;size:50;not null" json:"code"`
	Description string         `gorm:"size:255" json:"description"`
	Permissions []Permission   `gorm:"many2many:role_permissions;" json:"permissions"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"-"`
}

func (Role) TableName() string {
	return "roles"
}

type Permission struct {
	ID          uint           `gorm:"primaryKey" json:"id"`
	Name        string         `gorm:"uniqueIndex;size:100;not null" json:"name"`
	Code        string         `gorm:"uniqueIndex;size:100;not null" json:"code"`
	Description string         `gorm:"size:255" json:"description"`
	Resource    string         `gorm:"size:100;not null" json:"resource"`
	Action      string         `gorm:"size:50;not null" json:"action"`
	CreatedAt   time.Time      `json:"created_at"`
	UpdatedAt   time.Time      `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"-"`
}

func (Permission) TableName() string {
	return "permissions"
}

type Session struct {
	ID           uint       `gorm:"primaryKey" json:"id"`
	UserID       uint       `gorm:"not null;index" json:"user_id"`
	User         *User      `gorm:"foreignKey:UserID" json:"user,omitempty"`
	Token        string     `gorm:"uniqueIndex;size:500;not null" json:"token"`
	RefreshToken string     `gorm:"uniqueIndex;size:500" json:"refresh_token"`
	DeviceInfo   string     `gorm:"size:255" json:"device_info"`
	IPAddress    string     `gorm:"size:45" json:"ip_address"`
	UserAgent    string     `gorm:"size:500" json:"user_agent"`
	ExpiresAt    time.Time  `json:"expires_at"`
	CreatedAt    time.Time  `json:"created_at"`
}

func (Session) TableName() string {
	return "sessions"
}

type OAuthAccount struct {
	ID           uint      `gorm:"primaryKey" json:"id"`
	UserID       uint      `gorm:"not null;index" json:"user_id"`
	User         *User     `gorm:"foreignKey:UserID" json:"user,omitempty"`
	Provider     string    `gorm:"size:50;not null;index" json:"provider"`
	ProviderID   string    `gorm:"size:100;not null" json:"provider_id"`
	AccessToken  string    `gorm:"size:500" json:"access_token"`
	RefreshToken string    `gorm:"size:500" json:"refresh_token"`
	ExpiresAt    *time.Time `json:"expires_at"`
	CreatedAt    time.Time `json:"created_at"`
	UpdatedAt    time.Time `json:"updated_at"`
}

func (OAuthAccount) TableName() string {
	return "oauth_accounts"
}

func GetDefaultRoles() []Role {
	return []Role{
		{
			Name:        "学生",
			Code:        "student",
			Description: "学生用户角色",
		},
		{
			Name:        "家长",
			Code:        "parent",
			Description: "家长用户角色",
		},
		{
			Name:        "教师",
			Code:        "teacher",
			Description: "教师用户角色",
		},
		{
			Name:        "管理员",
			Code:        "admin",
			Description: "系统管理员角色",
		},
	}
}

func GetDefaultPermissions() []Permission {
	return []Permission{
		{Name: "查看个人信息", Code: "user:read", Resource: "user", Action: "read"},
		{Name: "编辑个人信息", Code: "user:update", Resource: "user", Action: "update"},
		{Name: "查看成绩", Code: "score:read", Resource: "score", Action: "read"},
		{Name: "管理成绩", Code: "score:manage", Resource: "score", Action: "manage"},
		{Name: "查看作业", Code: "homework:read", Resource: "homework", Action: "read"},
		{Name: "管理作业", Code: "homework:manage", Resource: "homework", Action: "manage"},
		{Name: "查看班级", Code: "class:read", Resource: "class", Action: "read"},
		{Name: "管理班级", Code: "class:manage", Resource: "class", Action: "manage"},
		{Name: "用户管理", Code: "user:manage", Resource: "user", Action: "manage"},
		{Name: "系统管理", Code: "system:manage", Resource: "system", Action: "manage"},
	}
}

func GetRolePermissions() map[string][]string {
	return map[string][]string{
		"student": {"user:read", "user:update", "score:read", "homework:read", "class:read"},
		"parent":  {"user:read", "user:update", "score:read", "homework:read", "class:read"},
		"teacher": {"user:read", "user:update", "score:read", "score:manage", "homework:read", "homework:manage", "class:read", "class:manage"},
		"admin":   {"user:read", "user:update", "user:manage", "score:read", "score:manage", "homework:read", "homework:manage", "class:read", "class:manage", "system:manage"},
	}
}
