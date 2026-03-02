# AI试卷分析服务 - Product Requirement Document

## Overview
- **Summary**: 开发一个基于AI的试卷分析后端服务，使用Python和FastAPI框架。该服务支持PDF/Word试卷文档的解析，使用本地Qwen3-0.5B模型分析出题技巧并生成相似题目。扫描件OCR识别将在DeepSeek-OCR2模型下载后实现。
- **Purpose**: 为教师和学生提供智能试卷分析和题目生成能力，提升教学效率和学习效果。
- **Target Users**: 教师、学生、教育工作者

## Goals
- 实现PDF和Word文档的解析功能
- 集成本地Qwen3-0.5B模型进行题目分析和相似题生成
- 预留DeepSeek-OCR2模型集成接口（待模型下载后实现）
- 提供RESTful API供前端调用
- 遵循现有项目的架构模式和代码规范
- 实现扫描件OCR识别

## Non-Goals (Out of Scope)
- 不实现前端UI界面
- 不涉及用户认证和权限管理（复用现有系统）
- 不实现大规模分布式训练
- 不处理非试卷类文档


## Background & Context
- 项目采用微服务架构，已有多个Python服务（grade-service, learning-service）使用FastAPI
- 现有服务使用PostgreSQL、MongoDB、Redis等组件
- 新增服务将遵循相同的技术栈和架构模式
- Qwen3-0.5B模型已在本地 ./model/qwen3-0.5b/ 目录
- DeepSeek-OCR2模型要求自己下载

## Functional Requirements
- **FR-1**: 下载DEEPSEEK-OCR2模型并配置环境
- **FR-1**: 支持上传PDF文档进行解析
- **FR-2**: 支持上传Word文档进行解析
- **FR-3**: 使用本地Qwen3-0.5B分析试卷的出题技巧
- **FR-4**: 支持扫描件OCR识别
- **FR-4**: 根据分析结果生成相似题目
- **FR-5**: 提供任务状态查询接口（支持异步处理）
- **FR-6**: 存储分析结果和生成的题目


## Non-Functional Requirements
- **NFR-1**: 文档解析响应时间不超过60秒（取决于文档大小）
- **NFR-2**: API接口响应时间不超过2秒（不含AI处理时间）
- **NFR-3**: 支持至少10个并发任务
- **NFR-4**: 代码遵循PEP 8规范
- **NFR-5**: 包含完整的单元测试和集成测试

## Constraints
- **Technical**: 
  - 使用Python 3.11+
  - 使用FastAPI框架
  - 使用异步编程（async/await）
  - 集成现有数据库（PostgreSQL/MongoDB/Redis）
  - 使用本地Qwen3-0.5B模型
- **Business**: 
  - 遵循OpenZhixue的代码规范
  - 扫描件OCR功能待DeepSeek-OCR2下载后实现
- **Dependencies**: 
  - PyPDF2/python-docx等文档处理库
  - Transformers库（用于加载本地Qwen模型）
  - PyTorch（用于模型推理）

## Assumptions
- 本地Qwen3-0.5B模型文件完整可用
- 服务器有足够的内存和GPU资源运行模型推理
- 现有数据库服务可用
- 前端会处理用户认证和文件上传UI

## Acceptance Criteria

### AC-1: PDF文档解析
- **Given**: 系统运行正常且Qwen模型已加载
- **When**: 用户上传一个PDF试卷文档
- **Then**: 系统接受文件并返回任务ID
- **Verification**: `programmatic`

### AC-2: Word文档解析
- **Given**: 系统运行正常且Qwen模型已加载
- **When**: 用户上传一个Word试卷文档
- **Then**: 系统接受文件并返回任务ID
- **Verification**: `programmatic`

### AC-3: 题目分析
- **Given**: 文档文本已成功提取
- **When**: 系统进行题目分析
- **Then**: 本地Qwen3-0.5B分析出题技巧并返回分析结果
- **Verification**: `programmatic`

### AC-4: 相似题生成
- **Given**: 题目分析已完成
- **When**: 系统生成相似题目
- **Then**: 返回至少3道相似题目及答案解析
- **Verification**: `programmatic`

### AC-5: 任务状态查询
- **Given**: 用户拥有有效的任务ID
- **When**: 用户查询任务状态
- **Then**: 返回任务当前状态（pending/processing/completed/failed）和结果
- **Verification**: `programmatic`

### AC-6: 结果存储
- **Given**: 分析任务已完成
- **When**: 系统保存结果
- **Then**: 分析结果和生成的题目持久化到数据库
- **Verification**: `programmatic`

### AC-7: 错误处理
- **Given**: 处理过程中发生错误（如模型加载失败）
- **When**: 错误发生
- **Then**: 系统记录错误日志并返回友好的错误信息
- **Verification**: `programmatic`

### AC-8: OCR预留接口
- **Given**: DeepSeek-OCR2模型尚未下载
- **When**: 系统初始化
- **Then**: OCR接口已预留且文档说明清楚
- **Verification**: `human-judgement`

## Open Questions
- [ ] DeepSeek-OCR2模型什么时候下载？
- [ ] 是否需要支持其他文档格式（如图片格式）？
- [ ] 生成的相似题目数量是否可配置？
- [ ] 是否需要题目分类和标签功能？
