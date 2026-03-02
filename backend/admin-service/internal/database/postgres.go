package database

import (
	"fmt"
	"log"

	"admin-service/internal/config"
	"admin-service/internal/models"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

var DB *gorm.DB

func Init(cfg *config.DatabaseConfig) error {
	dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=%s",
		cfg.Host,
		cfg.Username,
		cfg.Password,
		cfg.DBName,
		cfg.Port,
		cfg.SSLMode,
	)

	var err error
	DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
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
		&models.Admin{},
		&models.User{},
		&models.OperationLog{},
	)
}

func initDefaultData() error {
	var count int64
	DB.Model(&models.Admin{}).Count(&count)
	if count > 0 {
		return nil
	}

	defaultAdmin := models.GetDefaultAdmin()
	if err := DB.Create(&defaultAdmin).Error; err != nil {
		return err
	}

	log.Println("Default admin initialized successfully")
	return nil
}

func GetDB() *gorm.DB {
	return DB
}
