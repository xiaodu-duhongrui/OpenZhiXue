from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_async_session
from app.services.exam_service import ExamService
from app.schemas.exam import (
    ExamCreate, ExamUpdate, ExamResponse, ExamListResponse,
    ExamFilter, ExamStatus
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/exams", tags=["exams"])


@router.post("", response_model=ExamResponse, status_code=201)
async def create_exam(
    exam_data: ExamCreate,
    db: AsyncSession = Depends(get_async_session)
):
    service = ExamService(db)
    exam = await service.create_exam(exam_data)
    return exam


@router.get("", response_model=ExamListResponse)
async def get_exams(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    grade_level: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    school_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    service = ExamService(db)
    filters = ExamFilter(
        type=type,
        status=status,
        grade_level=grade_level,
        semester=semester,
        school_id=school_id,
        page=page,
        page_size=page_size,
    )
    exams, total = await service.get_exams(filters)
    
    total_pages = (total + page_size - 1) // page_size
    
    return ExamListResponse(
        items=[ExamResponse.model_validate(e) for e in exams],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = ExamService(db)
    exam = await service.get_exam_by_id(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(
    exam_id: UUID,
    exam_data: ExamUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    service = ExamService(db)
    exam = await service.update_exam(exam_id, exam_data)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.patch("/{exam_id}/status", response_model=ExamResponse)
async def update_exam_status(
    exam_id: UUID,
    status: ExamStatus,
    db: AsyncSession = Depends(get_async_session)
):
    service = ExamService(db)
    exam = await service.update_exam_status(exam_id, status)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam


@router.delete("/{exam_id}", response_model=SuccessResponse)
async def delete_exam(
    exam_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = ExamService(db)
    success = await service.delete_exam(exam_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exam not found")
    return SuccessResponse(message="Exam deleted successfully")
