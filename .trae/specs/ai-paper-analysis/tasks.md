# AI试卷分析服务 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 初始化项目结构
- **Priority**: P0
- **Depends On**: None
- **Description**: 
  - 创建 ai-paper-analysis 服务目录结构
  - 配置 pyproject.toml 和 requirements.txt（包含transformers, torch等）
  - 创建基础配置文件（config.py, main.py等）
  - 配置环境变量示例文件 .env.example
- **Acceptance Criteria Addressed**: [None (基础设施)]
- **Test Requirements**:
  - `programmatic` TR-1.1: 项目目录结构完整创建成功
  - `programmatic` TR-1.2: 可以成功安装依赖
  - `programmatic` TR-1.3: FastAPI应用可以启动
  - `human-judgement` TR-1.4: 代码结构与现有Python服务保持一致
- **Notes**: 参考 grade-service 和 learning-service 的结构作为模板

## [x] Task 2: 下载和配置DeepSeek-OCR2模型
- **Priority**: P0
- **Depends On**: Task 1
- **Description**: 
  - 下载DeepSeek-OCR2模型到 ./model/deepseek-ocr2/ 目录
  - 配置模型加载环境
  - 验证模型可以正常加载
- **Acceptance Criteria Addressed**: [FR-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: DeepSeek-OCR2模型下载成功
  - `programmatic` TR-2.2: 模型文件完整
  - `programmatic` TR-2.3: 模型可以成功加载
- **Notes**: 需要足够的磁盘空间和网络连接

## [x] Task 3: 数据库模型和配置
- **Priority**: P0
- **Depends On**: Task 2
- **Description**: 
  - 创建数据库模型（分析任务、题目等）
  - 配置数据库连接（PostgreSQL/MongoDB）
  - 配置Redis用于任务队列和缓存
  - 创建数据库迁移脚本
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: 数据库模型定义完整
  - `programmatic` TR-3.2: 数据库连接配置正确
  - `programmatic` TR-3.3: Redis连接配置正确
  - `programmatic` TR-3.4: 可以成功初始化数据库
- **Notes**: 使用SQLAlchemy 2.0 for PostgreSQL，Motor for MongoDB

## [x] Task 4: 文档上传和存储模块
- **Priority**: P0
- **Depends On**: Task 3
- **Description**: 
  - 实现文件上传API接口
  - 支持PDF和Word文档处理
  - 文件存储（本地或对象存储）
  - 文件验证和错误处理
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-4.1: 可以成功上传PDF文件
  - `programmatic` TR-4.2: 可以成功上传Word文件
  - `programmatic` TR-4.3: 文件正确保存到存储
  - `programmatic` TR-4.4: 无效文件格式返回错误
- **Notes**: 使用 PyPDF2 处理PDF，python-docx 处理Word

## [x] Task 5: DeepSeek-OCR2模型集成（扫描件OCR识别）
- **Priority**: P0
- **Depends On**: Task 4
- **Description**: 
  - 实现DeepSeek-OCR2模型加载模块
  - 实现扫描件PDF的OCR识别功能
  - 支持图片格式文档的OCR识别
  - 错误处理和性能优化
- **Acceptance Criteria Addressed**: [FR-4, AC-8]
- **Test Requirements**:
  - `programmatic` TR-5.1: DeepSeek-OCR2模型加载成功
  - `programmatic` TR-5.2: 扫描件PDF可以正确识别
  - `programmatic` TR-5.3: OCR识别结果准确
  - `programmatic` TR-5.4: 错误处理正确
- **Notes**: 模型路径 ./model/deepseek-ocr2/

## [x] Task 6: 本地Qwen3-0.5B模型加载和集成
- **Priority**: P0
- **Depends On**: Task 5
- **Description**: 
  - 实现模型加载模块（从 ./model/qwen3-0.5b/）
  - 使用Transformers库加载模型
  - 实现题目分析功能
  - 实现相似题生成功能
  - 提示词工程优化
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-6.1: Qwen3-0.5B模型加载成功
  - `programmatic` TR-6.2: 可以分析出题技巧
  - `programmatic` TR-6.3: 可以生成至少3道相似题
  - `programmatic` TR-6.4: 生成的题目包含答案解析
- **Notes**: 使用AutoModelForCausalLM和AutoTokenizer

## [x] Task 7: 异步任务处理
- **Priority**: P0
- **Depends On**: Task 6
- **Description**: 
  - 实现异步任务队列
  - 任务状态管理
  - 任务进度跟踪
  - 后台worker实现
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-7.1: 任务可以异步执行
  - `programmatic` TR-7.2: 可以查询任务状态
  - `programmatic` TR-7.3: 任务状态正确更新
  - `programmatic` TR-7.4: 支持任务失败处理
- **Notes**: 使用Celery或FastAPI BackgroundTasks

## [x] Task 8: RESTful API接口
- **Priority**: P1
- **Depends On**: Task 7
- **Description**: 
  - 创建文件上传API
  - 创建任务状态查询API
  - 创建结果获取API
  - 创建历史记录API
  - API文档和请求/响应Schema
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-8.1: 所有API端点可用
  - `programmatic` TR-8.2: 请求验证正确
  - `programmatic` TR-8.3: API文档完整
  - `programmatic` TR-8.4: 错误响应格式统一
- **Notes**: 使用Pydantic 2.0定义Schema

## [ ] Task 9: 单元测试和集成测试
- **Priority**: P1
- **Depends On**: Task 8
- **Description**: 
  - 编写单元测试
  - 编写集成测试
  - Mock模型推理以加速测试
  - 测试覆盖率目标&gt;80%
- **Acceptance Criteria Addressed**: [NFR-5]
- **Test Requirements**:
  - `programmatic` TR-9.1: 单元测试通过
  - `programmatic` TR-9.2: 集成测试通过
  - `programmatic` TR-9.3: 测试覆盖率&gt;80%
  - `human-judgement` TR-9.4: Mock模型推理正确
- **Notes**: 使用pytest和pytest-asyncio

## [ ] Task 10: CI/CD集成
- **Priority**: P2
- **Depends On**: Task 9
- **Description**: 
  - 更新CI/CD配置
  - 添加新服务到构建流程
  - 添加测试到CI
- **Acceptance Criteria Addressed**: [NFR-4, NFR-5]
- **Test Requirements**:
  - `programmatic` TR-10.1: CI流程可以构建成功
  - `programmatic` TR-10.2: 测试在CI中运行
  - `programmatic` TR-10.3: Lint检查通过
- **Notes**: 更新 .github/workflows/ci.yml

## [ ] Task 11: 文档和部署
- **Priority**: P2
- **Depends On**: Task 10
- **Description**: 
  - 编写服务README
  - 配置部署文档
  - 环境变量说明（包括模型路径配置）
  - 说明DeepSeek-OCR2和Qwen3-0.5B模型配置
- **Acceptance Criteria Addressed**: [human-judgement]
- **Test Requirements**:
  - `human-judgement` TR-11.1: README文档完整
  - `human-judgement` TR-11.2: 部署文档清晰
  - `human-judgement` TR-11.3: 环境变量说明详细
- **Notes**: 参考其他服务的文档格式
