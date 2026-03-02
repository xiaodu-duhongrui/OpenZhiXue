# 管理员系统与加密服务 Spec

## Why
需要一个管理员系统来管理学生、家长、教师账号，支持批量导入注册。同时需要开发加密服务保护敏感数据。

## What Changes
- 新增管理员服务 (Go)，独立端口部署
- 实现用户管理 API（创建、删除、查询）
- 实现 xlsx 批量导入功能
- 开发复合加密算法（AES-256 + RSA + SHA256）
- 替换所有模拟数据为真实 API 调用

## Impact
- Affected specs: 用户认证服务、Web UI
- Affected code: backend/admin-service, frontend/web

## ADDED Requirements

### Requirement: 管理员服务
系统 SHALL 提供独立的管理员服务，运行在独立端口。

#### Scenario: 服务部署
- **WHEN** 管理员服务启动
- **THEN** 服务监听独立端口（默认 8081）

#### Scenario: 管理员认证
- **WHEN** 管理员登录
- **THEN** 系统验证管理员身份并返回管理权限 Token

### Requirement: 用户管理 API
系统 SHALL 提供完整的用户管理功能。

#### Scenario: 创建用户
- **WHEN** 管理员创建新用户
- **THEN** 系统验证数据、加密密码、创建账号

#### Scenario: 删除用户
- **WHEN** 管理员删除用户
- **THEN** 系统软删除用户并记录操作日志

#### Scenario: 批量导入
- **WHEN** 管理员上传 xlsx 文件
- **THEN** 系统解析文件、验证数据、批量创建用户

### Requirement: 复合加密算法
系统 SHALL 提供复合加密服务保护敏感数据。

#### Scenario: 数据加密
- **WHEN** 需要加密敏感数据
- **THEN** 系统使用 SHA256 哈希 + AES-256 加密 + RSA 签名

#### Scenario: 数据解密
- **WHEN** 需要解密数据
- **THEN** 系统验证 RSA 签名 + AES-256 解密 + 验证 SHA256

### Requirement: Web UI 管理后台
系统 SHALL 提供管理员 Web 界面。

#### Scenario: 用户管理页面
- **WHEN** 管理员访问用户管理
- **THEN** 显示用户列表、支持搜索筛选、支持创建删除

#### Scenario: 批量导入页面
- **WHEN** 管理员访问导入页面
- **THEN** 提供文件上传、预览数据、确认导入功能

## MODIFIED Requirements
无

## REMOVED Requirements
无
