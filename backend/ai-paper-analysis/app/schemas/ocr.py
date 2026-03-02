"""
OCR 相关的 Schema 定义
"""

from enum import Enum
from typing import Optional, List, Any
from pydantic import BaseModel, Field


class OCRTaskType(str, Enum):
    """OCR 任务类型"""
    SINGLE = "single"  # 单张图片
    BATCH = "batch"  # 批量图片
    PDF = "pdf"  # PDF 文档


class OCRStatus(str, Enum):
    """OCR 任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OCRRequest(BaseModel):
    """OCR 识别请求"""
    file_path: str = Field(..., description="文件路径（图片或PDF）")
    task_type: OCRTaskType = Field(default=OCRTaskType.SINGLE, description="任务类型")
    prompt: Optional[str] = Field(
        default="<image>\nExtract all text from this image and convert to markdown format.",
        description="OCR 提示词"
    )
    language: Optional[str] = Field(default="ch", description="语言类型 (ch/en)")
    enable_crop: bool = Field(default=True, description="是否启用裁剪模式")
    max_new_tokens: Optional[int] = Field(default=None, description="最大生成 token 数")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/uploads/test.png",
                "task_type": "single",
                "prompt": "<image>\nExtract all text from this image and convert to markdown format.",
                "language": "ch",
                "enable_crop": True
            }
        }


class OCRBatchRequest(BaseModel):
    """批量 OCR 识别请求"""
    file_paths: List[str] = Field(..., description="文件路径列表")
    prompt: Optional[str] = Field(
        default="<image>\nExtract all text from this image and convert to markdown format.",
        description="OCR 提示词"
    )
    language: Optional[str] = Field(default="ch", description="语言类型")
    enable_crop: bool = Field(default=True, description="是否启用裁剪模式")

    class Config:
        json_schema_extra = {
            "example": {
                "file_paths": ["/uploads/test1.png", "/uploads/test2.png"],
                "prompt": "<image>\nExtract all text from this image.",
                "language": "ch",
                "enable_crop": True
            }
        }


class OCRResult(BaseModel):
    """单个 OCR 结果"""
    file_path: str = Field(..., description="文件路径")
    text: str = Field(..., description="识别出的文本")
    page_number: Optional[int] = Field(default=None, description="页码（PDF时有效）")
    confidence: Optional[float] = Field(default=None, description="置信度")
    processing_time: float = Field(..., description="处理时间（秒）")
    success: bool = Field(default=True, description="是否成功")
    error: Optional[str] = Field(default=None, description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/uploads/test.png",
                "text": "# 标题\n这是一段文本内容...",
                "page_number": None,
                "confidence": 0.95,
                "processing_time": 2.5,
                "success": True,
                "error": None
            }
        }


class OCRResponse(BaseModel):
    """OCR 识别响应"""
    task_id: Optional[str] = Field(default=None, description="任务ID")
    status: OCRStatus = Field(..., description="任务状态")
    results: List[OCRResult] = Field(default_factory=list, description="OCR 结果列表")
    total_pages: int = Field(default=0, description="总页数")
    processed_pages: int = Field(default=0, description="已处理页数")
    total_time: float = Field(default=0.0, description="总处理时间（秒）")
    message: Optional[str] = Field(default=None, description="消息")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "ocr_123456",
                "status": "completed",
                "results": [
                    {
                        "file_path": "/uploads/test.png",
                        "text": "# 标题\n这是一段文本内容...",
                        "page_number": 1,
                        "confidence": 0.95,
                        "processing_time": 2.5,
                        "success": True,
                        "error": None
                    }
                ],
                "total_pages": 1,
                "processed_pages": 1,
                "total_time": 2.5,
                "message": "OCR completed successfully"
            }
        }


class OCRStatusResponse(BaseModel):
    """OCR 服务状态响应"""
    service_available: bool = Field(..., description="服务是否可用")
    model_loaded: bool = Field(default=False, description="模型是否已加载")
    device: Optional[str] = Field(default=None, description="运行设备")
    model_path: Optional[str] = Field(default=None, description="模型路径")
    cuda_available: bool = Field(default=False, description="CUDA 是否可用")
    error: Optional[str] = Field(default=None, description="错误信息")
    memory_usage: Optional[Dict[str, Any]] = Field(default=None, description="内存使用情况")

    class Config:
        json_schema_extra = {
            "example": {
                "service_available": True,
                "model_loaded": True,
                "device": "cuda",
                "model_path": "e:/openzhixue/model/deepseek-ocr2",
                "cuda_available": True,
                "error": None,
                "memory_usage": {
                    "gpu_memory_allocated": "4.5 GB",
                    "gpu_memory_reserved": "5.0 GB"
                }
            }
        }


class PDFPageOCRResult(BaseModel):
    """PDF 页面 OCR 结果"""
    page_number: int = Field(..., description="页码")
    text: str = Field(..., description="识别出的文本")
    image_path: Optional[str] = Field(default=None, description="页面图像路径")
    confidence: Optional[float] = Field(default=None, description="置信度")
    processing_time: float = Field(..., description="处理时间（秒）")


class PDFOCRRequest(BaseModel):
    """PDF OCR 识别请求"""
    file_path: str = Field(..., description="PDF 文件路径")
    start_page: Optional[int] = Field(default=None, description="起始页码（从1开始）")
    end_page: Optional[int] = Field(default=None, description="结束页码")
    prompt: Optional[str] = Field(
        default="<image>\nExtract all text from this image and convert to markdown format.",
        description="OCR 提示词"
    )
    enable_crop: bool = Field(default=True, description="是否启用裁剪模式")
    dpi: int = Field(default=200, description="PDF 转图像的 DPI")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/uploads/test.pdf",
                "start_page": 1,
                "end_page": 10,
                "prompt": "<image>\nExtract all text from this image.",
                "enable_crop": True,
                "dpi": 200
            }
        }


class PDFOCRResponse(BaseModel):
    """PDF OCR 识别响应"""
    task_id: Optional[str] = Field(default=None, description="任务ID")
    status: OCRStatus = Field(..., description="任务状态")
    file_path: str = Field(..., description="PDF 文件路径")
    total_pages: int = Field(..., description="总页数")
    processed_pages: int = Field(default=0, description="已处理页数")
    results: List[PDFPageOCRResult] = Field(default_factory=list, description="各页 OCR 结果")
    full_text: Optional[str] = Field(default=None, description="合并后的完整文本")
    total_time: float = Field(default=0.0, description="总处理时间（秒）")
    error: Optional[str] = Field(default=None, description="错误信息")


# 为了兼容性，添加 Dict 类型导入
from typing import Dict
