package middleware

import (
	"testing"
	"time"

	"github.com/gin-gonic/gin"
)

func TestNewRateLimiter(t *testing.T) {
	limiter := NewRateLimiter(10, 60)
	if limiter == nil {
		t.Fatal("NewRateLimiter() returned nil")
	}
}

func TestRateLimiter_Allow(t *testing.T) {
	limiter := NewRateLimiter(3, 60)

	for i := 0; i < 3; i++ {
		if !limiter.Allow("test-key") {
			t.Errorf("Request %d should be allowed", i+1)
		}
	}

	if limiter.Allow("test-key") {
		t.Error("Request 4 should be rate limited")
	}
}

func TestRateLimiter_DifferentKeys(t *testing.T) {
	limiter := NewRateLimiter(2, 60)

	if !limiter.Allow("key1") {
		t.Error("key1 request 1 should be allowed")
	}
	if !limiter.Allow("key1") {
		t.Error("key1 request 2 should be allowed")
	}
	if limiter.Allow("key1") {
		t.Error("key1 request 3 should be rate limited")
	}

	if !limiter.Allow("key2") {
		t.Error("key2 request 1 should be allowed (different key)")
	}
}

func TestNewCircuitBreaker(t *testing.T) {
	breaker := NewCircuitBreaker("test", 3, 5, 2, 60*time.Second, 30*time.Second)
	if breaker == nil {
		t.Fatal("NewCircuitBreaker() returned nil")
	}
}

func TestCircuitBreaker_State(t *testing.T) {
	breaker := NewCircuitBreaker("test", 3, 5, 2, 60*time.Second, 30*time.Second)

	if breaker.State() != StateClosed {
		t.Errorf("Initial state should be Closed, got %v", breaker.State())
	}
}

func TestCircuitBreaker_Allow_Closed(t *testing.T) {
	breaker := NewCircuitBreaker("test", 3, 5, 2, 60*time.Second, 30*time.Second)

	for i := 0; i < 10; i++ {
		if !breaker.Allow() {
			t.Errorf("Request %d should be allowed in closed state", i+1)
		}
	}
}

func TestCircuitBreaker_OpenAfterFailures(t *testing.T) {
	breaker := NewCircuitBreaker("test", 3, 5, 2, 60*time.Second, 30*time.Second)

	for i := 0; i < 3; i++ {
		breaker.RecordFailure()
	}

	if breaker.State() != StateOpen {
		t.Errorf("State should be Open after 3 failures, got %v", breaker.State())
	}

	if breaker.Allow() {
		t.Error("Requests should not be allowed in open state")
	}
}

func TestCircuitBreaker_HalfOpen(t *testing.T) {
	breaker := NewCircuitBreaker("test", 2, 1, 1, 100*time.Millisecond, 50*time.Millisecond)

	breaker.RecordFailure()
	breaker.RecordFailure()

	if breaker.State() != StateOpen {
		t.Errorf("State should be Open, got %v", breaker.State())
	}

	time.Sleep(150 * time.Millisecond)

	if breaker.State() != StateHalfOpen {
		t.Errorf("State should be HalfOpen after timeout, got %v", breaker.State())
	}
}

func TestCircuitBreaker_SuccessInHalfOpen(t *testing.T) {
	breaker := NewCircuitBreaker("test", 2, 1, 1, 100*time.Millisecond, 50*time.Millisecond)

	breaker.RecordFailure()
	breaker.RecordFailure()

	time.Sleep(150 * time.Millisecond)

	if !breaker.Allow() {
		t.Error("Should allow in half-open state")
	}

	breaker.RecordSuccess()

	if breaker.State() != StateClosed {
		t.Errorf("State should be Closed after success in half-open, got %v", breaker.State())
	}
}

func TestCircuitBreaker_FailureInHalfOpen(t *testing.T) {
	breaker := NewCircuitBreaker("test", 2, 1, 1, 100*time.Millisecond, 50*time.Millisecond)

	breaker.RecordFailure()
	breaker.RecordFailure()

	time.Sleep(150 * time.Millisecond)

	breaker.RecordFailure()

	if breaker.State() != StateOpen {
		t.Errorf("State should be Open after failure in half-open, got %v", breaker.State())
	}
}

func TestCircuitBreakerManager_Get(t *testing.T) {
	manager := NewCircuitBreakerManager()

	breaker1 := manager.Get("service1", 3, 5, 2, 60*time.Second, 30*time.Second)
	if breaker1 == nil {
		t.Fatal("Get() returned nil")
	}

	breaker2 := manager.Get("service1", 3, 5, 2, 60*time.Second, 30*time.Second)
	if breaker1 != breaker2 {
		t.Error("Same breaker should be returned for same name")
	}

	breaker3 := manager.Get("service2", 3, 5, 2, 60*time.Second, 30*time.Second)
	if breaker1 == breaker3 {
		t.Error("Different breakers should be returned for different names")
	}
}

func TestRecovery(t *testing.T) {
	gin.SetMode(gin.TestMode)

	recovery := Recovery()
	if recovery == nil {
		t.Fatal("Recovery() returned nil")
	}
}

func TestCORS(t *testing.T) {
	gin.SetMode(gin.TestMode)

	cors := CORS()
	if cors == nil {
		t.Fatal("CORS() returned nil")
	}
}

func TestLogger(t *testing.T) {
	gin.SetMode(gin.TestMode)

	logger := Logger()
	if logger == nil {
		t.Fatal("Logger() returned nil")
	}
}

func TestMetrics(t *testing.T) {
	gin.SetMode(gin.TestMode)

	metrics := Metrics("test-service")
	if metrics == nil {
		t.Fatal("Metrics() returned nil")
	}
}
