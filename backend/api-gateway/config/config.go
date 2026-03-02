package config

import (
	"time"

	"github.com/spf13/viper"
)

type Config struct {
	Server         ServerConfig         `mapstructure:"server"`
	Services       ServicesConfig       `mapstructure:"services"`
	RateLimit      RateLimitConfig      `mapstructure:"rate_limit"`
	CircuitBreaker CircuitBreakerConfig `mapstructure:"circuit_breaker"`
	Retry          RetryConfig          `mapstructure:"retry"`
	JWT            JWTConfig            `mapstructure:"jwt"`
	Logging        LoggingConfig        `mapstructure:"logging"`
	Metrics        MetricsConfig        `mapstructure:"metrics"`
}

type ServerConfig struct {
	Port int    `mapstructure:"port"`
	Mode string `mapstructure:"mode"`
}

type ServiceConfig struct {
	URL     string        `mapstructure:"url"`
	Timeout time.Duration `mapstructure:"timeout"`
}

type ServicesConfig struct {
	AuthService        ServiceConfig `mapstructure:"auth-service"`
	StudentService     ServiceConfig `mapstructure:"student-service"`
	GradeService       ServiceConfig `mapstructure:"grade-service"`
	HomeworkService    ServiceConfig `mapstructure:"homework-service"`
	ExamService        ServiceConfig `mapstructure:"exam-service"`
	LearningService    ServiceConfig `mapstructure:"learning-service"`
	CommunicationService ServiceConfig `mapstructure:"communication-service"`
}

type RateLimitConfig struct {
	Enabled           bool `mapstructure:"enabled"`
	RequestsPerSecond int  `mapstructure:"requests_per_second"`
	Burst             int  `mapstructure:"burst"`
}

type CircuitBreakerConfig struct {
	Enabled         bool          `mapstructure:"enabled"`
	MaxRequests     uint32        `mapstructure:"max_requests"`
	Interval        time.Duration `mapstructure:"interval"`
	Timeout         time.Duration `mapstructure:"timeout"`
	FailureThreshold uint32       `mapstructure:"failure_threshold"`
	SuccessThreshold uint32       `mapstructure:"success_threshold"`
}

type RetryConfig struct {
	Enabled         bool          `mapstructure:"enabled"`
	MaxAttempts     int           `mapstructure:"max_attempts"`
	InitialInterval time.Duration `mapstructure:"initial_interval"`
	MaxInterval     time.Duration `mapstructure:"max_interval"`
	Multiplier      float64       `mapstructure:"multiplier"`
}

type JWTConfig struct {
	Secret string        `mapstructure:"secret"`
	Issuer string        `mapstructure:"issuer"`
	Expiry time.Duration `mapstructure:"expiry"`
}

type LoggingConfig struct {
	Level  string `mapstructure:"level"`
	Format string `mapstructure:"format"`
	Output string `mapstructure:"output"`
}

type MetricsConfig struct {
	Enabled bool   `mapstructure:"enabled"`
	Path    string `mapstructure:"path"`
}

func Load(configPath string) (*Config, error) {
	v := viper.New()
	
	v.SetConfigFile(configPath)
	v.SetConfigType("yaml")
	
	v.AutomaticEnv()
	
	if err := v.ReadInConfig(); err != nil {
		return nil, err
	}
	
	var config Config
	if err := v.Unmarshal(&config); err != nil {
		return nil, err
	}
	
	return &config, nil
}
