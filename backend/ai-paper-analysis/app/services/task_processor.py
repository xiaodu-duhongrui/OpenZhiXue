"""
后台任务处理器
处理文档解析、题目分析、相似题生成等异步任务
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.models.analysis_task import TaskStatus as ModelTaskStatus
from app.schemas.task import TaskStatus, TaskType, TaskProgress
from app.services.task_service import TaskService
from app.services.document_service import document_service, DocumentParseError
from app.services.ai_service import get_ai_service
from app.utils import redis_client

logger = logging.getLogger(__name__)


class TaskProcessor:
    """后台任务处理器"""

    # 最大重试次数
    MAX_RETRIES = 3
    # 重试延迟（秒）
    RETRY_DELAY = 5

    def __init__(self):
        """初始化任务处理器"""
        self._running_tasks: Dict[str, bool] = {}

    def is_task_running(self, task_id: str) -> bool:
        """检查任务是否正在运行"""
        return self._running_tasks.get(task_id, False)

    def mark_task_running(self, task_id: str, running: bool = True):
        """标记任务运行状态"""
        self._running_tasks[task_id] = running

    async def process_task(self, task_id: str, task_type: TaskType):
        """
        处理任务的主入口

        Args:
            task_id: 任务ID
            task_type: 任务类型
        """
        # 检查是否已经在运行
        if self.is_task_running(task_id):
            logger.warning(f"Task {task_id} is already running")
            return

        self.mark_task_running(task_id, True)

        try:
            async with async_session_maker() as session:
                task_service = TaskService(session)

                # 获取任务
                task = await task_service.get_task(UUID(task_id))
                if not task:
                    logger.error(f"Task not found: {task_id}")
                    return

                # 检查任务状态
                if task.status != ModelTaskStatus.PENDING:
                    logger.warning(f"Task {task_id} is not in pending status: {task.status}")
                    return

                # 更新状态为处理中
                await task_service.update_task_status(
                    UUID(task_id),
                    TaskStatus.PROCESSING
                )

                # 根据任务类型处理
                if task_type == TaskType.DOCUMENT_PARSE:
                    await self._process_document_parse(task_id, task_service, task)
                elif task_type == TaskType.QUESTION_ANALYSIS:
                    await self._process_question_analysis(task_id, task_service, task)
                elif task_type == TaskType.SIMILAR_QUESTION_GENERATION:
                    await self._process_similar_question_generation(task_id, task_service, task)
                elif task_type == TaskType.FULL_ANALYSIS:
                    await self._process_full_analysis(task_id, task_service, task)
                else:
                    logger.error(f"Unknown task type: {task_type}")
                    await task_service.update_task_status(
                        UUID(task_id),
                        TaskStatus.FAILED,
                        error_message=f"未知的任务类型: {task_type}"
                    )

        except Exception as e:
            logger.error(f"Task processing failed: task_id={task_id}, error={str(e)}", exc_info=True)
            # 尝试更新任务状态为失败
            try:
                async with async_session_maker() as session:
                    task_service = TaskService(session)
                    await task_service.update_task_status(
                        UUID(task_id),
                        TaskStatus.FAILED,
                        error_message=str(e)
                    )
            except Exception as update_error:
                logger.error(f"Failed to update task status: {update_error}")

        finally:
            self.mark_task_running(task_id, False)

    async def _process_document_parse(
        self,
        task_id: str,
        task_service: TaskService,
        task,
    ):
        """
        处理文档解析任务

        Args:
            task_id: 任务ID
            task_service: 任务服务
            task: 任务对象
        """
        try:
            # 更新进度：开始解析
            await self._update_progress(task_service, task_id, TaskType.DOCUMENT_PARSE, 1, "正在解析文档...")

            # 解析文档
            result = await document_service.parse_document(task.file_path)

            if not result.get("success"):
                raise DocumentParseError(result.get("error", "文档解析失败"))

            # 更新进度：提取文本完成
            await self._update_progress(task_service, task_id, TaskType.DOCUMENT_PARSE, 2, "文本提取完成")

            # 更新任务状态
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.COMPLETED,
                extracted_text=result.get("text"),
            )

            # 更新进度：完成
            await self._update_progress(task_service, task_id, TaskType.DOCUMENT_PARSE, 3, "任务完成")

            logger.info(f"Document parse completed: task_id={task_id}")

        except DocumentParseError as e:
            logger.error(f"Document parse failed: task_id={task_id}, error={str(e)}")
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.FAILED,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Document parse failed: task_id={task_id}, error={str(e)}", exc_info=True)
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.FAILED,
                error_message=f"文档解析失败: {str(e)}"
            )

    async def _process_question_analysis(
        self,
        task_id: str,
        task_service: TaskService,
        task,
    ):
        """
        处理题目分析任务

        Args:
            task_id: 任务ID
            task_service: 任务服务
            task: 任务对象
        """
        try:
            # 检查是否有提取的文本
            if not task.extracted_text:
                raise ValueError("没有可分析的文本内容，请先解析文档")

            # 更新进度：加载模型
            await self._update_progress(task_service, task_id, TaskType.QUESTION_ANALYSIS, 1, "正在加载AI模型...")

            # 获取AI服务
            ai_service = get_ai_service()

            # 确保模型已加载
            if not ai_service.is_model_loaded():
                success = await asyncio.to_thread(ai_service.load_model)
                if not success:
                    raise RuntimeError("AI模型加载失败")

            # 更新进度：分析题目
            await self._update_progress(task_service, task_id, TaskType.QUESTION_ANALYSIS, 2, "正在分析题目...")

            # 执行分析
            analysis_result = await asyncio.to_thread(
                ai_service.analyze_questions,
                task.extracted_text
            )

            if not analysis_result.get("success"):
                raise ValueError(analysis_result.get("error", "题目分析失败"))

            # 更新进度：完成
            await self._update_progress(task_service, task_id, TaskType.QUESTION_ANALYSIS, 3, "任务完成")

            # 更新任务状态
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.COMPLETED,
                analysis_result=analysis_result.get("data"),
            )

            logger.info(f"Question analysis completed: task_id={task_id}")

        except Exception as e:
            logger.error(f"Question analysis failed: task_id={task_id}, error={str(e)}", exc_info=True)
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.FAILED,
                error_message=f"题目分析失败: {str(e)}"
            )

    async def _process_similar_question_generation(
        self,
        task_id: str,
        task_service: TaskService,
        task,
    ):
        """
        处理相似题生成任务

        Args:
            task_id: 任务ID
            task_service: 任务服务
            task: 任务对象
        """
        try:
            # 检查是否有提取的文本
            if not task.extracted_text:
                raise ValueError("没有可用的文本内容，请先解析文档")

            # 更新进度：加载模型
            await self._update_progress(task_service, task_id, TaskType.SIMILAR_QUESTION_GENERATION, 1, "正在加载AI模型...")

            # 获取AI服务
            ai_service = get_ai_service()

            # 确保模型已加载
            if not ai_service.is_model_loaded():
                success = await asyncio.to_thread(ai_service.load_model)
                if not success:
                    raise RuntimeError("AI模型加载失败")

            # 更新进度：生成相似题
            await self._update_progress(task_service, task_id, TaskType.SIMILAR_QUESTION_GENERATION, 2, "正在生成相似题...")

            # 执行相似题生成
            similar_result = await asyncio.to_thread(
                ai_service.generate_similar_questions,
                task.extracted_text[:2000],  # 限制文本长度
                count=3
            )

            if not similar_result.get("success"):
                raise ValueError(similar_result.get("error", "相似题生成失败"))

            # 更新进度：完成
            await self._update_progress(task_service, task_id, TaskType.SIMILAR_QUESTION_GENERATION, 3, "任务完成")

            # 更新任务状态
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.COMPLETED,
                similar_questions=similar_result.get("data", {}).get("similar_questions", []),
            )

            logger.info(f"Similar question generation completed: task_id={task_id}")

        except Exception as e:
            logger.error(f"Similar question generation failed: task_id={task_id}, error={str(e)}", exc_info=True)
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.FAILED,
                error_message=f"相似题生成失败: {str(e)}"
            )

    async def _process_full_analysis(
        self,
        task_id: str,
        task_service: TaskService,
        task,
    ):
        """
        处理完整分析任务（解析+分析+生成相似题）

        Args:
            task_id: 任务ID
            task_service: 任务服务
            task: 任务对象
        """
        extracted_text = None
        analysis_result = None
        similar_questions = None

        try:
            # 步骤1：解析文档
            await self._update_progress(task_service, task_id, TaskType.FULL_ANALYSIS, 1, "正在解析文档...")

            parse_result = await document_service.parse_document(task.file_path)

            if not parse_result.get("success"):
                raise DocumentParseError(parse_result.get("error", "文档解析失败"))

            extracted_text = parse_result.get("text")

            # 步骤2：提取文本完成
            await self._update_progress(task_service, task_id, TaskType.FULL_ANALYSIS, 2, "文本提取完成")

            # 步骤3：加载AI模型
            await self._update_progress(task_service, task_id, TaskType.FULL_ANALYSIS, 3, "正在加载AI模型...")

            ai_service = get_ai_service()

            if not ai_service.is_model_loaded():
                success = await asyncio.to_thread(ai_service.load_model)
                if not success:
                    raise RuntimeError("AI模型加载失败")

            # 步骤4：分析题目
            await self._update_progress(task_service, task_id, TaskType.FULL_ANALYSIS, 4, "正在分析题目...")

            analysis_response = await asyncio.to_thread(
                ai_service.analyze_questions,
                extracted_text[:4000]  # 限制文本长度
            )

            if analysis_response.get("success"):
                analysis_result = analysis_response.get("data")

            # 步骤5：生成相似题
            await self._update_progress(task_service, task_id, TaskType.FULL_ANALYSIS, 5, "正在生成相似题...")

            similar_response = await asyncio.to_thread(
                ai_service.generate_similar_questions,
                extracted_text[:2000],
                count=3
            )

            if similar_response.get("success"):
                similar_questions = similar_response.get("data", {}).get("similar_questions", [])

            # 步骤6：保存结果
            await self._update_progress(task_service, task_id, TaskType.FULL_ANALYSIS, 6, "正在保存结果...")

            # 更新任务状态
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.COMPLETED,
                extracted_text=extracted_text,
                analysis_result=analysis_result,
                similar_questions=similar_questions,
            )

            logger.info(f"Full analysis completed: task_id={task_id}")

        except DocumentParseError as e:
            logger.error(f"Full analysis failed at document parse: task_id={task_id}, error={str(e)}")
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.FAILED,
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Full analysis failed: task_id={task_id}, error={str(e)}", exc_info=True)
            await task_service.update_task_status(
                UUID(task_id),
                TaskStatus.FAILED,
                error_message=f"分析失败: {str(e)}"
            )

    async def _update_progress(
        self,
        task_service: TaskService,
        task_id: str,
        task_type: TaskType,
        step: int,
        message: str,
    ):
        """
        更新任务进度

        Args:
            task_service: 任务服务
            task_id: 任务ID
            task_type: 任务类型
            step: 当前步骤
            message: 进度消息
        """
        await task_service._update_progress(task_id, TaskStatus.PROCESSING, task_type, step, message)
        logger.debug(f"Task progress updated: task_id={task_id}, step={step}, message={message}")

    async def retry_task(self, task_id: str, task_type: TaskType, retry_count: int = 0):
        """
        重试失败的任务

        Args:
            task_id: 任务ID
            task_type: 任务类型
            retry_count: 当前重试次数
        """
        if retry_count >= self.MAX_RETRIES:
            logger.error(f"Task {task_id} exceeded max retries ({self.MAX_RETRIES})")
            async with async_session_maker() as session:
                task_service = TaskService(session)
                await task_service.update_task_status(
                    UUID(task_id),
                    TaskStatus.FAILED,
                    error_message=f"任务重试次数超过上限 ({self.MAX_RETRIES}次)"
                )
            return

        logger.info(f"Retrying task {task_id}, attempt {retry_count + 1}/{self.MAX_RETRIES}")

        # 等待一段时间后重试
        await asyncio.sleep(self.RETRY_DELAY * (retry_count + 1))

        # 重置任务状态为待处理
        async with async_session_maker() as session:
            task_service = TaskService(session)
            await task_service.update_task_status(UUID(task_id), TaskStatus.PENDING)

        # 重新处理任务
        await self.process_task(task_id, task_type)


# 创建全局任务处理器实例
task_processor = TaskProcessor()


def get_task_processor() -> TaskProcessor:
    """获取任务处理器实例"""
    return task_processor
