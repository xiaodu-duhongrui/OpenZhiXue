# 管理员系统完善计划

## 一、项目背景

基于现有的 OpenZhixue 教育管理平台，完善学生管理、教师管理功能，创建完整的管理员系统，支持：
- 创建/删除学生、家长、教师账号
- 通过 xlsx 表格批量导入注册

## 二、现状分析

### 已有功能
| 模块 | 状态 | 说明 |
|------|------|------|
| 学生管理 | ✅ 基本完成 | student-service 提供 CRUD API |
| 班级管理 | ✅ 基本完成 | class_router.py |
| 权限系统 | ✅ 完成 | RBAC 模型，支持 4 种角色 |
| 认证服务 | ✅ 完成 | auth-service (Go) |

### 待实现功能
| 模块 | 状态 | 说明 |
|------|------|------|
| 教师模型 | ❌ 缺失 | 无独立 Teacher 模型 |
| 教师服务 | ❌ 缺失 | 无 teacher-service |
| 家长模型 | ❌ 缺失 | 无独立 Parent 模型 |
| 家长服务 | ❌ 缺失 | 无 parent-service |
| 管理员前端 | ❌ 缺失 | 无管理后台界面 |
| 批量导入 | ❌ 缺失 | 无 xlsx 导入功能 |

## 三、技术方案

### 3.1 后端方案

#### 教师服务 (teacher-service)
- **技术栈**: Python FastAPI (与 student-service 保持一致)
- **数据库**: MySQL
- **端口**: 8004

#### 家长服务 (parent-service)
- **技术栈**: Python FastAPI
- **数据库**: MySQL
- **端口**: 8005

#### 批量导入服务
- 集成到 auth-service 中
- 使用 Python openpyxl 库处理 xlsx 文件
- 支持异步任务处理大批量导入

### 3.2 前端方案

#### 管理员 Web 界面
- **技术栈**: Next.js 14 (与现有 Web 前端一致)
- **路由**: `/admin/*`
- **主要页面**:
  - 仪表盘 `/admin/dashboard`
  - 学生管理 `/admin/students`
  - 教师管理 `/admin/teachers`
  - 家长管理 `/admin/parents`
  - 账号管理 `/admin/accounts`
  - 批量导入 `/admin/import`

## 四、详细实施步骤

### 第一阶段：后端模型和服务

#### 4.1 创建教师服务 (teacher-service)

**步骤 4.1.1**: 创建项目结构
```
backend/teacher-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── teacher.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── teacher_schema.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── teacher_router.py
│   └── services/
│       ├── __init__.py
│       └── teacher_service.py
├── requirements.txt
└── Dockerfile
```

**步骤 4.1.2**: 定义教师模型
```python
class Teacher(Base):
    __tablename__ = "teachers"
    
    id: int                    # 主键
    teacher_no: str            # 工号 (唯一)
    name: str                  # 姓名
    gender: Gender             # 性别
    birth_date: date           # 出生日期
    phone: str                 # 联系电话
    email: str                 # 邮箱
    subject: str               # 任教科目
    title: TeacherTitle        # 职称
    status: TeacherStatus      # 状态
    user_id: int               # 关联用户ID
    created_at: datetime
    updated_at: datetime
```

**步骤 4.1.3**: 实现教师 API
- `GET /teachers` - 获取教师列表
- `GET /teachers/{id}` - 获取教师详情
- `POST /teachers` - 创建教师
- `PUT /teachers/{id}` - 更新教师
- `DELETE /teachers/{id}` - 删除教师
- `POST /teachers/import` - 批量导入教师

#### 4.2 创建家长服务 (parent-service)

**步骤 4.2.1**: 创建项目结构
```
backend/parent-service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── parent.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── parent_schema.py
│   ├── routers/
│   │   ├── __init__.py
│   │   └── parent_router.py
│   └── services/
│       ├── __init__.py
│       └── parent_service.py
├── requirements.txt
└── Dockerfile
```

**步骤 4.2.2**: 定义家长模型
```python
class Parent(Base):
    __tablename__ = "parents"
    
    id: int                    # 主键
    name: str                  # 姓名
    gender: Gender             # 性别
    phone: str                 # 联系电话
    email: str                 # 邮箱
    relationship: Relationship # 与学生关系
    status: ParentStatus       # 状态
    user_id: int               # 关联用户ID
    created_at: datetime
    updated_at: datetime

class ParentChildRelation(Base):
    __tablename__ = "parent_child_relations"
    
    id: int
    parent_id: int             # 家长ID
    student_id: int            # 学生ID
    relationship: Relationship # 关系
    is_primary: bool           # 是否主要联系人
```

