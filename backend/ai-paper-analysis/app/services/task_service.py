"""
任务服务模块
管理任务的生命周期，包括创建、查询、更新和删除任务
"""

import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_task import AnalysisTask, TaskStatus as ModelTaskStatus, FileType as ModelFileType
from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskStatus,
    TaskType,
    TaskProgress,
    FileType,
)
from app.utils import redis_client

logger = logging.getLogger(__name__)


class TaskService:
    """任务服务类，管理任务生命周期"""

    # 任务进度步骤定义
    PROGRESS_STEPS = {
        TaskType.DOCUMENT_PARSE: [
            "初始化",
            "解析文档",
            "提取文本",
            "完成",
        ],
        TaskType.QUESTION_ANALYSIS: [
            "初始化",
            "加载AI模型",
            "分析题目",
            "完成",
        ],
        TaskType.SIMILAR_QUESTION_GENERATION: [
            "初始化",
            "加载AI模型",
            "生成相似题",
            "完成",
        ],
        TaskType.FULL_ANALYSIS: [
            "初始化",
            "解析文档",
            "提取文本",
            "分析题目",
            "生成相似题",
            "保存结果",
            "完成",
        ],
    }

    def __init__(self, session: AsyncSession):
        """初始化任务服务"""
        self.session = session

    async def create_task(self, task_data: TaskCreate) -> AnalysisTask:
        """
        创建新任务

        Args:
            task_data: 任务创建数据

        Returns:
            创建的任务对象
        """
        task_id = uuid4()
        now = datetime.utcnow()

        # 映射文件类型
        file_type_map = {
            FileType.PDF: ModelFileType.PDF,
            FileType.WORD: ModelFileType.WORD,
        }

        task = AnalysisTask(
            id=task_id,
            status=ModelTaskStatus.PENDING,
            file_path=task_data.file_path,
            file_type=file_type_map.get(task_data.file_type, ModelFileType.PDF),
            original_filename=task_data.original_filename,
            created_at=now,
            updated_at=now,
        )

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)

        # 在Redis中设置初始状态
        await redis_client.set_task_status(
            str(task.id),
            TaskStatus.PENDING.value,
            ttl=86400  # 24小时
        )

        # 存储任务进度信息
        await self._update_progress(
            str(task.id),
            TaskStatus.PENDING,
            task_data.task_type,
            0,
            "任务已创建，等待处理"
        )

        logger.info(f"Task created: id={task.id}, type={task_data.task_type}, file={task_data.original_filename}")

        return task

    async def get_task(self, task_id: UUID) -> Optional[AnalysisTask]:
        """
        获取任务详情

        Args:
            task_id: 任务ID

        Returns:
            任务对象或None
        """
        result = await self.session.execute(
            select(AnalysisTask).where(AnalysisTask.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[AnalysisTask], int]:
        """
        获取任务列表

        Args:
            status: 按状态筛选
            page: 页码
            page_size: 每页数量

        Returns:
            任务列表和总数
        """
        query = select(AnalysisTask)

        if status:
            status_map = {
                TaskStatus.PENDING: ModelTaskStatus.PENDING,
                TaskStatus.PROCESSING: ModelTaskStatus.PROCESSING,
                TaskStatus.COMPLETED: ModelTaskStatus.COMPLETED,
                TaskStatus.FAILED: ModelTaskStatus.FAILED,
                TaskStatus.CANCELLED: ModelTaskStatus.FAILED,  # 取消的任务映射为失败
            }
            query = query.where(AnalysisTask.status == status_map.get(status))

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # 分页查询
        query = query.order_by(AnalysisTask.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.session.execute(query)
        tasks = list(result.scalars().all())

        return tasks, total

    async def update_task_status(
        self,
        task_id: UUID,
        status: TaskStatus,
        error_message: Optional[str] = None,
        extracted_text: Optional[str] = None,
        analysis_result: Optional[Dict[str, Any]] = None,
        similar_questions: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[AnalysisTask]:
        """
        更新任务状态

        Args:
            task_id: 任务ID
            status: 新状态
            error_message: 错误信息
            extracted_text: 提取的文本
            analysis_result: 分析结果
            similar_questions: 相似题目列表

        Returns:
            更新后的任务对象
        """
        task = await self.get_task(task_id)
        if not task:
            logger.warning(f"Task not found: {task_id}")
            return None

        # 状态映射
        status_map = {
            TaskStatus.PENDING: ModelTaskStatus.PENDING,
            TaskStatus.PROCESSING: ModelTaskStatus.PROCESSING,
            TaskStatus.COMPLETED: ModelTaskStatus.COMPLETED,
            TaskStatus.FAILED: ModelTaskStatus.FAILED,
            TaskStatus.CANCELLED: ModelTaskStatus.FAILED,
        }

        task.status = status_map.get(status, ModelTaskStatus.PENDING)
        task.updated_at = datetime.utcnow()

        if error_message:
            task.error_message = error_message

        if extracted_text is not None:
            task.extracted_text = extracted_text

        if analysis_result is not None:
            task.analysis_result = analysis_result

        if similar_questions is not None:
            task.similar_questions = similar_questions

        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        # 更新Redis缓存
        await redis_client.set_task_status(
            str(task_id),
            status.value,
            ttl=86400
        )

        logger.info(f"Task status updated: id={task_id}, status={status}")

        return task

    async def delete_task(self, task_id: UUID) -> bool:
        """
        删除任务

        Args:
            task_id: 任务ID

        Returns:
            是否删除成功
        """
        task = await self.get_task(task_id)
        if not task:
            logger.warning(f"Task not found for deletion: {task_id}")
            return False

        await self.session.execute(
            delete(AnalysisTask).where(AnalysisTask.id == task_id)
        )
        await self.session.commit()

        # 删除Redis缓存
        await redis_client.delete_task_cache(str(task_id))

        logger.info(f"Task deleted: id={task_id}")

        return True

    async def cancel_task(self, task_id: UUID) -> Optional[AnalysisTask]:
        """
        取消任务

        Args:
            task_id: 任务ID

        Returns:
            更新后的任务对象
        """
        task = await self.get_task(task_id)
        if not task:
            return None

        # 只有待处理或处理中的任务可以取消
        if task.status not in [ModelTaskStatus.PENDING, ModelTaskStatus.PROCESSING]:
            logger.warning(f"Cannot cancel task {task_id} with status {task.status}")
            return None

        task.status = ModelTaskStatus.FAILED
        task.error_message = "任务已取消"
        task.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(task)

        # 更新Redis缓存
        await redis_client.set_task_status(
            str(task_id),
            TaskStatus.CANCELLED.value,
            ttl=86400
        )

        logger.info(f"Task cancelled: id={task_id}")

        return task

    async def _update_progress(
        self,
        task_id: str,
        status: TaskStatus,
        task_type: TaskType,
        step: int,
        message: str,
    ):
        """
        更新任务进度到Redis

        Args:
            task_id: 任务ID
            status: 任务状态
            task_type: 任务类型
            step: 当前步骤
            message: 进度消息
        """
        steps = self.PROGRESS_STEPS.get(task_type, ["初始化", "处理中", "完成"])
        total_steps = len(steps)

        progress = TaskProgress(
            current_step=steps[min(step, total_steps - 1)],
            total_steps=total_steps,
            current_step_number=step + 1,
            percentage=int((step + 1) / total_steps * 100),
            message=message,
        )

        # 存储进度到Redis
        progress_key = f"task_progress:{task_id}"
        await redis_client.set_cache(
            progress_key,
            progress.model_dump(),
            ttl=86400
        )

    async def get_task_progress(self, task_id: str) -> Optional[TaskProgress]:
        """
        获取任务进度

        Args:
            task_id: 任务ID

        Returns:
            任务进度或None
        """
        progress_key = f"task_progress:{task_id}"
        progress_data = await redis_client.get_cache(progress_key)

        if progress_data:
            return TaskProgress(**progress_data)
        return None

    def task_to_response(
        self,
        task: AnalysisTask,
        progress: Optional[TaskProgress] = None,
        task_type: TaskType = TaskType.FULL_ANALYSIS,
    ) -> TaskResponse:
        """
        将任务模型转换为响应模型

        Args:
            task: 任务模型
            progress: 任务进度
            task_type: 任务类型

        Returns:
            任务响应模型
        """
        # 状态映射
        status_map = {
            ModelTaskStatus.PENDING: TaskStatus.PENDING,
            ModelTaskStatus.PROCESSING: TaskStatus.PROCESSING,
            ModelTaskStatus.COMPLETED: TaskStatus.COMPLETED,
            ModelTaskStatus.FAILED: TaskStatus.FAILED,
        }

        # 文件类型映射
        file_type_map = {
            ModelFileType.PDF: FileType.PDF,
            ModelFileType.WORD: FileType.WORD,
        }

        return TaskResponse(
            id=task.id,
            status=status_map.get(task.status, TaskStatus.PENDING),
            task_type=task_type,
            file_path=task.file_path,
            file_type=file_type_map.get(task.file_type, FileType.PDF),
            original_filename=task.original_filename,
            progress=progress,
            extracted_text=task.extracted_text,
            analysis_result=task.analysis_result,
            similar_questions=task.similar_questions,
            error_message=task.error_message,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at,
        )
