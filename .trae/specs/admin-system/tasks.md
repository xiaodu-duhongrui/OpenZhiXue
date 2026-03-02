# Tasks

- [ ] Task 1: 开发管理员服务 (Go)
  - [ ] SubTask 1.1: 创建 Go 项目结构
  - [ ] SubTask 1.2: 实现管理员认证中间件
  - [ ] SubTask 1.3: 实现用户 CRUD API
  - [ ] SubTask 1.4: 实现 xlsx 批量导入 API
  - [ ] SubTask 1.5: 实现操作日志记录

- [ ] Task 2: 开发加密服务
  - [ ] SubTask 2.1: 实现 SHA256 哈希工具
  - [ ] SubTask 2.2: 实现 AES-256 加密解密
  - [ ] SubTask 2.3: 实现 RSA 签名验证
  - [ ] SubTask 2.4: 实现复合加密算法
  - [ ] SubTask 2.5: 创建加密服务 API

- [ ] Task 3: 开发管理后台 Web UI
  - [ ] SubTask 3.1: 创建管理员布局和路由
  - [ ] SubTask 3.2: 实现用户列表页面
  - [ ] SubTask 3.3: 实现用户创建/编辑页面
  - [ ] SubTask 3.4: 实现批量导入页面
  - [ ] SubTask 3.5: 实现操作日志页面

- [x] Task 4: 替换模拟数据
  - [x] SubTask 4.1: 创建 API 服务层
  - [x] SubTask 4.2: 替换学生端模拟数据
  - [x] SubTask 4.3: 替换家长端模拟数据
  - [x] SubTask 4.4: 替换教师端模拟数据
  - [ ] SubTask 4.5: 实现数据加密存储

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 1]
- [Task 4] depends on [Task 1, Task 2]
