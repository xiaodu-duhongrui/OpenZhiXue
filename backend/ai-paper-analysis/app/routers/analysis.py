"""
分析路由
提供文档解析、题目分析和相似题生成的API接口
"""

import logging
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    File,
    BackgroundTasks,
    Query,
)

from app.database import get_async_session
from app.services.storage_service import storage_service
from app.services.document_service import document_service, DocumentParseError
from app.services.ai_service import get_ai_service, AIModelService
from app.services.task_service import TaskService
from app.services.task_processor import get_task_processor
from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResult,
    AnalysisStatus,
    AnalyzeRequest,
    AnalyzeResponse,
    ParseRequest,
    ParseResponse,
    GenerateRequest,
    GenerateResponse,
    FullAnalysisRequest,
    FullAnalysisResponse,
    QuestionAnalysis,
    SimilarQuestion,
    PaperAnalysisResult,
    KnowledgePoint,
    QuestionType,
    DifficultyLevel,
)
from app.schemas.task import TaskType, TaskStatus, FileType, TaskCreate
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _get_file_type_from_extension(filename: str) -> FileType:
    """根据文件扩展名获取文件类型"""
    extension = filename.lower().split(".")[-1] if "." in filename else ""
    if extension == "pdf":
        return FileType.PDF
    elif extension in ["doc", "docx"]:
        return FileType.WORD
    return FileType.PDF  # 默认PDF


def _map_question_type(type_str: str) -> QuestionType:
    """映射题目类型字符串到枚举"""
    type_mapping = {
        "选择题": QuestionType.CHOICE,
        "填空题": QuestionType.FILL_BLANK,
        "简答题": QuestionType.SHORT_ANSWER,
        "计算题": QuestionType.CALCULATION,
        "证明题": QuestionType.PROOF,
        "应用题": QuestionType.APPLICATION,
        "choice": QuestionType.CHOICE,
        "fill_blank": QuestionType.FILL_BLANK,
        "short_answer": QuestionType.SHORT_ANSWER,
        "calculation": QuestionType.CALCULATION,
        "proof": QuestionType.PROOF,
        "application": QuestionType.APPLICATION,
    }
    return type_mapping.get(type_str, QuestionType.UNKNOWN)


def _map_difficulty(difficulty_str: str) -> DifficultyLevel:
    """映射难度字符串到枚举"""
    difficulty_mapping = {
        "简单": DifficultyLevel.EASY,
        "中等": DifficultyLevel.MEDIUM,
        "困难": DifficultyLevel.HARD,
        "easy": DifficultyLevel.EASY,
        "medium": DifficultyLevel.MEDIUM,
        "hard": DifficultyLevel.HARD,
    }
    return difficulty_mapping.get(difficulty_str, DifficultyLevel.UNKNOWN)


def _parse_ai_analysis_result(data: Dict[str, Any]) -> QuestionAnalysis:
    """解析AI分析结果为QuestionAnalysis模型"""
    knowledge_points = []
    for kp in data.get("knowledge_points", []):
        if isinstance(kp, str):
            knowledge_points.append(KnowledgePoint(name=kp))
        elif isinstance(kp, dict):
            knowledge_points.append(KnowledgePoint(
                name=kp.get("name", ""),
                category=kp.get("category"),
                description=kp.get("description"),
                importance=kp.get("importance"),
            ))

    return QuestionAnalysis(
        question_type=_map_question_type(data.get("question_type", "unknown")),
        difficulty=_map_difficulty(data.get("difficulty", "medium")),
        content=data.get("content"),
        answer=data.get("answer"),
        analysis=data.get("analysis"),
        knowledge_points=knowledge_points,
        main_knowledge_points=data.get("main_knowledge_points", []),
        secondary_knowledge_points=data.get("secondary_knowledge_points", []),
        estimated_time=data.get("estimated_time"),
        score=data.get("score"),
        tags=data.get("tags", []),
    )


def _parse_similar_questions(data: Dict[str, Any]) -> list[SimilarQuestion]:
    """解析AI生成的相似题结果"""
    similar_questions = []
    questions_data = data.get("similar_questions", data.get("questions", []))

    for idx, q in enumerate(questions_data):
        if isinstance(q, dict):
            similar_questions.append(SimilarQuestion(
                question_id=idx + 1,
                content=q.get("content", q.get("question", "")),
                answer=q.get("answer"),
                analysis=q.get("analysis"),
                difficulty=_map_difficulty(q.get("difficulty", "medium")),
                knowledge_points=q.get("knowledge_points", []),
                similarity_score=q.get("similarity_score"),
            ))

    return similar_questions


