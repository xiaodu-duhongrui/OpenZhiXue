from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_async_session
from app.services.grade_service import GradeService
from app.schemas.grade import GradeListResponse, GradeResponse

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{student_id}/grades", response_model=GradeListResponse)
async def get_student_grades(
    student_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_session)
):
    service = GradeService(db)
    grades, total = await service.get_grades_by_student(student_id, page, page_size)
    
    total_pages = (total + page_size - 1) // page_size
    
    return GradeListResponse(
        items=[GradeResponse.model_validate(g) for g in grades],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
