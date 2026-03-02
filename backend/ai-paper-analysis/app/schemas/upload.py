"""
文件上传相关的数据模型
"""

from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum


class UploadStatus(str, Enum):
    """上传状态枚举"""
    PENDING = "pending"  # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class FileInfo(BaseModel):
    """文件信息模型"""
    file_id: UUID = Field(..., description="文件唯一ID")
    original_filename: str = Field(..., description="原始文件名")
    stored_filename: str = Field(..., description="存储的文件名")
    file_path: str = Field(..., description="文件存储路径")
    relative_path: str = Field(..., description="相对路径")
    file_size: int = Field(..., description="文件大小（字节）")
    file_hash: str = Field(..., description="文件SHA256哈希值")
    content_type: Optional[str] = Field(None, description="文件Content-Type")
    extension: str = Field(..., description="文件扩展名")
    upload_time: datetime = Field(..., description="上传时间")

    model_config = ConfigDict(from_attributes=True)


class UploadResponse(BaseModel):
    """上传响应模型"""
    success: bool = Field(..., description="上传是否成功")
    message: str = Field(..., description="响应消息")
    task_id: UUID = Field(..., description="任务ID，用于查询上传状态")
    file_info: Optional[FileInfo] = Field(None, description="文件信息")
    status: UploadStatus = Field(default=UploadStatus.PENDING, description="上传状态")

    model_config = ConfigDict(from_attributes=True)


class UploadStatusResponse(BaseModel):
    """上传状态查询响应模型"""
    task_id: UUID = Field(..., description="任务ID")
    status: UploadStatus = Field(..., description="上传状态")
    message: str = Field(..., description="状态消息")
    file_info: Optional[FileInfo] = Field(None, description="文件信息（如果已完成）")
    error: Optional[str] = Field(None, description="错误信息（如果失败）")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class UploadListResponse(BaseModel):
    """上传列表响应模型"""
    items: List[UploadStatusResponse] = Field(..., description="上传任务列表")
    total: int = Field(..., description="总数")
    page: int = Field(default=1, ge=1, description="当前页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class DocumentParseResult(BaseModel):
    """文档解析结果模型"""
    success: bool = Field(..., description="解析是否成功")
    text: Optional[str] = Field(None, description="提取的文本内容")
    page_count: int = Field(default=0, description="页数")
    word_count: int = Field(default=0, description="字数")
    metadata: dict = Field(default_factory=dict, description="文档元数据")
    error: Optional[str] = Field(None, description="错误信息")

    model_config = ConfigDict(from_attributes=True)


class UploadTaskCreate(BaseModel):
    """创建上传任务的请求模型"""
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., ge=1, description="文件大小（字节）")
    content_type: Optional[str] = Field(None, description="文件Content-Type")
    file_hash: Optional[str] = Field(None, description="文件哈希值（用于去重）")


class UploadTaskInfo(BaseModel):
    """上传任务信息模型"""
    id: UUID = Field(..., description="任务ID")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小")
    status: UploadStatus = Field(..., description="任务状态")
    file_path: Optional[str] = Field(None, description="文件路径")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)
