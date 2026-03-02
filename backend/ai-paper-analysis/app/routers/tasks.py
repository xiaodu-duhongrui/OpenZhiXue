"""
任务路由
提供任务管理相关的API接口
"""

import logging
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskListResponse,
    TaskCancelResponse,
    TaskStatus,
    TaskType,
    FileType,
    TaskProgress,
)
from app.services.task_service import TaskService
from app.services.task_processor import get_task_processor
from app.models.analysis_task import FileType as ModelFileType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_file_type_from_extension(filename: str) -> FileType:
    """根据文件扩展名获取文件类型"""
    extension = filename.lower().split(".")[-1] if "." in filename else ""
    if extension == "pdf":
        return FileType.PDF
    elif extension in ["doc", "docx"]:
        return FileType.WORD
    return FileType.PDF  # 默认PDF


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    """
    创建分析任务

    创建一个新的分析任务并在后台处理。

    任务类型：
    - document_parse: 仅解析文档，提取文本
    - question_analysis: 仅分析题目（需要已有文本）
    - similar_question_generation: 仅生成相似题（需要已有文本）
    - full_analysis: 完整分析流程（解析+分析+生成相似题）

    返回任务ID，可用于查询任务状态和进度。
    """
    try:
        task_service = TaskService(session)

        # 创建任务
        task = await task_service.create_task(task_data)

        # 获取任务处理器
        processor = get_task_processor()

        # 在后台处理任务
        background_tasks.add_task(
            processor.process_task,
            str(task.id),
            task_data.task_type
        )

        logger.info(f"Task created and queued: id={task.id}, type={task_data.task_type}")

        # 获取初始进度
        progress = await task_service.get_task_progress(str(task.id))

        return task_service.task_to_response(task, progress, task_data.task_type)

    except Exception as e:
        logger.error(f"Failed to create task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    获取任务状态

    通过任务ID查询任务的详细状态和进度。

    返回：
    - 任务状态（pending/processing/completed/failed/cancelled）
    - 任务进度（当前步骤、百分比等）
    - 处理结果（如果已完成）
    - 错误信息（如果失败）
    """
    task_service = TaskService(session)

    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 获取进度
    progress = await task_service.get_task_progress(str(task_id))

    return task_service.task_to_response(task, progress)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="按状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    获取任务列表

    获取所有任务列表，支持按状态筛选和分页。

    查询参数：
    - status: 按状态筛选（可选）
    - page: 页码（默认1）
    - page_size: 每页数量（默认20，最大100）
    """
    task_service = TaskService(session)

    tasks, total = await task_service.list_tasks(status, page, page_size)

    # 转换为响应模型
    items = []
    for task in tasks:
        progress = await task_service.get_task_progress(str(task.id))
        items.append(task_service.task_to_response(task, progress))

    return TaskListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    删除任务

    删除指定的任务及其相关数据。

    注意：
    - 只能删除已完成、失败或已取消的任务
    - 正在处理的任务需要先取消
    """
    task_service = TaskService(session)

    # 检查任务是否存在
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 检查任务状态
    if task.status.value in ["pending", "processing"]:
        raise HTTPException(
            status_code=400,
            detail="无法删除正在处理或待处理的任务，请先取消任务"
        )

    # 删除任务
    success = await task_service.delete_task(task_id)

    if success:
        return {"success": True, "message": "任务已删除", "task_id": str(task_id)}
    else:
        raise HTTPException(status_code=500, detail="删除任务失败")


@router.post("/{task_id}/cancel", response_model=TaskCancelResponse)
async def cancel_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    取消任务

    取消正在处理或待处理的任务。

    注意：
    - 只能取消待处理或处理中的任务
    - 已完成或已失败的任务无法取消
    """
    task_service = TaskService(session)

    # 检查任务是否存在
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 取消任务
    cancelled_task = await task_service.cancel_task(task_id)

    if cancelled_task:
        return TaskCancelResponse(
            success=True,
            message="任务已取消",
            task_id=task_id,
            status=TaskStatus.CANCELLED,
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="无法取消任务，任务可能已完成或已失败"
        )


@router.get("/{task_id}/progress", response_model=TaskProgress)
async def get_task_progress(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    获取任务进度

    获取任务的详细进度信息。

    返回：
    - 当前步骤描述
    - 总步骤数
    - 当前步骤编号
    - 完成百分比
    - 进度消息
    """
    task_service = TaskService(session)

    # 检查任务是否存在
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 获取进度
    progress = await task_service.get_task_progress(str(task_id))

    if not progress:
        # 如果没有进度信息，返回默认进度
        progress = TaskProgress(
            current_step="等待处理",
            total_steps=1,
            current_step_number=0,
            percentage=0,
            message="任务等待处理中"
        )

    return progress


@router.post("/{task_id}/retry")
async def retry_task(
    task_id: UUID,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_async_session),
):
    """
    重试失败的任务

    重新执行失败的任务。

    注意：
    - 只能重试失败的任务
    - 任务会从头开始重新执行
    """
    task_service = TaskService(session)

    # 检查任务是否存在
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 检查任务状态
    if task.status.value != "failed":
        raise HTTPException(
            status_code=400,
            detail="只能重试失败的任务"
        )

    # 获取任务处理器
    processor = get_task_processor()

    # 重置任务状态
    await task_service.update_task_status(task_id, TaskStatus.PENDING)

    # 在后台重新处理任务
    background_tasks.add_task(
        processor.process_task,
        str(task_id),
        TaskType.FULL_ANALYSIS  # 默认使用完整分析
    )

    return {
        "success": True,
        "message": "任务已重新排队",
        "task_id": str(task_id)
    }
