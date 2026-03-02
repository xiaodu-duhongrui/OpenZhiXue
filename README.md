# OpenZhixue - 智学网开源版

## 项目简介

OpenZhixue（智学网开源版）是一个面向 K12 教育场景的综合性智慧校园管理平台。本项目采用微服务架构，提供学生管理、成绩分析、作业管理、考试管理、在线学习、家校沟通等核心功能，旨在为学校、教师、学生和家长提供一站式教育信息化解决方案。

### 核心特性

- **微服务架构**：采用多语言微服务架构，各服务独立部署、独立扩展
- **高性能**：基于现代化的技术栈，支持高并发场景
- **可扩展**：模块化设计，易于扩展新功能
- **开源免费**：完全开源，可自由部署和定制

## 技术栈

### 后端服务

| 服务 | 技术栈 | 说明 |
|------|--------|------|
| API Gateway | Go | API 网关，路由转发、限流、鉴权 |
| Auth Service | Go | 用户认证授权服务 |
| Student Service | Java 25 | 学生信息管理服务 |
| Grade Service | Python | 成绩管理与分析服务 |
| Homework Service | Rust | 作业管理服务 |
| Exam Service | Go | 考试管理服务 |
| Learning Service | Python | 在线学习服务 |
| Communication Service | Java 25 | 家校沟通服务 |

### 前端

| 项目 | 技术栈 | 说明 |
|------|--------|------|
| Web | Vue 3 / React | Web 管理平台 |
| Mobile | Flutter | 移动端应用（iOS/Android） |

### 基础设施

- **消息队列**：RabbitMQ / Kafka
- **数据库**：PostgreSQL / MySQL / MongoDB
- **缓存**：Redis

## 项目结构

```
openzhixue/
├── backend/                    # 后端服务
│   ├── api-gateway/           # API 网关 (Go)
│   ├── auth-service/          # 用户认证服务 (Go)
│   ├── student-service/       # 学生管理服务 (Java 25)
│   ├── grade-service/         # 成绩管理服务 (Python)
│   ├── homework-service/      # 作业管理服务 (Rust)
│   ├── exam-service/          # 考试管理服务 (Go)
│   ├── learning-service/      # 在线学习服务 (Python)
│   └── communication-service/ # 家校沟通服务 (Java 25)
├── frontend/                   # 前端项目
│   ├── web/                   # Web UI
│   └── mobile/                # 移动端 (Flutter)
├── infrastructure/             # 基础设施
│   └── scripts/               # 开发脚本
├── docs/                       # 文档
├── .github/                    # GitHub 配置
│   └── workflows/             # CI/CD 工作流
├── .gitignore
└── README.md
```

## 快速开始

### 环境要求

- Go 1.21+
- Java 25 (JDK)
- Python 3.11+
- Rust 1.75+
- Node.js 20+
- Flutter 3.16+
- PostgreSQL 15+
- MySQL 8.0+
- MongoDB 7.0+
- Redis 7.0+
- RabbitMQ 3.12+

### 本地开发

1. **克隆项目**

```bash
git clone https://github.com/your-org/openzhixue.git
cd openzhixue
```

2. **安装并启动数据库和中间件**

需要手动安装以下服务：
- PostgreSQL (端口 5432)
- MySQL (端口 3306)
- MongoDB (端口 27017)
- Redis (端口 6379)
- RabbitMQ (端口 5672)

3. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

4. **启动后端服务**

各服务独立启动：

```bash
# API Gateway
cd backend/api-gateway
go run cmd/main.go

# Auth Service
cd backend/auth-service
go run cmd/server/main.go

# Student Service
cd backend/student-service
./gradlew bootRun

# Grade Service
cd backend/grade-service
python -m uvicorn app.main:app --reload

# Homework Service
cd backend/homework-service
cargo run

# Exam Service
cd backend/exam-service
go run cmd/server/main.go

# Learning Service
cd backend/learning-service
python -m uvicorn app.main:app --reload

# Communication Service
cd backend/communication-service
./gradlew bootRun
```

5. **启动前端**

```bash
cd frontend/web
npm install
npm run dev
```

6. **访问应用**

- Web 前端：http://localhost:3000
- API Gateway: http://localhost:8080

## 开发指南

### 分支管理

- `main` - 主分支，稳定版本
- `develop` - 开发分支
- `feature/*` - 功能分支
- `hotfix/*` - 热修复分支

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 贡献指南

欢迎贡献代码！请阅读 [贡献指南](docs/CONTRIBUTING.md) 了解详情。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 联系方式

- Issue: [GitHub Issues](https://github.com/your-org/openzhixue/issues)
- Email: openzhixue@example.com
