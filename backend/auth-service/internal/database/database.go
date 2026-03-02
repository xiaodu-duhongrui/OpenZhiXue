package database

import (
	"fmt"
	"log"

	"auth-service/internal/config"
	"auth-service/internal/models"

	"gorm.io/driver/mysql"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

func Init(cfg *config.DatabaseConfig) error {
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?charset=%s&parseTime=True&loc=Local",
		cfg.Username,
		cfg.Password,
		cfg.Host,
		cfg.Port,
		cfg.DBName,
		cfg.Charset,
	)

	var err error
	DB, err = gorm.Open(mysql.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		return fmt.Errorf("failed to connect database: %w", err)
	}

	sqlDB, err := DB.DB()
	if err != nil {
		return fmt.Errorf("failed to get sql.DB: %w", err)
	}

	sqlDB.SetMaxIdleConns(cfg.MaxIdleConns)
	sqlDB.SetMaxOpenConns(cfg.MaxOpenConns)

	if err = autoMigrate(); err != nil {
		return fmt.Errorf("failed to migrate: %w", err)
	}

	if err = initDefaultData(); err != nil {
		return fmt.Errorf("failed to init default data: %w", err)
	}

	log.Println("Database connected successfully")
	return nil
}

func autoMigrate() error {
	return DB.AutoMigrate(
		&models.User{},
		&models.Role{},
		&models.Permission{},
		&models.Session{},
		&models.OAuthAccount{},
	)
}

func initDefaultData() error {
	var count int64
	DB.Model(&models.Role{}).Count(&count)
	if count > 0 {
		return nil
	}

	permissions := models.GetDefaultPermissions()
	if err := DB.Create(&permissions).Error; err != nil {
		return err
	}

	roles := models.GetDefaultRoles()
	if err := DB.Create(&roles).Error; err != nil {
		return err
	}

	rolePerms := models.GetRolePermissions()
	for i, role := range roles {
		var rolePermsList []models.Permission
		for _, permCode := range rolePerms[role.Code] {
			for _, perm := range permissions {
				if perm.Code == permCode {
					rolePermsList = append(rolePermsList, perm)
				}
			}
		}
		if err := DB.Model(&roles[i]).Association("Permissions").Append(rolePermsList); err != nil {
			return err
		}
	}

	log.Println("Default data initialized successfully")
	return nil
}

func GetDB() *gorm.DB {
	return DB
}
