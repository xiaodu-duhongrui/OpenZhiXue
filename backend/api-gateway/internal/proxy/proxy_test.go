package proxy

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/openzhixue/api-gateway/internal/middleware"
)

func TestNewProxy(t *testing.T) {
	proxy := NewProxy()
	if proxy == nil {
		t.Fatal("NewProxy() returned nil")
	}
	if proxy.client == nil {
		t.Error("Proxy client should not be nil")
	}
	if proxy.services == nil {
		t.Error("Proxy services map should not be nil")
	}
	if proxy.circuitBreaker == nil {
		t.Error("Proxy circuitBreaker should not be nil")
	}
}

func TestProxy_RegisterService(t *testing.T) {
	proxy := NewProxy()
	
	proxy.RegisterService("test-service", "http://localhost:8080", 30*time.Second)
	
	if len(proxy.services) != 1 {
		t.Errorf("Expected 1 service, got %d", len(proxy.services))
	}
	
	service, exists := proxy.services["test-service"]
	if !exists {
		t.Fatal("Service not found")
	}
	
	if service.Name != "test-service" {
		t.Errorf("Expected name 'test-service', got '%s'", service.Name)
	}
	if service.URL != "http://localhost:8080" {
		t.Errorf("Expected URL 'http://localhost:8080', got '%s'", service.URL)
	}
	if service.Timeout != 30*time.Second {
		t.Errorf("Expected timeout 30s, got %v", service.Timeout)
	}
}

func TestProxy_RegisterService_TrailingSlash(t *testing.T) {
	proxy := NewProxy()
	
	proxy.RegisterService("test-service", "http://localhost:8080/", 30*time.Second)
	
	service := proxy.services["test-service"]
	if service.URL != "http://localhost:8080" {
		t.Errorf("Trailing slash should be trimmed, got '%s'", service.URL)
	}
}

func TestProxy_ProxyRequest_ServiceNotFound(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	proxy := NewProxy()
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodGet, "/test", nil)
	
	handler := proxy.ProxyRequest("non-existent-service")
	handler(c)
	
	if w.Code != http.StatusBadGateway {
		t.Errorf("Expected status %d, got %d", http.StatusBadGateway, w.Code)
	}
}

func TestProxy_ProxyRequest_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)
	
	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"code":0,"message":"success"}`))
	}))
	defer mockServer.Close()
	
	proxy := NewProxy()
	proxy.RegisterService("test-service", mockServer.URL, 5*time.Second)
	proxy.SetRetryConfig(middleware.RetryConfig{
		MaxAttempts:     1,
		InitialInterval: 100 * time.Millisecond,
		MaxInterval:     1 * time.Second,
		Multiplier:      2.0,
	})
	
	w := httptest.NewRecorder()
	c, _ := gin.CreateTestContext(w)
	c.Request = httptest.NewRequest(http.MethodGet, "/test", nil)
	c.Set("request_id", "test-request-id")
	
	handler := proxy.ProxyRequest("test-service")
	handler(c)
	
	if w.Code != http.StatusOK {
		t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
	}
}

func TestProxy_CalculateDelay(t *testing.T) {
	proxy := NewProxy()
	proxy.SetRetryConfig(middleware.RetryConfig{
		MaxAttempts:     3,
		InitialInterval: 100 * time.Millisecond,
		MaxInterval:     1 * time.Second,
		Multiplier:      2.0,
	})
	
	tests := []struct {
		attempt  int
		expected time.Duration
	}{
		{1, 100 * time.Millisecond},
		{2, 200 * time.Millisecond},
		{3, 400 * time.Millisecond},
	}
	
	for _, tt := range tests {
		delay := proxy.calculateDelay(tt.attempt)
		if delay != tt.expected {
			t.Errorf("Attempt %d: expected delay %v, got %v", tt.attempt, tt.expected, delay)
		}
	}
}

func TestProxy_CalculateDelay_MaxInterval(t *testing.T) {
	proxy := NewProxy()
	proxy.SetRetryConfig(middleware.RetryConfig{
		MaxAttempts:     10,
		InitialInterval: 100 * time.Millisecond,
		MaxInterval:     500 * time.Millisecond,
		Multiplier:      2.0,
	})
	
	delay := proxy.calculateDelay(10)
	if delay > 500*time.Millisecond {
		t.Errorf("Delay should not exceed MaxInterval, got %v", delay)
	}
}