@router.post("/parse", response_model=ParseResponse, status_code=201)
async def parse_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="要解析的文档文件（PDF或Word）"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    解析文档

    上传文件并解析文档内容，提取文本信息。

    支持的文件类型：
    - PDF文档 (.pdf)
    - Word文档 (.doc, .docx)

    文件大小限制：50MB

    返回任务ID，可用于查询解析状态和结果。
    """
    task_id = uuid4()

    try:
        # 保存文件
        file_info = await storage_service.save_file(file)
        logger.info(f"File saved: {file_info['file_path']}")

        # 解析文档
        parse_result = await document_service.parse_document(file_info["file_path"])

        if not parse_result.get("success"):
            raise HTTPException(
                status_code=422,
                detail=f"文档解析失败: {parse_result.get('error', '未知错误')}"
            )

        # 创建任务记录
        task_service = TaskService(session)
        task_create = TaskCreate(
            file_path=file_info["file_path"],
            file_type=_get_file_type_from_extension(file.filename or "document.pdf"),
            original_filename=file.filename or "document",
            task_type=TaskType.DOCUMENT_PARSE,
        )
        task = await task_service.create_task(task_create)

        # 更新任务结果
        await task_service.update_task_status(
            task.id,
            TaskStatus.COMPLETED,
            extracted_text=parse_result.get("text"),
        )

        return ParseResponse(
            success=True,
            task_id=task.id,
            message="文档解析成功",
            extracted_text=parse_result.get("text"),
            page_count=parse_result.get("page_count"),
            word_count=parse_result.get("word_count"),
            metadata=parse_result.get("metadata"),
        )

    except DocumentParseError as e:
        logger.error(f"Document parse error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to parse document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"文档解析失败: {str(e)}")


@router.post("/analyze", response_model=AnalyzeResponse, status_code=201)
async def analyze_questions(
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    分析题目

    对已解析的文档内容进行题目分析。

    需要提供任务ID，该任务必须已完成文档解析。

    分析内容包括：
    - 题目类型识别
    - 难度评估
    - 知识点提取
    - 答案解析
    """
    task_service = TaskService(session)

    # 获取任务
    task = await task_service.get_task(request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {request.task_id}")

    # 检查任务状态
    if task.status.value not in ["completed", "processing"]:
        raise HTTPException(
            status_code=400,
            detail=f"任务状态无效，当前状态: {task.status.value}"
        )

    # 检查是否有提取的文本
    if not task.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="任务尚未完成文档解析，请先解析文档"
        )

    try:
        # 获取AI服务
        ai_service = get_ai_service()

        # 分析题目
        analysis_result = ai_service.analyze_questions(task.extracted_text)

        if not analysis_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"题目分析失败: {analysis_result.get('error', '未知错误')}"
            )

        # 解析结果
        question_analysis = _parse_ai_analysis_result(analysis_result.get("data", {}))

        # 更新任务
        await task_service.update_task_status(
            request.task_id,
            TaskStatus.COMPLETED,
            analysis_result=analysis_result.get("data"),
        )

        return AnalyzeResponse(
            success=True,
            task_id=request.task_id,
            message="题目分析成功",
            analysis=question_analysis,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to analyze questions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"题目分析失败: {str(e)}")


