"""
分析相关的数据模型
定义分析请求和响应的数据结构
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from enum import Enum


class AnalysisStatus(str, Enum):
    """分析状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class QuestionType(str, Enum):
    """题目类型枚举"""
    CHOICE = "choice"  # 选择题
    FILL_BLANK = "fill_blank"  # 填空题
    SHORT_ANSWER = "short_answer"  # 简答题
    CALCULATION = "calculation"  # 计算题
    PROOF = "proof"  # 证明题
    APPLICATION = "application"  # 应用题
    UNKNOWN = "unknown"  # 未知类型


class DifficultyLevel(str, Enum):
    """难度等级枚举"""
    EASY = "easy"  # 简单
    MEDIUM = "medium"  # 中等
    HARD = "hard"  # 困难
    UNKNOWN = "unknown"  # 未知


# ============ 请求模型 ============

class AnalysisRequest(BaseModel):
    """
    分析请求基础模型
    用于题目分析请求
    """
    task_id: Optional[UUID] = Field(None, description="任务ID（如果已有解析任务）")
    text: Optional[str] = Field(None, description="待分析的文本内容（如果直接提供文本）")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="分析选项配置"
    )

    model_config = ConfigDict(from_attributes=True)


class ParseRequest(BaseModel):
    """
    文档解析请求模型
    用于上传文件并解析
    """
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="解析选项配置"
    )

    model_config = ConfigDict(from_attributes=True)


class AnalyzeRequest(BaseModel):
    """
    题目分析请求模型
    用于分析已解析的题目
    """
    task_id: UUID = Field(..., description="任务ID")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="分析选项配置"
    )

    model_config = ConfigDict(from_attributes=True)


class GenerateRequest(BaseModel):
    """
    相似题生成请求模型
    用于生成相似题目
    """
    task_id: UUID = Field(..., description="任务ID")
    count: int = Field(default=3, ge=1, le=10, description="生成相似题数量")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="生成选项配置"
    )

    model_config = ConfigDict(from_attributes=True)


class FullAnalysisRequest(BaseModel):
    """
    完整分析流程请求模型
    包含上传、解析、分析、生成的完整流程
    """
    similar_question_count: int = Field(default=3, ge=1, le=10, description="相似题生成数量")
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="分析选项配置"
    )

    model_config = ConfigDict(from_attributes=True)


# ============ 响应模型 ============

class KnowledgePoint(BaseModel):
    """知识点模型"""
    name: str = Field(..., description="知识点名称")
    category: Optional[str] = Field(None, description="知识点分类")
    description: Optional[str] = Field(None, description="知识点描述")
    importance: Optional[int] = Field(None, ge=1, le=5, description="重要程度（1-5）")

    model_config = ConfigDict(from_attributes=True)


class QuestionAnalysis(BaseModel):
    """
    题目分析结果模型
    包含单个题目的详细分析信息
    """
    question_number: Optional[int] = Field(None, description="题目编号")
    question_type: QuestionType = Field(default=QuestionType.UNKNOWN, description="题目类型")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.UNKNOWN, description="难度等级")
    content: Optional[str] = Field(None, description="题目内容")
    answer: Optional[str] = Field(None, description="参考答案")
    analysis: Optional[str] = Field(None, description="题目解析")
    knowledge_points: List[KnowledgePoint] = Field(
        default_factory=list,
        description="相关知识点列表"
    )
    main_knowledge_points: List[str] = Field(
        default_factory=list,
        description="主要知识点名称列表"
    )
    secondary_knowledge_points: List[str] = Field(
        default_factory=list,
        description="次要知识点名称列表"
    )
    estimated_time: Optional[int] = Field(None, description="预估答题时间（分钟）")
    score: Optional[float] = Field(None, description="题目分值")
    tags: List[str] = Field(default_factory=list, description="标签列表")

    model_config = ConfigDict(from_attributes=True)


class SimilarQuestion(BaseModel):
    """
    相似题目模型
    包含生成的相似题目信息
    """
    question_id: Optional[int] = Field(None, description="题目编号")
    content: str = Field(..., description="题目内容")
    answer: Optional[str] = Field(None, description="参考答案")
    analysis: Optional[str] = Field(None, description="题目解析")
    difficulty: DifficultyLevel = Field(default=DifficultyLevel.MEDIUM, description="难度等级")
    knowledge_points: List[str] = Field(default_factory=list, description="涉及知识点")
    similarity_score: Optional[float] = Field(None, ge=0, le=1, description="相似度分数")

    model_config = ConfigDict(from_attributes=True)


