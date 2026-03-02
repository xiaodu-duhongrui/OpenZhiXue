package middleware

import (
	"sync"
	"sync/atomic"
	"time"
)

type State int32

const (
	StateClosed State = iota
	StateOpen
	StateHalfOpen
)

type CircuitBreaker struct {
	name             string
	maxRequests      uint32
	interval         time.Duration
	timeout          time.Duration
	failureThreshold uint32
	successThreshold uint32
	
	state            int32
	failures         uint32
	successes        uint32
	lastStateChange  time.Time
	mu               sync.RWMutex
}

func NewCircuitBreaker(name string, maxRequests, failureThreshold, successThreshold uint32, interval, timeout time.Duration) *CircuitBreaker {
	return &CircuitBreaker{
		name:             name,
		maxRequests:      maxRequests,
		interval:         interval,
		timeout:          timeout,
		failureThreshold: failureThreshold,
		successThreshold: successThreshold,
		state:            int32(StateClosed),
		lastStateChange:  time.Now(),
	}
}

func (cb *CircuitBreaker) Name() string {
	return cb.name
}

func (cb *CircuitBreaker) State() State {
	return State(atomic.LoadInt32(&cb.state))
}

func (cb *CircuitBreaker) Allow() bool {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	
	switch cb.State() {
	case StateClosed:
		return true
	case StateOpen:
		if time.Since(cb.lastStateChange) > cb.timeout {
			cb.setState(StateHalfOpen)
			return true
		}
		return false
	case StateHalfOpen:
		return cb.successes < cb.maxRequests
	default:
		return false
	}
}

func (cb *CircuitBreaker) RecordSuccess() {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	
	switch cb.State() {
	case StateClosed:
		cb.failures = 0
	case StateHalfOpen:
		cb.successes++
		if cb.successes >= cb.successThreshold {
			cb.setState(StateClosed)
		}
	}
}

func (cb *CircuitBreaker) RecordFailure() {
	cb.mu.Lock()
	defer cb.mu.Unlock()
	
	switch cb.State() {
	case StateClosed:
		cb.failures++
		if cb.failures >= cb.failureThreshold {
			cb.setState(StateOpen)
		}
	case StateHalfOpen:
		cb.setState(StateOpen)
	}
}

func (cb *CircuitBreaker) setState(state State) {
	atomic.StoreInt32(&cb.state, int32(state))
	cb.lastStateChange = time.Now()
	cb.failures = 0
	cb.successes = 0
}

type CircuitBreakerManager struct {
	breakers map[string]*CircuitBreaker
	mu       sync.RWMutex
}

func NewCircuitBreakerManager() *CircuitBreakerManager {
	return &CircuitBreakerManager{
		breakers: make(map[string]*CircuitBreaker),
	}
}

func (m *CircuitBreakerManager) Get(name string, maxRequests, failureThreshold, successThreshold uint32, interval, timeout time.Duration) *CircuitBreaker {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	if breaker, exists := m.breakers[name]; exists {
		return breaker
	}
	
	breaker := NewCircuitBreaker(name, maxRequests, failureThreshold, successThreshold, interval, timeout)
	m.breakers[name] = breaker
	return breaker
}
