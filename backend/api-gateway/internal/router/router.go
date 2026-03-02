package router

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"github.com/openzhixue/api-gateway/config"
	"github.com/openzhixue/api-gateway/internal/middleware"
	"github.com/openzhixue/api-gateway/internal/proxy"
	"github.com/openzhixue/api-gateway/pkg/logger"
	"github.com/openzhixue/api-gateway/pkg/metrics"
	"go.uber.org/zap"
)

type Router struct {
	engine       *gin.Engine
	proxy        *proxy.Proxy
	config       *config.Config
	rateLimiter  *middleware.RateLimiter
}

func NewRouter(cfg *config.Config) *Router {
	gin.SetMode(cfg.Server.Mode)
	
	engine := gin.New()
	
	p := proxy.NewProxy()
	p.SetRetryConfig(middleware.RetryConfig{
		MaxAttempts:     cfg.Retry.MaxAttempts,
		InitialInterval: cfg.Retry.InitialInterval,
		MaxInterval:     cfg.Retry.MaxInterval,
		Multiplier:      cfg.Retry.Multiplier,
	})
	
	p.RegisterService("auth-service", cfg.Services.AuthService.URL, cfg.Services.AuthService.Timeout)
	p.RegisterService("student-service", cfg.Services.StudentService.URL, cfg.Services.StudentService.Timeout)
	p.RegisterService("grade-service", cfg.Services.GradeService.URL, cfg.Services.GradeService.Timeout)
	p.RegisterService("homework-service", cfg.Services.HomeworkService.URL, cfg.Services.HomeworkService.Timeout)
	p.RegisterService("exam-service", cfg.Services.ExamService.URL, cfg.Services.ExamService.Timeout)
	p.RegisterService("learning-service", cfg.Services.LearningService.URL, cfg.Services.LearningService.Timeout)
	p.RegisterService("communication-service", cfg.Services.CommunicationService.URL, cfg.Services.CommunicationService.Timeout)
	
	var rateLimiter *middleware.RateLimiter
	if cfg.RateLimit.Enabled {
		rateLimiter = middleware.NewRateLimiter(cfg.RateLimit.RequestsPerSecond, cfg.RateLimit.Burst)
		rateLimiter.Cleanup(5 * time.Minute)
	}
	
	return &Router{
		engine:      engine,
		proxy:       p,
		config:      cfg,
		rateLimiter: rateLimiter,
	}
}

func (r *Router) Setup() *gin.Engine {
	r.engine.Use(middleware.Recovery())
	r.engine.Use(middleware.Logger())
	r.engine.Use(middleware.CORS())
	
	r.setupHealthCheck()
	r.setupMetrics()
	r.setupRoutes()
	
	return r.engine
}

func (r *Router) setupHealthCheck() {
	r.engine.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"timestamp": time.Now().Unix(),
			"service":   "api-gateway",
		})
	})
	
	r.engine.GET("/ready", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "ready",
		})
	})
	
	r.engine.GET("/live", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "alive",
		})
	})
}

func (r *Router) setupMetrics() {
	if r.config.Metrics.Enabled {
		r.engine.GET(r.config.Metrics.Path, gin.WrapH(promhttp.Handler()))
	}
}

func (r *Router) setupRoutes() {
	v1 := r.engine.Group("/api/v1")
	{
		r.setupAuthRoutes(v1)
		r.setupStudentRoutes(v1)
		r.setupGradeRoutes(v1)
		r.setupHomeworkRoutes(v1)
		r.setupExamRoutes(v1)
		r.setupLearningRoutes(v1)
		r.setupCommunicationRoutes(v1)
	}
}

func (r *Router) setupAuthRoutes(rg *gin.RouterGroup) {
	auth := rg.Group("/auth")
	auth.Use(r.serviceMiddleware("auth-service"))
	{
		auth.Any("/*path", r.proxy.ProxyRequest("auth-service"))
	}
}

func (r *Router) setupStudentRoutes(rg *gin.RouterGroup) {
	students := rg.Group("/students")
	students.Use(r.serviceMiddleware("student-service"))
	{
		students.Any("/*path", r.proxy.ProxyRequest("student-service"))
	}
}

func (r *Router) setupGradeRoutes(rg *gin.RouterGroup) {
	grades := rg.Group("/grades")
	grades.Use(r.serviceMiddleware("grade-service"))
	{
		grades.Any("/*path", r.proxy.ProxyRequest("grade-service"))
	}
}

func (r *Router) setupHomeworkRoutes(rg *gin.RouterGroup) {
	homework := rg.Group("/homework")
	homework.Use(r.serviceMiddleware("homework-service"))
	{
		homework.Any("/*path", r.proxy.ProxyRequest("homework-service"))
	}
}

func (r *Router) setupExamRoutes(rg *gin.RouterGroup) {
	exams := rg.Group("/exams")
	exams.Use(r.serviceMiddleware("exam-service"))
	{
		exams.Any("/*path", r.proxy.ProxyRequest("exam-service"))
	}
}

func (r *Router) setupLearningRoutes(rg *gin.RouterGroup) {
	learning := rg.Group("/learning")
	learning.Use(r.serviceMiddleware("learning-service"))
	{
		learning.Any("/*path", r.proxy.ProxyRequest("learning-service"))
	}
}

func (r *Router) setupCommunicationRoutes(rg *gin.RouterGroup) {
	communication := rg.Group("/communication")
	communication.Use(r.serviceMiddleware("communication-service"))
	{
		communication.Any("/*path", r.proxy.ProxyRequest("communication-service"))
	}
}

func (r *Router) serviceMiddleware(serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Set("service", serviceName)
		
		if r.config.RateLimit.Enabled && r.rateLimiter != nil {
			key := c.ClientIP()
			if !r.rateLimiter.Allow(key) {
				metrics.RecordRateLimitExceeded(serviceName)
				logger.Warn("Rate limit exceeded",
					zap.String("client_ip", key),
					zap.String("service", serviceName),
				)
				c.JSON(http.StatusTooManyRequests, gin.H{
					"code":    429,
					"message": "rate limit exceeded",
				})
				c.Abort()
				return
			}
		}
		
		c.Next()
	}
}