@router.post("/generate", response_model=GenerateResponse, status_code=201)
async def generate_similar_questions(
    request: GenerateRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    生成相似题

    基于已分析的题目生成相似题目。

    需要提供任务ID，该任务必须已完成题目分析。

    参数：
    - task_id: 任务ID
    - count: 生成数量（1-10，默认3）
    """
    task_service = TaskService(session)

    # 获取任务
    task = await task_service.get_task(request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {request.task_id}")

    # 检查任务状态
    if task.status.value not in ["completed", "processing"]:
        raise HTTPException(
            status_code=400,
            detail=f"任务状态无效，当前状态: {task.status.value}"
        )

    # 检查是否有提取的文本
    if not task.extracted_text:
        raise HTTPException(
            status_code=400,
            detail="任务尚未完成文档解析，请先解析文档"
        )

    try:
        # 获取AI服务
        ai_service = get_ai_service()

        # 获取分析结果中的知识点信息
        analysis_data = task.analysis_result or {}

        # 生成相似题
        generate_result = ai_service.generate_similar_questions(
            question=task.extracted_text[:2000],  # 限制长度
            count=request.count,
            question_type=analysis_data.get("question_type"),
            difficulty=analysis_data.get("difficulty"),
            knowledge_points=analysis_data.get("main_knowledge_points", []),
        )

        if not generate_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"相似题生成失败: {generate_result.get('error', '未知错误')}"
            )

        # 解析结果
        similar_questions = _parse_similar_questions(generate_result.get("data", {}))

        # 更新任务
        await task_service.update_task_status(
            request.task_id,
            TaskStatus.COMPLETED,
            similar_questions=[sq.model_dump() for sq in similar_questions],
        )

        return GenerateResponse(
            success=True,
            task_id=request.task_id,
            message=f"成功生成 {len(similar_questions)} 道相似题",
            similar_questions=similar_questions,
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Failed to generate similar questions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"相似题生成失败: {str(e)}")


@router.post("/full", response_model=FullAnalysisResponse, status_code=201)
async def full_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="要分析的文档文件"),
    similar_question_count: int = Query(default=3, ge=1, le=10, description="相似题生成数量"),
    session: AsyncSession = Depends(get_async_session),
):
    """
    完整分析流程

    执行完整的分析流程：上传 -> 解析 -> 分析 -> 生成相似题

    这是最便捷的API，一次性完成所有分析步骤。

    支持的文件类型：
    - PDF文档 (.pdf)
    - Word文档 (.doc, .docx)

    参数：
    - file: 要分析的文档文件
    - similar_question_count: 相似题生成数量（1-10，默认3）
    """
    task_id = uuid4()

    try:
        # Step 1: 保存文件
        file_info = await storage_service.save_file(file)
        logger.info(f"[Full Analysis] File saved: {file_info['file_path']}")

        # 创建任务
        task_service = TaskService(session)
        task_create = TaskCreate(
            file_path=file_info["file_path"],
            file_type=_get_file_type_from_extension(file.filename or "document.pdf"),
            original_filename=file.filename or "document",
            task_type=TaskType.FULL_ANALYSIS,
            options={"similar_question_count": similar_question_count},
        )
        task = await task_service.create_task(task_create)

        # Step 2: 解析文档
        parse_result = await document_service.parse_document(file_info["file_path"])

        if not parse_result.get("success"):
            await task_service.update_task_status(
                task.id,
                TaskStatus.FAILED,
                error_message=f"文档解析失败: {parse_result.get('error')}"
            )
            raise HTTPException(
                status_code=422,
                detail=f"文档解析失败: {parse_result.get('error', '未知错误')}"
            )

        extracted_text = parse_result.get("text", "")
        logger.info(f"[Full Analysis] Document parsed: {parse_result.get('word_count')} words")

        # 更新任务状态
        await task_service.update_task_status(
            task.id,
            TaskStatus.PROCESSING,
            extracted_text=extracted_text,
        )

        # Step 3: 分析题目
        ai_service = get_ai_service()
        analysis_result = ai_service.analyze_questions(extracted_text)

        if not analysis_result.get("success"):
            logger.warning(f"[Full Analysis] Question analysis failed: {analysis_result.get('error')}")
            # 继续执行，即使分析失败

        question_analysis = None
        paper_analysis = None

        if analysis_result.get("success"):
            data = analysis_result.get("data", {})
            question_analysis = _parse_ai_analysis_result(data)

            # 构建试卷分析结果
            paper_analysis = PaperAnalysisResult(
                total_questions=1,
                question_types_distribution={
                    question_analysis.question_type.value: 1
                },
                difficulty_distribution={
                    question_analysis.difficulty.value: 1
                },
                knowledge_points=question_analysis.knowledge_points,
                questions=[question_analysis],
                overall_difficulty=question_analysis.difficulty,
            )

        logger.info(f"[Full Analysis] Questions analyzed")

        # Step 4: 生成相似题
        similar_questions = []

        if analysis_result.get("success"):
            generate_result = ai_service.generate_similar_questions(
                question=extracted_text[:2000],
                count=similar_question_count,
                question_type=analysis_result.get("data", {}).get("question_type"),
                difficulty=analysis_result.get("data", {}).get("difficulty"),
                knowledge_points=analysis_result.get("data", {}).get("main_knowledge_points", []),
            )

            if generate_result.get("success"):
                similar_questions = _parse_similar_questions(generate_result.get("data", {}))
                logger.info(f"[Full Analysis] Generated {len(similar_questions)} similar questions")

        # 更新任务完成状态
        await task_service.update_task_status(
            task.id,
            TaskStatus.COMPLETED,
            analysis_result=analysis_result.get("data") if analysis_result.get("success") else None,
            similar_questions=[sq.model_dump() for sq in similar_questions],
        )

        return FullAnalysisResponse(
            success=True,
            task_id=task.id,
            message="完整分析流程执行成功",
            status=AnalysisStatus.COMPLETED,
            extracted_text=extracted_text,
            page_count=parse_result.get("page_count"),
            word_count=parse_result.get("word_count"),
            paper_analysis=paper_analysis,
            similar_questions=similar_questions,
            metadata={
                "original_filename": file.filename,
                "file_size": file_info.get("file_size"),
                "analysis_success": analysis_result.get("success", False),
            },
        )

    except DocumentParseError as e:
        logger.error(f"[Full Analysis] Document parse error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"[Full Analysis] Failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"完整分析失败: {str(e)}")


@router.get("/{task_id}/result", response_model=AnalysisResult)
async def get_analysis_result(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    获取分析结果

    通过任务ID获取完整的分析结果。

    返回内容包括：
    - 文档解析结果（提取的文本）
    - 题目分析结果
    - 生成的相似题目
    - 任务状态和元数据
    """
    task_service = TaskService(session)

    # 获取任务
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 获取进度
    progress = await task_service.get_task_progress(str(task_id))

    # 映射状态
    status_mapping = {
        "pending": AnalysisStatus.PENDING,
        "processing": AnalysisStatus.PROCESSING,
        "completed": AnalysisStatus.COMPLETED,
        "failed": AnalysisStatus.FAILED,
    }
    analysis_status = status_mapping.get(task.status.value, AnalysisStatus.PENDING)

    # 构建题目分析结果
    question_analysis = None
    paper_analysis = None

    if task.analysis_result:
        question_analysis = _parse_ai_analysis_result(task.analysis_result)
        paper_analysis = PaperAnalysisResult(
            total_questions=1,
            question_types_distribution={
                question_analysis.question_type.value: 1
            },
            difficulty_distribution={
                question_analysis.difficulty.value: 1
            },
            knowledge_points=question_analysis.knowledge_points,
            questions=[question_analysis],
            overall_difficulty=question_analysis.difficulty,
        )

    # 构建相似题列表
    similar_questions = []
    if task.similar_questions:
        for idx, sq in enumerate(task.similar_questions):
            if isinstance(sq, dict):
                similar_questions.append(SimilarQuestion(
                    question_id=idx + 1,
                    content=sq.get("content", sq.get("question", "")),
                    answer=sq.get("answer"),
                    analysis=sq.get("analysis"),
                    difficulty=_map_difficulty(sq.get("difficulty", "medium")),
                    knowledge_points=sq.get("knowledge_points", []),
                    similarity_score=sq.get("similarity_score"),
                ))

    return AnalysisResult(
        task_id=task.id,
        status=analysis_status,
        message=progress.message if progress else None,
        extracted_text=task.extracted_text,
        page_count=len(task.extracted_text.split("--- 第")) if task.extracted_text else 0,
        word_count=len(task.extracted_text.replace(" ", "").replace("\n", "")) if task.extracted_text else 0,
        paper_analysis=paper_analysis,
        question_analysis=question_analysis,
        similar_questions=similar_questions,
        metadata={
            "original_filename": task.original_filename,
            "file_type": task.file_type.value,
            "progress": progress.model_dump() if progress else None,
        },
        error=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
        completed_at=task.completed_at,
    )


@router.get("/{task_id}/status")
async def get_analysis_status(
    task_id: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """
    获取分析状态

    快速获取任务的分析状态，不包含详细结果。
    适用于轮询场景。
    """
    task_service = TaskService(session)

    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    progress = await task_service.get_task_progress(str(task_id))

    return {
        "task_id": str(task_id),
        "status": task.status.value,
        "progress": progress.model_dump() if progress else None,
        "error": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }
