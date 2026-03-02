#!/bin/bash

# OpenZhixue Platform - Development Environment Start Script
# This script helps you start all services for local development

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=========================================="
echo "  OpenZhixue Development Environment"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"

if [ ! -f .env ]; then
    echo "⚠️  .env file not found, creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please review and modify as needed."
    echo ""
fi

echo "💡 本地开发环境启动指南"
echo ""
echo "请按照以下步骤启动各服务："
echo ""
echo "1. 启动数据库和中间件（需要手动安装）："
echo "   - PostgreSQL (端口 5432)"
echo "   - MySQL (端口 3306)"
echo "   - MongoDB (端口 27017)"
echo "   - Redis (端口 6379)"
echo "   - RabbitMQ (端口 5672, 管理端口 15672)"
echo ""
echo "2. 启动后端服务："
echo "   - API Gateway: cd backend/api-gateway && go run cmd/main.go"
echo "   - Auth Service: cd backend/auth-service && go run cmd/server/main.go"
echo "   - Student Service: cd backend/student-service && ./gradlew bootRun"
echo "   - Grade Service: cd backend/grade-service && python -m uvicorn app.main:app --reload"
echo "   - Homework Service: cd backend/homework-service && cargo run"
echo "   - Exam Service: cd backend/exam-service && go run cmd/server/main.go"
echo "   - Learning Service: cd backend/learning-service && python -m uvicorn app.main:app --reload"
echo "   - Communication Service: cd backend/communication-service && ./gradlew bootRun"
echo ""
echo "3. 启动前端："
echo "   cd frontend/web && npm install && npm run dev"
echo ""
echo "=========================================="
echo "  服务端口和配置信息"
echo "=========================================="
echo ""
echo "📊 默认服务端口:"
echo "   PostgreSQL:     localhost:5432"
echo "   MySQL:          localhost:3306"
echo "   MongoDB:        localhost:27017"
echo "   Redis:          localhost:6379"
echo "   RabbitMQ:       localhost:5672"
echo "   RabbitMQ Mgmt:  http://localhost:15672"
echo ""
echo "📝 默认凭证:"
echo "   PostgreSQL:     openzhixue / openzhixue123"
echo "   MySQL:          root / root123"
echo "   MongoDB:        admin / admin123"
echo "   RabbitMQ:       openzhixue / openzhixue123"
echo ""
echo "🛑 要停止服务，请手动停止各服务进程"
echo ""
