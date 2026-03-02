"""
文件上传路由
提供文件上传和状态查询接口
"""

import logging
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse

from app.services.storage_service import storage_service
from app.services.document_service import document_service, DocumentParseError
from app.schemas.upload import (
    UploadResponse,
    UploadStatus,
    UploadStatusResponse,
    FileInfo,
    DocumentParseResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["upload"])

# 内存中存储上传任务状态（生产环境应使用Redis或数据库）
upload_tasks: Dict[UUID, dict] = {}


def _get_task_or_404(task_id: UUID) -> dict:
    """获取任务或返回404错误"""
    if task_id not in upload_tasks:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")
    return upload_tasks[task_id]


@router.post("", response_model=UploadResponse, status_code=201)
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件（PDF或Word文档）")
):
    """
    上传文件接口

    支持的文件类型：
    - PDF文档 (.pdf)
    - Word文档 (.doc, .docx)

    文件大小限制：50MB

    返回任务ID，可用于查询上传状态
    """
    task_id = uuid4()
    now = datetime.now()

    # 初始化任务状态
    upload_tasks[task_id] = {
        "task_id": task_id,
        "status": UploadStatus.PENDING,
        "message": "文件上传中...",
        "file_info": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
    }

    try:
        # 更新状态为处理中
        upload_tasks[task_id]["status"] = UploadStatus.PROCESSING
        upload_tasks[task_id]["message"] = "正在处理文件..."

        # 保存文件
        file_info_dict = await storage_service.save_file(file)

        # 创建FileInfo对象
        file_info = FileInfo(**file_info_dict)

        # 更新任务状态为完成
        upload_tasks[task_id]["status"] = UploadStatus.COMPLETED
        upload_tasks[task_id]["message"] = "文件上传成功"
        upload_tasks[task_id]["file_info"] = file_info
        upload_tasks[task_id]["updated_at"] = datetime.now()

        logger.info(f"File uploaded successfully: task_id={task_id}, filename={file.filename}")

        return UploadResponse(
            success=True,
            message="文件上传成功",
            task_id=task_id,
            file_info=file_info,
            status=UploadStatus.COMPLETED,
        )

    except HTTPException as e:
        # 文件验证错误
        upload_tasks[task_id]["status"] = UploadStatus.FAILED
        upload_tasks[task_id]["message"] = f"文件上传失败: {e.detail}"
        upload_tasks[task_id]["error"] = e.detail
        upload_tasks[task_id]["updated_at"] = datetime.now()

        logger.error(f"File upload failed: task_id={task_id}, error={e.detail}")
        raise

    except Exception as e:
        # 其他错误
        error_msg = f"文件上传失败: {str(e)}"
        upload_tasks[task_id]["status"] = UploadStatus.FAILED
        upload_tasks[task_id]["message"] = error_msg
        upload_tasks[task_id]["error"] = error_msg
        upload_tasks[task_id]["updated_at"] = datetime.now()

        logger.error(f"File upload failed: task_id={task_id}, error={str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)


@router.get("/{task_id}", response_model=UploadStatusResponse)
async def get_upload_status(task_id: UUID):
    """
    查询上传状态

    通过任务ID查询文件上传的处理状态

    返回：
    - 任务状态（pending/processing/completed/failed）
    - 文件信息（如果已完成）
    - 错误信息（如果失败）
    """
    task = _get_task_or_404(task_id)

    return UploadStatusResponse(
        task_id=task["task_id"],
        status=task["status"],
        message=task["message"],
        file_info=task.get("file_info"),
        error=task.get("error"),
        created_at=task["created_at"],
        updated_at=task["updated_at"],
    )


@router.post("/{task_id}/parse", response_model=DocumentParseResult)
async def parse_uploaded_document(task_id: UUID):
    """
    解析已上传的文档

    对已上传的文档进行文本提取

    支持：
    - PDF文档文本提取
    - Word文档文本提取
    """
    task = _get_task_or_404(task_id)

    if task["status"] != UploadStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"任务未完成，当前状态: {task['status']}"
        )

    file_info = task.get("file_info")
    if not file_info:
        raise HTTPException(status_code=404, detail="文件信息不存在")

    try:
        # 解析文档
        result = await document_service.parse_document(file_info.file_path)

        return DocumentParseResult(**result)

    except DocumentParseError as e:
        logger.error(f"Document parse failed: task_id={task_id}, error={str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Document parse failed: task_id={task_id}, error={str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"文档解析失败: {str(e)}")


@router.delete("/{task_id}")
async def delete_uploaded_file(task_id: UUID):
    """
    删除已上传的文件

    删除任务记录和对应的文件
    """
    task = _get_task_or_404(task_id)

    # 删除文件
    file_info = task.get("file_info")
    if file_info:
        try:
            storage_service.delete_file(file_info.relative_path)
            logger.info(f"File deleted: {file_info.relative_path}")
        except Exception as e:
            logger.warning(f"Failed to delete file: {e}")

    # 删除任务记录
    del upload_tasks[task_id]

    return {"success": True, "message": "文件已删除"}


@router.get("", response_model=dict)
async def list_uploads(
    status: Optional[UploadStatus] = Query(None, description="按状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取上传任务列表

    可选按状态筛选
    """
    # 筛选任务
    filtered_tasks = list(upload_tasks.values())
    if status:
        filtered_tasks = [t for t in filtered_tasks if t["status"] == status]

    # 排序（按创建时间倒序）
    filtered_tasks.sort(key=lambda x: x["created_at"], reverse=True)

    # 分页
    total = len(filtered_tasks)
    start = (page - 1) * page_size
    end = start + page_size
    page_tasks = filtered_tasks[start:end]

    # 构建响应
    items = [
        UploadStatusResponse(
            task_id=t["task_id"],
            status=t["status"],
            message=t["message"],
            file_info=t.get("file_info"),
            error=t.get("error"),
            created_at=t["created_at"],
            updated_at=t["updated_at"],
        )
        for t in page_tasks
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/supported-types")
async def get_supported_file_types():
    """
    获取支持的文件类型

    返回服务支持的文件类型列表
    """
    return {
        "supported_types": [".pdf", ".doc", ".docx"],
        "max_file_size_mb": 50,
        "max_file_size_bytes": storage_service.max_file_size,
        "document_parsing_available": {
            "pdf": document_service.pypdf_available,
            "docx": document_service.docx_available,
            "doc": False,  # .doc格式暂不支持
        },
    }
