package middleware

import (
	"context"
	"math/rand"
	"net/http"
	"time"
)

type RetryConfig struct {
	MaxAttempts     int
	InitialInterval time.Duration
	MaxInterval     time.Duration
	Multiplier      float64
}

type RetryableTransport struct {
	transport http.RoundTripper
	config    RetryConfig
}

func NewRetryableTransport(config RetryConfig) *RetryableTransport {
	return &RetryableTransport{
		transport: http.DefaultTransport,
		config:    config,
	}
}

func (t *RetryableTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	var lastErr error
	var resp *http.Response
	
	for attempt := 0; attempt < t.config.MaxAttempts; attempt++ {
		if attempt > 0 {
			select {
			case <-req.Context().Done():
				return nil, req.Context().Err()
			case <-time.After(t.calculateDelay(attempt)):
			}
		}
		
		resp, lastErr = t.transport.RoundTrip(req)
		if lastErr == nil && !t.shouldRetry(resp.StatusCode) {
			return resp, nil
		}
		
		if resp != nil {
			resp.Body.Close()
		}
	}
	
	if lastErr != nil {
		return nil, lastErr
	}
	
	return resp, nil
}

func (t *RetryableTransport) shouldRetry(statusCode int) bool {
	return statusCode == http.StatusServiceUnavailable ||
		statusCode == http.StatusGatewayTimeout ||
		statusCode == http.StatusTooManyRequests ||
		statusCode == http.StatusInternalServerError
}

func (t *RetryableTransport) calculateDelay(attempt int) time.Duration {
	delay := float64(t.config.InitialInterval) * pow(t.config.Multiplier, float64(attempt-1))
	if delay > float64(t.config.MaxInterval) {
		delay = float64(t.config.MaxInterval)
	}
	
	jitter := rand.Float64() * 0.1 * delay
	return time.Duration(delay + jitter)
}

func pow(base, exp float64) float64 {
	result := 1.0
	for i := 0; i < int(exp); i++ {
		result *= base
	}
	return result
}

type RetryMiddleware struct {
	config RetryConfig
}

func NewRetryMiddleware(config RetryConfig) *RetryMiddleware {
	return &RetryMiddleware{config: config}
}

func (m *RetryMiddleware) DoWithRetry(ctx context.Context, fn func() error) error {
	var lastErr error
	
	for attempt := 0; attempt < m.config.MaxAttempts; attempt++ {
		if attempt > 0 {
			select {
			case <-ctx.Done():
				return ctx.Err()
			case <-time.After(m.calculateDelay(attempt)):
			}
		}
		
		if err := fn(); err == nil {
			return nil
		} else {
			lastErr = err
		}
	}
	
	return lastErr
}

func (m *RetryMiddleware) calculateDelay(attempt int) time.Duration {
	delay := float64(m.config.InitialInterval) * pow(m.config.Multiplier, float64(attempt-1))
	if delay > float64(m.config.MaxInterval) {
		delay = float64(m.config.MaxInterval)
	}
	
	jitter := rand.Float64() * 0.1 * delay
	return time.Duration(delay + jitter)
}
