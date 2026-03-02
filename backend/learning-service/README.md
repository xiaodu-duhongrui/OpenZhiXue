# Learning Service

在线学习服务 - 提供课程管理、视频点播、学习进度追踪等功能。

## 功能特性

- 课程管理：创建、更新、删除课程，管理章节和课时
- 视频点播：视频播放地址获取，防盗链签名
- 学习进度追踪：记录学习进度，统计学习时长
- 学习报告：生成学习报告，数据分析

## 技术栈

- Python 3.11+
- FastAPI
- SQLAlchemy (async)
- PostgreSQL
- Redis
- MinIO

## 项目结构

```
learning-service/
├── app/
│   ├── __init__.py
│   ├── main.py           # 应用入口
│   ├── config.py         # 配置管理
│   ├── database.py       # 数据库连接
│   ├── models/           # 数据模型
│   │   ├── __init__.py
│   │   └── course.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── __init__.py
│   │   └── course.py
│   ├── routers/          # API 路由
│   │   ├── __init__.py
│   │   ├── courses.py
│   │   ├── lessons.py
│   │   ├── students.py
│   │   └── reports.py
│   ├── services/         # 业务逻辑
│   │   ├── __init__.py
│   │   ├── course_service.py
│   │   ├── learning_service.py
│   │   └── report_service.py
│   └── utils/            # 工具类
│       ├── __init__.py
│       ├── auth.py
│       ├── logger.py
│       ├── redis_client.py
│       └── storage.py
├── tests/                # 测试文件
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_courses.py
│   ├── test_learning.py
│   └── test_reports.py
├── alembic/              # 数据库迁移
│   ├── __init__.py
│   ├── env.py
│   └── versions/
│       └── 001_init.py
├── alembic.ini
├── Dockerfile
└── requirements.txt
```

## API 端点

### 课程管理

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/v1/courses | 创建课程 |
| GET | /api/v1/courses | 获取课程列表 |
| GET | /api/v1/courses/{id} | 获取课程详情 |
| PUT | /api/v1/courses/{id} | 更新课程 |
| DELETE | /api/v1/courses/{id} | 删除课程 |
| POST | /api/v1/courses/{id}/chapters | 添加章节 |
| POST | /api/v1/courses/chapters/{id}/lessons | 添加课时 |

### 视频点播

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/lessons/{id}/video | 获取视频播放地址 |
| POST | /api/v1/lessons/{id}/progress | 更新播放进度 |
| GET | /api/v1/lessons/{id}/progress | 获取播放进度 |
| POST | /api/v1/lessons/{id}/complete | 完成课时 |

### 学习进度

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/students/{id}/progress | 获取学习进度 |
| GET | /api/v1/students/{id}/courses/{courseId}/progress | 获取课程学习进度 |

### 学习报告

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/v1/students/{id}/reports | 获取学习报告 |
| POST | /api/v1/reports/generate | 生成学习报告 |
| GET | /api/v1/reports/analysis/{studentId} | 学习数据分析 |

## 开发

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行服务

```bash
uvicorn app.main:app --reload --port 8000
```

### 运行测试

```bash
pytest
```

### 数据库迁移

```bash
alembic upgrade head
```

## 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | postgresql+asyncpg://... |
| REDIS_URL | Redis连接URL | redis://localhost:6379/0 |
| JWT_SECRET | JWT密钥 | - |
| MINIO_ENDPOINT | MinIO端点 | localhost:9000 |
