package main

import (
	"context"
	"flag"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/openzhixue/api-gateway/config"
	"github.com/openzhixue/api-gateway/internal/router"
	"github.com/openzhixue/api-gateway/pkg/logger"
	"go.uber.org/zap"
)

var (
	configPath = flag.String("config", "config/config.yaml", "path to config file")
	version    = "1.0.0"
)

func main() {
	flag.Parse()
	
	cfg, err := config.Load(*configPath)
	if err != nil {
		fmt.Printf("Failed to load config: %v\n", err)
		os.Exit(1)
	}
	
	if err := logger.Init(cfg.Logging.Level, cfg.Logging.Format, cfg.Logging.Output); err != nil {
		fmt.Printf("Failed to initialize logger: %v\n", err)
		os.Exit(1)
	}
	defer logger.Sync()
	
	logger.Info("Starting API Gateway",
		zap.String("version", version),
		zap.Int("port", cfg.Server.Port),
	)
	
	r := router.NewRouter(cfg)
	engine := r.Setup()
	
	srv := &http.Server{
		Addr:         fmt.Sprintf(":%d", cfg.Server.Port),
		Handler:      engine,
		ReadTimeout:  30 * time.Second,
		WriteTimeout: 30 * time.Second,
		IdleTimeout:  120 * time.Second,
	}
	
	go func() {
		logger.Info("Server starting", zap.Int("port", cfg.Server.Port))
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			logger.Fatal("Failed to start server", zap.Error(err))
		}
	}()
	
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	
	logger.Info("Shutting down server...")
	
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()
	
	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("Server forced to shutdown", zap.Error(err))
	}
	
	logger.Info("Server exited")
}
