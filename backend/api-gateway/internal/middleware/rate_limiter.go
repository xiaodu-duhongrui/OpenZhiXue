package middleware

import (
	"sync"
	"time"

	"golang.org/x/time/rate"
)

type RateLimiter struct {
	limiters map[string]*rate.Limiter
	mu       sync.RWMutex
	rps      int
	burst    int
}

func NewRateLimiter(rps, burst int) *RateLimiter {
	return &RateLimiter{
		limiters: make(map[string]*rate.Limiter),
		rps:      rps,
		burst:    burst,
	}
}

func (rl *RateLimiter) GetLimiter(key string) *rate.Limiter {
	rl.mu.Lock()
	defer rl.mu.Unlock()
	
	limiter, exists := rl.limiters[key]
	if !exists {
		limiter = rate.NewLimiter(rate.Limit(rl.rps), rl.burst)
		rl.limiters[key] = limiter
	}
	
	return limiter
}

func (rl *RateLimiter) Allow(key string) bool {
	return rl.GetLimiter(key).Allow()
}

func (rl *RateLimiter) Wait(key string) error {
	return rl.GetLimiter(key).Wait(nil)
}

func (rl *RateLimiter) Reserve(key string) *rate.Reservation {
	return rl.GetLimiter(key).Reserve()
}

func (rl *RateLimiter) Cleanup(interval time.Duration) {
	ticker := time.NewTicker(interval)
	go func() {
		for range ticker.C {
			rl.mu.Lock()
			rl.limiters = make(map[string]*rate.Limiter)
			rl.mu.Unlock()
		}
	}()
}
