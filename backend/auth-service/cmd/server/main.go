package main

import (
	"fmt"
	"log"

	"auth-service/internal/config"
	"auth-service/internal/database"
	"auth-service/internal/handlers"
	"auth-service/internal/middleware"
	"auth-service/internal/repositories"
	"auth-service/internal/services"
	"auth-service/pkg/jwt"
	"auth-service/pkg/oauth"

	"github.com/gin-gonic/gin"
)

func main() {
	cfg, err := config.Load("config/config.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	if err := database.Init(&cfg.Database); err != nil {
		log.Fatalf("Failed to init database: %v", err)
	}

	jwtService := jwt.NewJWTService(
		cfg.JWT.Secret,
		cfg.JWT.Issuer,
		cfg.JWT.AccessTokenExpire,
		cfg.JWT.RefreshTokenExpire,
	)

	userRepo := repositories.NewUserRepository()
	roleRepo := repositories.NewRoleRepository()
	sessionRepo := repositories.NewSessionRepository()
	permissionRepo := repositories.NewPermissionRepository()
	oauthAccountRepo := repositories.NewOAuthAccountRepository()

	authService := services.NewAuthService(userRepo, roleRepo, sessionRepo, jwtService)
	rbacService := services.NewRBACService(roleRepo, permissionRepo)

	oauthService := oauth.NewOAuthService(
		cfg.OAuth.WeChat.AppID,
		cfg.OAuth.WeChat.AppSecret,
		cfg.OAuth.WeChat.RedirectURL,
		cfg.OAuth.QQ.AppID,
		cfg.OAuth.QQ.AppKey,
		cfg.OAuth.QQ.RedirectURL,
	)

	ssoService := services.NewSSOService(userRepo, roleRepo, sessionRepo, oauthAccountRepo, jwtService, oauthService)

	authHandler := handlers.NewAuthHandler(authService, jwtService)
	rbacHandler := handlers.NewRBACHandler(rbacService)
	ssoHandler := handlers.NewSSOHandler(ssoService)

	gin.SetMode(cfg.Server.Mode)
	router := gin.Default()

	router.Use(CORS())

	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	setupRoutes(router, jwtService, authHandler, rbacHandler, ssoHandler)

	addr := fmt.Sprintf("%s:%d", cfg.Server.Host, cfg.Server.Port)
	log.Printf("Server starting on %s", addr)
	if err := router.Run(addr); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}

func setupRoutes(
	router *gin.Engine,
	jwtService *jwt.JWTService,
	authHandler *handlers.AuthHandler,
	rbacHandler *handlers.RBACHandler,
	ssoHandler *handlers.SSOHandler,
) {
	api := router.Group("/api/v1")
	{
		auth := api.Group("/auth")
		{
			auth.POST("/register", authHandler.Register)
			auth.POST("/login", authHandler.Login)
			auth.POST("/refresh", authHandler.RefreshToken)

			auth.GET("/oauth/wechat", ssoHandler.WeChatLogin)
			auth.GET("/oauth/wechat/callback", ssoHandler.WeChatCallback)
			auth.GET("/oauth/qq", ssoHandler.QQLogin)
			auth.GET("/oauth/qq/callback", ssoHandler.QQCallback)

			protected := auth.Group("")
			protected.Use(middleware.JWTAuth(jwtService))
			{
				protected.POST("/logout", authHandler.Logout)
				protected.GET("/profile", authHandler.GetProfile)
				protected.PUT("/profile", authHandler.UpdateProfile)
				protected.PUT("/password", authHandler.ChangePassword)

				protected.GET("/sessions", ssoHandler.GetActiveSessions)
				protected.DELETE("/sessions", ssoHandler.TerminateAllSessions)
				protected.DELETE("/sessions/:id", ssoHandler.TerminateSession)

				protected.GET("/oauth/accounts", ssoHandler.GetLinkedAccounts)
				protected.POST("/oauth/link/:provider", ssoHandler.LinkOAuthAccount)
				protected.DELETE("/oauth/unlink/:provider", ssoHandler.UnlinkOAuthAccount)
			}
		}

		roles := api.Group("/roles")
		roles.Use(middleware.JWTAuth(jwtService))
		roles.Use(middleware.RequireAdmin())
		{
			roles.GET("", rbacHandler.ListRoles)
			roles.GET("/:id", rbacHandler.GetRole)
			roles.POST("", rbacHandler.CreateRole)
			roles.PUT("/:id", rbacHandler.UpdateRole)
			roles.DELETE("/:id", rbacHandler.DeleteRole)
			roles.POST("/:id/permissions", rbacHandler.AssignPermissions)
			roles.GET("/:id/permissions", rbacHandler.GetRolePermissions)
		}

		permissions := api.Group("/permissions")
		permissions.Use(middleware.JWTAuth(jwtService))
		permissions.Use(middleware.RequireAdmin())
		{
			permissions.GET("", rbacHandler.ListPermissions)
		}
	}
}
