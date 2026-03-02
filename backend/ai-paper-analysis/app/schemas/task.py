"""
任务相关的数据模型
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Any, Dict
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskType(str, Enum):
    """任务类型枚举"""
    DOCUMENT_PARSE = "document_parse"  # 文档解析
    QUESTION_ANALYSIS = "question_analysis"  # 题目分析
    SIMILAR_QUESTION_GENERATION = "similar_question_generation"  # 相似题生成
    FULL_ANALYSIS = "full_analysis"  # 完整分析（解析+分析+生成相似题）


class FileType(str, Enum):
    """文件类型枚举"""
    PDF = "pdf"
    WORD = "word"


class TaskProgress(BaseModel):
    """任务进度模型"""
    current_step: str = Field(..., description="当前步骤描述")
    total_steps: int = Field(..., description="总步骤数")
    current_step_number: int = Field(..., description="当前步骤编号")
    percentage: int = Field(..., ge=0, le=100, description="完成百分比")
    message: Optional[str] = Field(None, description="进度消息")

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    """创建任务请求模型"""
    file_path: str = Field(..., description="文件存储路径")
    file_type: FileType = Field(..., description="文件类型")
    original_filename: str = Field(..., description="原始文件名")
    task_type: TaskType = Field(
        default=TaskType.FULL_ANALYSIS,
        description="任务类型"
    )
    options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="任务选项（如相似题生成数量等）"
    )

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    """任务响应模型"""
    id: UUID = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    task_type: TaskType = Field(..., description="任务类型")
    file_path: str = Field(..., description="文件存储路径")
    file_type: FileType = Field(..., description="文件类型")
    original_filename: str = Field(..., description="原始文件名")
    progress: Optional[TaskProgress] = Field(None, description="任务进度")
    extracted_text: Optional[str] = Field(None, description="提取的文本")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="分析结果")
    similar_questions: Optional[List[Dict[str, Any]]] = Field(None, description="相似题目列表")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    items: List[TaskResponse] = Field(..., description="任务列表")
    total: int = Field(..., description="总数")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")

    model_config = ConfigDict(from_attributes=True)


class TaskCancelResponse(BaseModel):
    """取消任务响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    task_id: UUID = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")

    model_config = ConfigDict(from_attributes=True)


class TaskResultResponse(BaseModel):
    """任务结果响应模型"""
    task_id: UUID = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    extracted_text: Optional[str] = Field(None, description="提取的文本")
    analysis_result: Optional[Dict[str, Any]] = Field(None, description="分析结果")
    similar_questions: Optional[List[Dict[str, Any]]] = Field(None, description="相似题目列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

    model_config = ConfigDict(from_attributes=True)
