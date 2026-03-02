# 移除 Docker 配置计划

## 目标
修改项目配置，移除 Docker 相关配置，改为本地直接运行方式。

## 需要修改的文件

### 1. 删除 Docker 相关文件
- 删除所有 Dockerfile 文件（6 个后端服务的 Dockerfile）
- 删除 docker-compose.yml
- 检查并删除 frontend/web 的 Dockerfile（如果存在）

### 2. 修改 CI/CD 配置 (.github/workflows/ci.yml)
- 移除 Docker 构建步骤（build job 中的 docker build 命令）
- 移除 Docker Buildx 和 Docker Hub 登录步骤
- 保留代码检查、测试步骤

### 3. 修改部署脚本
- 修改 infrastructure/scripts/start-dev.sh
  - 移除 docker-compose 命令
  - 改为直接启动各服务的方式（或提供本地开发指南）
- 修改 infrastructure/scripts/stop-dev.sh
  - 移除 docker-compose down 命令

### 4. 更新 README.md
- 移除环境要求中的 Docker 和 Docker Compose
- 修改快速开始章节，移除 docker-compose 相关命令
- 删除 Docker 部署和 Kubernetes 部署章节
- 保留本地开发指南

### 5. 删除基础设施相关目录（可选）
- infrastructure/docker/ - Docker 配置文件
- infrastructure/k8s/ - Kubernetes 配置文件
- infrastructure/monitoring/ - 监控配置（如果不再需要）

## 实施步骤

1. **删除 Docker 文件**
   - 删除所有 Dockerfile
   - 删除 docker-compose.yml

2. **修改 CI/CD 配置**
   - 编辑 .github/workflows/ci.yml，移除 Docker 构建相关步骤

3. **修改部署脚本**
   - 编辑 start-dev.sh，改为本地启动脚本或提供说明
   - 编辑 stop-dev.sh，改为停止本地服务脚本

4. **更新 README.md**
   - 移除 Docker 相关内容
   - 更新快速开始指南

5. **清理基础设施配置**
   - 删除不再需要的基础设施配置文件

## 注意事项
- 保留各服务的本地运行配置（如环境配置文件）
- 确保修改后的配置仍然可以正常开发
- CI/CD 流程仍然可以运行测试和代码检查
