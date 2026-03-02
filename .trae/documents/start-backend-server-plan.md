# 启动后端服务器计划

## 项目概述

OpenZhixue 是一个微服务架构的智慧教育平台，后端包含多个独立服务，使用不同的编程语言实现：

| 服务 | 端口 | 技术栈 | 数据库依赖 |
|------|------|--------|-----------|
| api-gateway | 8080 | Go (Gin) | Redis, RabbitMQ |
| auth-service | 8081 | Go (Gin) | MySQL |
| student-service | 8082 | Python (FastAPI) | PostgreSQL |
| grade-service | 8083 | Python (FastAPI) | PostgreSQL, MongoDB, Redis |
| homework-service | 8084 | Rust (Actix-web) | PostgreSQL |
| exam-service | 8085 | Go (Gin) | PostgreSQL, Redis |
| learning-service | 8086 | Python (FastAPI) | PostgreSQL, MongoDB, Redis |
| communication-service | 8087 | Java/Kotlin (Spring) | MySQL, RabbitMQ |
| admin-service | 8088 | Go (Gin) | PostgreSQL |

## 启动方式

### 方式一：Docker Compose 启动（推荐用于完整环境）

#### 步骤 1：启动基础设施服务

```powershell
# 在项目根目录执行
docker-compose up -d postgres mysql mongodb redis rabbitmq
```

#### 步骤 2：等待服务健康检查通过

```powershell
# 查看服务状态
docker-compose ps
```

#### 步骤 3：启动后端微服务

```powershell
# 启动所有后端服务
docker-compose --profile services up -d
```

### 方式二：本地开发启动（推荐用于开发调试）

#### 步骤 1：启动基础设施服务

```powershell
docker-compose up -d postgres mysql mongodb redis rabbitmq
```

#### 步骤 2：启动各个微服务

**启动 API Gateway (Go)**
```powershell
cd backend/api-gateway
go run cmd/main.go
```

**启动 Auth Service (Go)**
```powershell
cd backend/auth-service
go run cmd/server/main.go
```

**启动 Student Service (Python)**
```powershell
cd backend/student-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

**启动 Grade Service (Python)**
```powershell
cd backend/grade-service
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

**启动 Homework Service (Rust)**
```powershell
cd backend/homework-service
cargo run --release
```

**启动 Exam Service (Go)**
```powershell
cd backend/exam-service
go run cmd/server/main.go
```

**启动 Learning Service (Python)**
```powershell
cd backend/learning-service
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.main
```

**启动 Admin Service (Go)**
```powershell
cd backend/admin-service
go run cmd/server/main.go
```

## 实施步骤

### 阶段一：启动基础设施

1. 检查 Docker Desktop 是否运行
2. 启动 PostgreSQL、MySQL、MongoDB、Redis、RabbitMQ
3. 验证各服务健康状态

### 阶段二：启动核心服务

按依赖顺序启动服务：

1. **auth-service** (8081) - 认证服务，其他服务依赖
2. **api-gateway** (8080) - API 网关，路由请求

### 阶段三：启动业务服务

1. **student-service** (8082)
2. **grade-service** (8083)
3. **homework-service** (8084)
4. **exam-service** (8085)
5. **learning-service** (8086)
6. **admin-service** (8088)

## 验证服务状态

启动后访问以下端点验证：

| 服务 | 健康检查端点 |
|------|-------------|
| api-gateway | http://localhost:8080/health |
| auth-service | http://localhost:8081/health |
| student-service | http://localhost:8082/health |
| grade-service | http://localhost:8083/health |
| homework-service | http://localhost:8084/health |
| exam-service | http://localhost:8085/health |
| learning-service | http://localhost:8086/health |
| admin-service | http://localhost:8088/health |

## 默认凭据

- **PostgreSQL**: openzhixue / openzhixue123
- **MySQL**: root / root123 或 openzhixue / openzhixue123
- **MongoDB**: admin / admin123
- **RabbitMQ**: openzhixue / openzhixue123 (管理界面: http://localhost:15672)
- **Redis**: 无密码

## 注意事项

1. 首次启动需要确保 Docker Desktop 正在运行
2. 端口 5432、3306、27017、6379、5672、8080-8088 需要未被占用
3. 部分服务需要先运行数据库迁移
4. 建议按顺序启动，先启动基础设施，再启动核心服务
