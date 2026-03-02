package database

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
	"github.com/spf13/viper"
)

type DBConfig struct {
	Host            string
	Port            int
	User            string
	Password        string
	Name            string
	SSLMode         string
	MaxConns        int32
	MinConns        int32
	MaxConnLifetime time.Duration
	MaxConnIdleTime time.Duration
}

func NewDBConfig() *DBConfig {
	return &DBConfig{
		Host:            viper.GetString("database.host"),
		Port:            viper.GetInt("database.port"),
		User:            viper.GetString("database.user"),
		Password:        viper.GetString("database.password"),
		Name:            viper.GetString("database.name"),
		SSLMode:         viper.GetString("database.sslmode"),
		MaxConns:        viper.GetInt32("database.max_conns"),
		MinConns:        viper.GetInt32("database.min_conns"),
		MaxConnLifetime: viper.GetDuration("database.max_conn_lifetime"),
		MaxConnIdleTime: viper.GetDuration("database.max_conn_idle_time"),
	}
}

func (c *DBConfig) DSN() string {
	return fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		c.Host, c.Port, c.User, c.Password, c.Name, c.SSLMode,
	)
}

func NewPool(ctx context.Context, config *DBConfig) (*pgxpool.Pool, error) {
	poolConfig, err := pgxpool.ParseConfig(config.DSN())
	if err != nil {
		return nil, fmt.Errorf("failed to parse database config: %w", err)
	}

	poolConfig.MaxConns = config.MaxConns
	poolConfig.MinConns = config.MinConns
	poolConfig.MaxConnLifetime = config.MaxConnLifetime
	poolConfig.MaxConnIdleTime = config.MaxConnIdleTime

	pool, err := pgxpool.NewWithConfig(ctx, poolConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create connection pool: %w", err)
	}

	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	if err := pool.Ping(ctx); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	return pool, nil
}
