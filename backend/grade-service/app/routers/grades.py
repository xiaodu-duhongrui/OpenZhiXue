from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_async_session
from app.services.grade_service import GradeService
from app.schemas.grade import (
    GradeCreate, GradeBatchCreate, GradeUpdate, GradeResponse,
    GradeListResponse, GradeFilter, GradeDetailResponse
)
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("", response_model=GradeResponse, status_code=201)
async def create_grade(
    grade_data: GradeCreate,
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    grade = await service.create_grade(grade_data)
    return grade


@router.post("/batch", response_model=SuccessResponse, status_code=201)
async def batch_create_grades(
    grade_data: GradeBatchCreate,
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    grades = await service.batch_create_grades(grade_data)
    return SuccessResponse(
        message=f"Successfully created {len(grades)} grades",
        data={"created_count": len(grades)}
    )


@router.get("", response_model=GradeListResponse)
async def get_grades(
    student_id: Optional[UUID] = Query(None),
    exam_id: Optional[UUID] = Query(None),
    subject_id: Optional[UUID] = Query(None),
    class_id: Optional[UUID] = Query(None),
    min_score: Optional[float] = Query(None),
    max_score: Optional[float] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    filters = GradeFilter(
        student_id=student_id,
        exam_id=exam_id,
        subject_id=subject_id,
        class_id=class_id,
        min_score=min_score,
        max_score=max_score,
        page=page,
        page_size=page_size,
    )
    grades, total = await service.get_grades(filters)
    
    total_pages = (total + page_size - 1) // page_size
    
    return GradeListResponse(
        items=[GradeResponse.model_validate(g) for g in grades],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{grade_id}", response_model=GradeDetailResponse)
async def get_grade(
    grade_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    grade = await service.get_grade_by_id(grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    response = GradeDetailResponse.model_validate(grade)
    if grade.subject:
        response.subject_name = grade.subject.name
        response.subject_total_score = grade.subject.total_score
    if grade.exam:
        response.exam_name = grade.exam.name
    
    return response


@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: UUID,
    grade_data: GradeUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    grade = await service.update_grade(grade_id, grade_data)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    return grade


@router.delete("/{grade_id}", response_model=SuccessResponse)
async def delete_grade(
    grade_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    success = await service.delete_grade(grade_id)
    if not success:
        raise HTTPException(status_code=404, detail="Grade not found")
    return SuccessResponse(message="Grade deleted successfully")


@router.post("/{grade_id}/calculate-ranks", response_model=SuccessResponse)
async def calculate_ranks(
    grade_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    grade = await service.get_grade_by_id(grade_id)
    if not grade:
        raise HTTPException(status_code=404, detail="Grade not found")
    
    await service.calculate_ranks(grade.exam_id, grade.subject_id)
    return SuccessResponse(message="Ranks calculated successfully")
