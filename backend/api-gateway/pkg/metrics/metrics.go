package metrics

import (
	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	RequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "api_gateway_requests_total",
			Help: "Total number of requests by service and method",
		},
		[]string{"service", "method", "path", "status"},
	)

	RequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "api_gateway_request_duration_seconds",
			Help:    "Request duration in seconds",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"service", "method", "path"},
	)

	RequestsInFlight = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "api_gateway_requests_in_flight",
			Help: "Current number of requests being processed",
		},
		[]string{"service"},
	)

	RateLimitExceeded = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "api_gateway_rate_limit_exceeded_total",
			Help: "Total number of rate limit exceeded events",
		},
		[]string{"service"},
	)

	CircuitBreakerState = promauto.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "api_gateway_circuit_breaker_state",
			Help: "Circuit breaker state: 0=closed, 1=open, 2=half-open",
		},
		[]string{"service"},
	)

	RetryAttempts = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "api_gateway_retry_attempts_total",
			Help: "Total number of retry attempts",
		},
		[]string{"service", "success"},
	)

	ProxyErrors = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "api_gateway_proxy_errors_total",
			Help: "Total number of proxy errors",
		},
		[]string{"service", "error_type"},
	)
)

func RecordRequest(service, method, path string, status int) {
	RequestsTotal.WithLabelValues(service, method, path, string(rune(status))).Inc()
}

func RecordDuration(service, method, path string, duration float64) {
	RequestDuration.WithLabelValues(service, method, path).Observe(duration)
}

func IncInFlight(service string) {
	RequestsInFlight.WithLabelValues(service).Inc()
}

func DecInFlight(service string) {
	RequestsInFlight.WithLabelValues(service).Dec()
}

func RecordRateLimitExceeded(service string) {
	RateLimitExceeded.WithLabelValues(service).Inc()
}

func SetCircuitBreakerState(service string, state float64) {
	CircuitBreakerState.WithLabelValues(service).Set(state)
}

func RecordRetryAttempt(service string, success bool) {
	RetryAttempts.WithLabelValues(service, string(rune(0))).Inc()
}

func RecordProxyError(service, errorType string) {
	ProxyErrors.WithLabelValues(service, errorType).Inc()
}
