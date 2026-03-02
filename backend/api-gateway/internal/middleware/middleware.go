package middleware

import (
	"time"

	"github.com/gin-gonic/gin"
	"github.com/openzhixue/api-gateway/pkg/logger"
	"github.com/openzhixue/api-gateway/pkg/metrics"
	"go.uber.org/zap"
)

func Logger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		query := c.Request.URL.RawQuery
		
		c.Next()
		
		latency := time.Since(start)
		status := c.Writer.Status()
		method := c.Request.Method
		clientIP := c.ClientIP()
		
		if query != "" {
			path = path + "?" + query
		}
		
		if status >= 500 {
			logger.Error("Request",
				zap.Int("status", status),
				zap.String("method", method),
				zap.String("path", path),
				zap.String("client_ip", clientIP),
				zap.Duration("latency", latency),
				zap.String("user-agent", c.Request.UserAgent()),
			)
		} else if status >= 400 {
			logger.Warn("Request",
				zap.Int("status", status),
				zap.String("method", method),
				zap.String("path", path),
				zap.String("client_ip", clientIP),
				zap.Duration("latency", latency),
			)
		} else {
			logger.Info("Request",
				zap.Int("status", status),
				zap.String("method", method),
				zap.String("path", path),
				zap.String("client_ip", clientIP),
				zap.Duration("latency", latency),
			)
		}
	}
}

func Metrics(serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method
		
		metrics.IncInFlight(serviceName)
		
		c.Next()
		
		metrics.DecInFlight(serviceName)
		
		duration := time.Since(start).Seconds()
		status := c.Writer.Status()
		
		metrics.RecordRequest(serviceName, method, path, status)
		metrics.RecordDuration(serviceName, method, path, duration)
	}
}

func RateLimit(limiter *RateLimiter, serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		key := c.ClientIP()
		
		if !limiter.Allow(key) {
			metrics.RecordRateLimitExceeded(serviceName)
			logger.Warn("Rate limit exceeded",
				zap.String("client_ip", key),
				zap.String("service", serviceName),
			)
			c.JSON(429, gin.H{
				"code":    429,
				"message": "rate limit exceeded",
			})
			c.Abort()
			return
		}
		
		c.Next()
	}
}

func CircuitBreakerMiddleware(breaker *CircuitBreaker, serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		if !breaker.Allow() {
			metrics.SetCircuitBreakerState(serviceName, float64(StateOpen))
			logger.Warn("Circuit breaker open",
				zap.String("service", serviceName),
			)
			c.JSON(503, gin.H{
				"code":    503,
				"message": "service temporarily unavailable",
			})
			c.Abort()
			return
		}
		
		c.Next()
		
		status := c.Writer.Status()
		if status >= 500 {
			breaker.RecordFailure()
			metrics.SetCircuitBreakerState(serviceName, float64(breaker.State()))
		} else {
			breaker.RecordSuccess()
			metrics.SetCircuitBreakerState(serviceName, float64(breaker.State()))
		}
	}
}

func Recovery() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				logger.Error("Panic recovered",
					zap.Any("error", err),
					zap.String("path", c.Request.URL.Path),
				)
				c.JSON(500, gin.H{
					"code":    500,
					"message": "internal server error",
				})
				c.Abort()
			}
		}()
		c.Next()
	}
}

func CORS() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Credentials", "true")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE, PATCH")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	}
}
