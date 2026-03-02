#!/bin/bash

# OpenZhixue Platform - Development Environment Stop Script
# This script helps you stop all services

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "=========================================="
echo "  停止 OpenZhixue 服务"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"

echo "🛑 请手动停止以下服务进程："
echo ""
echo "后端服务："
echo "   - API Gateway (Go)"
echo "   - Auth Service (Go)"
echo "   - Student Service (Java)"
echo "   - Grade Service (Python)"
echo "   - Homework Service (Rust)"
echo "   - Exam Service (Go)"
echo "   - Learning Service (Python)"
echo "   - Communication Service (Java)"
echo ""
echo "前端服务："
echo "   - Web Frontend (Node.js)"
echo ""
echo "数据库和中间件（如果本地安装）："
echo "   - PostgreSQL"
echo "   - MySQL"
echo "   - MongoDB"
echo "   - Redis"
echo "   - RabbitMQ"
echo ""
echo "💡 提示：可以使用各进程对应的停止命令或任务管理器来停止服务"
echo ""
