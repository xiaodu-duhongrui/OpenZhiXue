package main

import (
	"fmt"
	"log"

	"admin-service/internal/config"
	"admin-service/internal/database"
	"admin-service/internal/handlers"
	"admin-service/internal/middleware"
	"admin-service/internal/repositories"
	"admin-service/internal/services"
	"admin-service/pkg/jwt"

	"github.com/gin-gonic/gin"
)

func main() {
	cfg, err := config.Load("./config/config.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	if err := database.Init(&cfg.Database); err != nil {
		log.Fatalf("Failed to initialize database: %v", err)
	}

	db := database.GetDB()

	adminRepo := repositories.NewAdminRepository(db)
	userRepo := repositories.NewUserRepository(db)
	logRepo := repositories.NewLogRepository(db)

	jwtService := jwt.NewJWTService(
		cfg.JWT.Secret,
		cfg.JWT.Issuer,
		cfg.JWT.AccessTokenExpire,
	)

	adminService := services.NewAdminService(adminRepo, jwtService)
	userService := services.NewUserService(userRepo)
	importService := services.NewImportService(userRepo, logRepo, cfg.Import.UploadDir, cfg.Import.MaxFileSize)

	adminHandler := handlers.NewAdminHandler(adminService, jwtService)
	userHandler := handlers.NewUserHandler(userService, userRepo, logRepo)
	importHandler := handlers.NewImportHandler(importService, logRepo)
	logHandler := handlers.NewLogHandler(logRepo)

	gin.SetMode(cfg.Server.Mode)
	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())
	router.Use(middleware.CORS())

	api := router.Group("/api/admin")
	{
		api.POST("/login", adminHandler.Login)

		protected := api.Group("")
		protected.Use(middleware.AuthMiddleware(jwtService))
		{
			protected.GET("/profile", adminHandler.GetProfile)
			protected.PUT("/password", adminHandler.ChangePassword)

			users := protected.Group("/users")
			{
				users.GET("", userHandler.List)
				users.POST("", userHandler.Create)
				users.GET("/:id", userHandler.GetByID)
				users.PUT("/:id", userHandler.Update)
				users.DELETE("/:id", userHandler.Delete)
				users.PUT("/:id/password", userHandler.ChangePassword)
			}

			imports := protected.Group("/import")
			{
				imports.POST("/upload", importHandler.Upload)
				imports.POST("/preview", importHandler.Preview)
				imports.POST("/confirm", importHandler.Confirm)
				imports.GET("/template", importHandler.DownloadTemplate)
			}

			logs := protected.Group("/logs")
			{
				logs.GET("", logHandler.List)
				logs.GET("/:id", logHandler.GetByID)
			}
		}
	}

	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"service": "admin-service",
		})
	})

	addr := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
	log.Printf("Admin service starting on %s", addr)
	if err := router.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}