**步骤 4.2.3**: 实现家长 API
- `GET /parents` - 获取家长列表
- `GET /parents/{id}` - 获取家长详情
- `POST /parents` - 创建家长
- `PUT /parents/{id}` - 更新家长
- `DELETE /parents/{id}` - 删除家长
- `POST /parents/bind-child` - 绑定学生
- `DELETE /parents/unbind-child` - 解绑学生
- `POST /parents/import` - 批量导入家长

#### 4.3 扩展认证服务

**步骤 4.3.1**: 添加批量注册 API
- `POST /auth/batch-register` - 批量注册用户
- `POST /auth/import-users` - 从 xlsx 导入用户

**步骤 4.3.2**: 添加管理员专用 API
- `GET /admin/users` - 获取所有用户列表
- `DELETE /admin/users/{id}` - 删除用户
- `PUT /admin/users/{id}/status` - 修改用户状态
- `POST /admin/users/{id}/reset-password` - 重置密码

#### 4.4 更新 API 网关

**步骤 4.4.1**: 添加新服务路由
```go
// 添加教师服务路由
teacherProxy := proxy.NewServiceProxy("teacher-service", cfg.TeacherServiceURL)
api.Group("/teachers").Use(middleware.AuthMiddleware()).Route("", teacherProxy)

// 添加家长服务路由
parentProxy := proxy.NewServiceProxy("parent-service", cfg.ParentServiceURL)
api.Group("/parents").Use(middleware.AuthMiddleware()).Route("", parentProxy)

// 添加管理员路由
adminGroup := api.Group("/admin")
adminGroup.Use(middleware.RequireAdmin())
```

### 第二阶段：前端管理员界面

#### 4.5 创建管理员页面结构

**步骤 4.5.1**: 创建目录结构
```
frontend/web/src/app/admin/
├── layout.tsx
├── dashboard/
│   └── page.tsx
├── students/
│   ├── page.tsx
│   ├── [id]/
│   │   └── page.tsx
│   └── components/
│       ├── StudentList.tsx
│       ├── StudentForm.tsx
│       └── StudentImport.tsx
├── teachers/
│   ├── page.tsx
│   ├── [id]/
│   │   └── page.tsx
│   └── components/
│       ├── TeacherList.tsx
│       ├── TeacherForm.tsx
│       └── TeacherImport.tsx
├── parents/
│   ├── page.tsx
│   ├── [id]/
│   │   └── page.tsx
│   └── components/
│       ├── ParentList.tsx
│       ├── ParentForm.tsx
│       └── ParentImport.tsx
├── accounts/
│   ├── page.tsx
│   └── components/
│       ├── AccountList.tsx
│       └── AccountForm.tsx
└── import/
    └── page.tsx
```

**步骤 4.5.2**: 创建管理员布局组件
- 侧边栏导航
- 顶部导航栏
- 权限检查中间件

#### 4.6 实现学生管理页面

**步骤 4.6.1**: 学生列表页面
- 表格展示学生信息
- 搜索、筛选功能
- 分页功能
- 批量操作

**步骤 4.6.2**: 学生创建/编辑表单
- 基本信息表单
- 表单验证
- 关联班级选择
- 关联家长选择

**步骤 4.6.3**: 学生批量导入
- xlsx 文件上传
- 数据预览
- 导入进度显示
- 错误报告

#### 4.7 实现教师管理页面

**步骤 4.7.1**: 教师列表页面
- 表格展示教师信息
- 搜索、筛选功能
- 分页功能

**步骤 4.7.2**: 教师创建/编辑表单
- 基本信息表单
- 任教科目选择
- 职称选择

**步骤 4.7.3**: 教师批量导入
- xlsx 文件上传
- 数据预览和验证

#### 4.8 实现家长管理页面

**步骤 4.8.1**: 家长列表页面
- 表格展示家长信息
- 显示关联学生
- 搜索、筛选功能

**步骤 4.8.2**: 家长创建/编辑表单
- 基本信息表单
- 子女绑定功能

**步骤 4.8.3**: 家长批量导入
- xlsx 文件上传
- 学生关系匹配

#### 4.9 实现账号管理页面

**步骤 4.9.1**: 账号列表页面
- 显示所有用户账号
- 按角色筛选
- 状态管理

**步骤 4.9.2**: 账号操作
- 创建账号（选择角色）
- 删除账号
- 重置密码
- 启用/禁用账号

#### 4.10 实现批量导入页面

