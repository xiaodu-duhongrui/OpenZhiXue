package proxy

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/openzhixue/api-gateway/internal/middleware"
	"github.com/openzhixue/api-gateway/pkg/logger"
	"github.com/openzhixue/api-gateway/pkg/metrics"
	"go.uber.org/zap"
)

type ServiceConfig struct {
	Name    string
	URL     string
	Timeout time.Duration
}

type Proxy struct {
	client         *http.Client
	services       map[string]ServiceConfig
	circuitBreaker *middleware.CircuitBreakerManager
	retryConfig    middleware.RetryConfig
}

func NewProxy() *Proxy {
	return &Proxy{
		client: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				MaxIdleConns:        100,
				MaxIdleConnsPerHost: 20,
				IdleConnTimeout:     90 * time.Second,
			},
		},
		services:       make(map[string]ServiceConfig),
		circuitBreaker: middleware.NewCircuitBreakerManager(),
	}
}

func (p *Proxy) RegisterService(name, url string, timeout time.Duration) {
	p.services[name] = ServiceConfig{
		Name:    name,
		URL:     strings.TrimSuffix(url, "/"),
		Timeout: timeout,
	}
}

func (p *Proxy) SetRetryConfig(config middleware.RetryConfig) {
	p.retryConfig = config
}

func (p *Proxy) ProxyRequest(serviceName string) gin.HandlerFunc {
	return func(c *gin.Context) {
		service, exists := p.services[serviceName]
		if !exists {
			logger.Error("Service not found", zap.String("service", serviceName))
			c.JSON(502, gin.H{
				"code":    502,
				"message": "service not found",
			})
			c.Abort()
			return
		}
		
		breaker := p.circuitBreaker.Get(
			serviceName,
			3,
			5,
			2,
			60*time.Second,
			30*time.Second,
		)
		
		if !breaker.Allow() {
			metrics.SetCircuitBreakerState(serviceName, float64(middleware.StateOpen))
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
		
		targetURL := service.URL + c.Request.URL.Path
		if c.Request.URL.RawQuery != "" {
			targetURL += "?" + c.Request.URL.RawQuery
		}
		
		var resp *http.Response
		var err error
		var lastErr error
		
		maxAttempts := p.retryConfig.MaxAttempts
		if maxAttempts < 1 {
			maxAttempts = 1
		}
		
		for attempt := 0; attempt < maxAttempts; attempt++ {
			if attempt > 0 {
				select {
				case <-c.Request.Context().Done():
					c.JSON(499, gin.H{"code": 499, "message": "request cancelled"})
					c.Abort()
					return
				case <-time.After(p.calculateDelay(attempt)):
				}
				metrics.RecordRetryAttempt(serviceName, false)
			}
			
			resp, err = p.doRequest(c, targetURL, service.Timeout)
			if err == nil && resp.StatusCode < 500 {
				break
			}
			
			if err != nil {
				lastErr = err
				logger.Warn("Request failed",
					zap.String("service", serviceName),
					zap.Int("attempt", attempt+1),
					zap.Error(err),
				)
			}
			
			if resp != nil {
				resp.Body.Close()
			}
		}
		
		if err != nil || resp == nil {
			breaker.RecordFailure()
			metrics.SetCircuitBreakerState(serviceName, float64(breaker.State()))
			metrics.RecordProxyError(serviceName, "connection_error")
			
			errMsg := "service unavailable"
			if lastErr != nil {
				errMsg = lastErr.Error()
			}
			
			logger.Error("Proxy error",
				zap.String("service", serviceName),
				zap.String("url", targetURL),
				zap.Error(lastErr),
			)
			
			c.JSON(502, gin.H{
				"code":    502,
				"message": errMsg,
			})
			c.Abort()
			return
		}
		
		defer resp.Body.Close()
		
		if resp.StatusCode >= 500 {
			breaker.RecordFailure()
			metrics.SetCircuitBreakerState(serviceName, float64(breaker.State()))
		} else {
			breaker.RecordSuccess()
			metrics.SetCircuitBreakerState(serviceName, float64(breaker.State()))
		}
		
		for key, values := range resp.Header {
			for _, value := range values {
				c.Writer.Header().Add(key, value)
			}
		}
		
		c.Writer.WriteHeader(resp.StatusCode)
		
		_, err = io.Copy(c.Writer, resp.Body)
		if err != nil {
			logger.Error("Failed to write response",
				zap.String("service", serviceName),
				zap.Error(err),
			)
		}
	}
}

func (p *Proxy) doRequest(c *gin.Context, targetURL string, timeout time.Duration) (*http.Response, error) {
	ctx, cancel := context.WithTimeout(c.Request.Context(), timeout)
	defer cancel()
	
	req, err := http.NewRequestWithContext(ctx, c.Request.Method, targetURL, c.Request.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}
	
	for key, values := range c.Request.Header {
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}
	
	req.Header.Set("X-Forwarded-For", c.ClientIP())
	req.Header.Set("X-Real-IP", c.ClientIP())
	req.Header.Set("X-Request-ID", c.GetString("request_id"))
	
	return p.client.Do(req)
}

func (p *Proxy) calculateDelay(attempt int) time.Duration {
	delay := float64(p.retryConfig.InitialInterval)
	for i := 1; i < attempt; i++ {
		delay *= p.retryConfig.Multiplier
	}
	
	if delay > float64(p.retryConfig.MaxInterval) {
		delay = float64(p.retryConfig.MaxInterval)
	}
	
	return time.Duration(delay)
}