class PaperAnalysisResult(BaseModel):
    """
    试卷分析结果模型
    包含整份试卷的分析汇总信息
    """
    total_questions: int = Field(default=0, description="题目总数")
    total_score: Optional[float] = Field(None, description="试卷总分")
    estimated_time: Optional[int] = Field(None, description="预估答题总时间（分钟）")
    question_types_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="题目类型分布"
    )
    difficulty_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="难度分布"
    )
    knowledge_points_summary: List[KnowledgePoint] = Field(
        default_factory=list,
        description="知识点汇总"
    )
    questions: List[QuestionAnalysis] = Field(
        default_factory=list,
        description="各题目详细分析"
    )
    overall_difficulty: Optional[DifficultyLevel] = Field(None, description="整体难度评估")
    suggestions: List[str] = Field(default_factory=list, description="学习建议")

    model_config = ConfigDict(from_attributes=True)


class AnalysisResult(BaseModel):
    """
    分析结果响应模型
    包含完整的分析结果信息
    """
    task_id: UUID = Field(..., description="任务ID")
    status: AnalysisStatus = Field(..., description="分析状态")
    message: Optional[str] = Field(None, description="状态消息")

    # 文档解析结果
    extracted_text: Optional[str] = Field(None, description="提取的文本内容")
    page_count: Optional[int] = Field(None, description="页数")
    word_count: Optional[int] = Field(None, description="字数")

    # 题目分析结果
    paper_analysis: Optional[PaperAnalysisResult] = Field(None, description="试卷分析结果")
    question_analysis: Optional[QuestionAnalysis] = Field(None, description="单题分析结果")

    # 相似题生成结果
    similar_questions: List[SimilarQuestion] = Field(
        default_factory=list,
        description="生成的相似题目列表"
    )

    # 元数据
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    error: Optional[str] = Field(None, description="错误信息")

    # 时间戳
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    model_config = ConfigDict(from_attributes=True)


class ParseResponse(BaseModel):
    """
    文档解析响应模型
    """
    success: bool = Field(..., description="是否成功")
    task_id: UUID = Field(..., description="任务ID")
    message: str = Field(..., description="响应消息")
    extracted_text: Optional[str] = Field(None, description="提取的文本")
    page_count: Optional[int] = Field(None, description="页数")
    word_count: Optional[int] = Field(None, description="字数")
    metadata: Optional[Dict[str, Any]] = Field(None, description="文档元数据")

    model_config = ConfigDict(from_attributes=True)


class AnalyzeResponse(BaseModel):
    """
    题目分析响应模型
    """
    success: bool = Field(..., description="是否成功")
    task_id: UUID = Field(..., description="任务ID")
    message: str = Field(..., description="响应消息")
    analysis: Optional[QuestionAnalysis] = Field(None, description="分析结果")

    model_config = ConfigDict(from_attributes=True)


class GenerateResponse(BaseModel):
    """
    相似题生成响应模型
    """
    success: bool = Field(..., description="是否成功")
    task_id: UUID = Field(..., description="任务ID")
    message: str = Field(..., description="响应消息")
    similar_questions: List[SimilarQuestion] = Field(
        default_factory=list,
        description="生成的相似题目列表"
    )

    model_config = ConfigDict(from_attributes=True)


class FullAnalysisResponse(BaseModel):
    """
    完整分析流程响应模型
    """
    success: bool = Field(..., description="是否成功")
    task_id: UUID = Field(..., description="任务ID")
    message: str = Field(..., description="响应消息")
    status: AnalysisStatus = Field(..., description="分析状态")

    # 解析结果
    extracted_text: Optional[str] = Field(None, description="提取的文本")
    page_count: Optional[int] = Field(None, description="页数")
    word_count: Optional[int] = Field(None, description="字数")

    # 分析结果
    paper_analysis: Optional[PaperAnalysisResult] = Field(None, description="试卷分析结果")

    # 相似题
    similar_questions: List[SimilarQuestion] = Field(
        default_factory=list,
        description="生成的相似题目列表"
    )

    # 元数据
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

    model_config = ConfigDict(from_attributes=True)


class AnalysisListResponse(BaseModel):
    """
    分析结果列表响应模型
    """
    items: List[AnalysisResult] = Field(..., description="分析结果列表")
    total: int = Field(..., description="总数")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

    model_config = ConfigDict(from_attributes=True)
