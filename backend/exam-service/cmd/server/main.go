package main

import (
	"context"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/openzhixue/exam-service/internal/database"
	"github.com/openzhixue/exam-service/internal/handlers"
	"github.com/openzhixue/exam-service/internal/middleware"
	"github.com/openzhixue/exam-service/internal/repositories"
	"github.com/openzhixue/exam-service/internal/services"
	"github.com/spf13/viper"
	"go.uber.org/zap"
)

func main() {
	initConfig()

	logger, err := zap.NewProduction()
	if err != nil {
		log.Fatalf("failed to create logger: %v", err)
	}
	defer logger.Sync()

	dbConfig := database.NewDBConfig()
	pool, err := database.NewPool(context.Background(), dbConfig)
	if err != nil {
		logger.Fatal("failed to connect to database", zap.Error(err))
	}
	defer pool.Close()

	logger.Info("database connection established")

	if err := database.Migrate(pool); err != nil {
		logger.Fatal("failed to run migrations", zap.Error(err))
	}
	logger.Info("database migrations completed")

	redisConfig := database.NewRedisConfig()
	redisClient, err := database.NewRedisClient(redisConfig)
	if err != nil {
		logger.Warn("failed to connect to redis, caching disabled", zap.Error(err))
	} else {
		logger.Info("redis connection established")
		defer redisClient.Close()
	}

	examRepo := repositories.NewExamRepository(pool)
	questionRepo := repositories.NewQuestionRepository(pool)
	sessionRepo := repositories.NewSessionRepository(pool)
	answerRepo := repositories.NewAnswerRepository(pool)

	examService := services.NewExamService(examRepo, questionRepo, sessionRepo)
	questionService := services.NewQuestionService(questionRepo, examRepo)
	sessionService := services.NewSessionService(sessionRepo, examRepo, answerRepo, questionRepo)
	gradingService := services.NewGradingService(answerRepo, sessionRepo, questionRepo, examRepo)
	statisticsService := services.NewStatisticsService(examRepo, sessionRepo, answerRepo, questionRepo)

	examHandler := handlers.NewExamHandler(examService)
	questionHandler := handlers.NewQuestionHandler(questionService)
	sessionHandler := handlers.NewSessionHandler(sessionService, gradingService)
	gradingHandler := handlers.NewGradingHandler(gradingService)
	statisticsHandler := handlers.NewStatisticsHandler(statisticsService)

	router := setupRouter(examHandler, questionHandler, sessionHandler, gradingHandler, statisticsHandler)

	port := viper.GetString("server.port")
	if port == "" {
		port = "8085"
	}

	srv := &http.Server{
		Addr:    ":" + port,
		Handler: router,
	}

	go func() {
		logger.Info("starting server", zap.String("port", port))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("failed to start server", zap.Error(err))
		}
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("shutting down server...")

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Fatal("server forced to shutdown", zap.Error(err))
	}

	logger.Info("server exited")
}

func initConfig() {
	viper.SetConfigName("config")
	viper.SetConfigType("yaml")
	viper.AddConfigPath("./config")
	viper.AddConfigPath(".")

	viper.AutomaticEnv()

	if err := viper.ReadInConfig(); err != nil {
		log.Printf("warning: failed to read config file: %v", err)
	}

	viper.SetDefault("server.port", "8085")
	viper.SetDefault("server.mode", "debug")
	viper.SetDefault("database.host", "localhost")
	viper.SetDefault("database.port", 5432)
	viper.SetDefault("database.user", "openzhixue")
	viper.SetDefault("database.password", "openzhixue123")
	viper.SetDefault("database.name", "openzhixue_exams")
	viper.SetDefault("database.sslmode", "disable")
	viper.SetDefault("database.max_conns", 25)
	viper.SetDefault("database.min_conns", 5)
	viper.SetDefault("jwt.secret", "your-jwt-secret-key")
}

func setupRouter(
	examHandler *handlers.ExamHandler,
	questionHandler *handlers.QuestionHandler,
	sessionHandler *handlers.SessionHandler,
	gradingHandler *handlers.GradingHandler,
	statisticsHandler *handlers.StatisticsHandler,
) *gin.Engine {
	mode := viper.GetString("server.mode")
	if mode == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	router := gin.New()
	router.Use(middleware.RecoveryMiddleware())
	router.Use(middleware.CORSMiddleware())
	router.Use(gin.Logger())

	jwtSecret := viper.GetString("jwt.secret")

	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"service": "exam-service",
			"time":    time.Now().Format(time.RFC3339),
		})
	})

	api := router.Group("/api/v1")
	{
		exams := api.Group("/exams")
		exams.Use(middleware.AuthMiddleware(jwtSecret))
		{
			exams.POST("", examHandler.CreateExam)
			exams.GET("", examHandler.ListExams)
			exams.GET("/:id", examHandler.GetExam)
			exams.GET("/:id/detail", examHandler.GetExamDetail)
			exams.PUT("/:id", examHandler.UpdateExam)
			exams.DELETE("/:id", examHandler.DeleteExam)
			exams.POST("/:id/publish", examHandler.PublishExam)

			exams.POST("/:id/start", sessionHandler.StartExam)
			exams.GET("/:id/questions", sessionHandler.GetExamQuestions)
			exams.POST("/:id/answer", sessionHandler.SubmitAnswer)
			exams.POST("/:id/submit", sessionHandler.SubmitExam)
			exams.GET("/:id/result", sessionHandler.GetExamResult)

			exams.POST("/:id/grade", gradingHandler.GradeAnswer)

			exams.GET("/:id/statistics", statisticsHandler.GetExamStatistics)
			exams.GET("/:id/analysis", statisticsHandler.GetExamAnalysis)
			exams.GET("/:id/ranking", statisticsHandler.GetRanking)
			exams.GET("/:id/top-performers", statisticsHandler.GetTopPerformers)
			exams.GET("/:id/bottom-performers", statisticsHandler.GetBottomPerformers)
		}

		questions := api.Group("/questions")
		questions.Use(middleware.AuthMiddleware(jwtSecret))
		{
			questions.POST("", questionHandler.CreateQuestion)
			questions.POST("/batch", questionHandler.CreateQuestionsBatch)
			questions.GET("/:id", questionHandler.GetQuestion)
			questions.PUT("/:id", questionHandler.UpdateQuestion)
			questions.DELETE("/:id", questionHandler.DeleteQuestion)
		}

		sessions := api.Group("/sessions")
		sessions.Use(middleware.AuthMiddleware(jwtSecret))
		{
			sessions.GET("/:sessionId", sessionHandler.GetSession)
			sessions.POST("/:sessionId/auto-grade", gradingHandler.AutoGradeSession)
			sessions.GET("/:sessionId/result", gradingHandler.GetStudentResult)
		}
	}

	return router
}