**步骤 4.10.1**: 统一导入界面
- 选择导入类型（学生/教师/家长）
- 模板下载
- 文件上传
- 数据预览
- 导入执行
- 结果展示

### 第三阶段：集成和测试

#### 4.11 数据库迁移

**步骤 4.11.1**: 创建迁移脚本
- 创建 teachers 表
- 创建 parents 表
- 创建 parent_child_relations 表
- 添加必要索引

#### 4.12 Docker 配置更新

**步骤 4.12.1**: 更新 docker-compose.yml
- 添加 teacher-service
- 添加 parent-service
- 配置服务依赖

#### 4.13 测试

**步骤 4.13.1**: 单元测试
- 教师服务测试
- 家长服务测试
- 批量导入测试

**步骤 4.13.2**: 集成测试
- API 集成测试
- 前端 E2E 测试

## 五、xlsx 导入模板设计

### 5.1 学生导入模板
| 学号* | 姓名* | 性别* | 出生日期 | 班级名称 | 家长姓名 | 家长电话 | 家长关系 |
|-------|-------|-------|----------|----------|----------|----------|----------|
| 2024001 | 张三 | 男 | 2010-01-15 | 一年级1班 | 张父 | 13800138000 | 父亲 |

### 5.2 教师导入模板
| 工号* | 姓名* | 性别* | 出生日期 | 电话 | 邮箱 | 任教科目 | 职称 |
|-------|-------|-------|----------|------|------|----------|------|
| T001 | 李老师 | 女 | 1985-05-20 | 13900139000 | li@school.com | 数学 | 高级教师 |

### 5.3 家长导入模板
| 姓名* | 性别* | 电话* | 邮箱 | 学生学号 | 与学生关系 | 是否主要联系人 |
|-------|-------|-------|------|----------|------------|----------------|
| 王父 | 男 | 13700137000 | wang@family.com | 2024001 | 父亲 | 是 |

## 六、实施优先级

| 优先级 | 任务 | 预计工作量 |
|--------|------|------------|
| P0 | 创建教师服务和模型 | 高 |
| P0 | 创建家长服务和模型 | 高 |
| P1 | 扩展认证服务（批量注册API） | 中 |
| P1 | 更新API网关路由 | 低 |
| P1 | 管理员前端布局和权限 | 中 |
| P2 | 学生管理页面完善 | 中 |
| P2 | 教师管理页面 | 中 |
| P2 | 家长管理页面 | 中 |
| P2 | 账号管理页面 | 中 |
| P3 | 批量导入功能 | 高 |
| P3 | Docker配置更新 | 低 |
| P3 | 测试 | 中 |

## 七、API 接口清单

### 7.1 教师服务 API
```
GET    /api/v1/teachers              # 获取教师列表
GET    /api/v1/teachers/{id}         # 获取教师详情
POST   /api/v1/teachers              # 创建教师
PUT    /api/v1/teachers/{id}         # 更新教师
DELETE /api/v1/teachers/{id}         # 删除教师
POST   /api/v1/teachers/import       # 批量导入教师
GET    /api/v1/teachers/template     # 下载导入模板
```

### 7.2 家长服务 API
```
GET    /api/v1/parents               # 获取家长列表
GET    /api/v1/parents/{id}          # 获取家长详情
POST   /api/v1/parents               # 创建家长
PUT    /api/v1/parents/{id}          # 更新家长
DELETE /api/v1/parents/{id}          # 删除家长
POST   /api/v1/parents/bind-child    # 绑定学生
DELETE /api/v1/parents/unbind-child  # 解绑学生
POST   /api/v1/parents/import        # 批量导入家长
GET    /api/v1/parents/template      # 下载导入模板
```

### 7.3 管理员 API
```
GET    /api/v1/admin/users           # 获取用户列表
DELETE /api/v1/admin/users/{id}      # 删除用户
PUT    /api/v1/admin/users/{id}/status    # 修改用户状态
POST   /api/v1/admin/users/{id}/reset-password  # 重置密码
POST   /api/v1/admin/import/students  # 批量导入学生
POST   /api/v1/admin/import/teachers  # 批量导入教师
POST   /api/v1/admin/import/parents   # 批量导入家长
```

## 八、风险和注意事项

1. **数据一致性**: 创建教师/家长时需要同步创建用户账号，需要保证事务一致性
2. **权限控制**: 管理员功能需要严格的权限验证
3. **批量导入性能**: 大批量导入需要异步处理，避免阻塞
4. **数据验证**: xlsx 导入需要严格的数据验证和错误提示
5. **密码安全**: 批量创建账号时需要生成随机密码并安全传递
