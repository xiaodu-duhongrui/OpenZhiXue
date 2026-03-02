import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.course import (
    CourseProgressResponse,
    StudentLearningStatsResponse,
    PaginatedResponse,
)
from app.services.learning_service import LearningProgressService

router = APIRouter(prefix="/students", tags=["students"])


def get_progress_service(
    db: AsyncSession = Depends(get_db),
) -> LearningProgressService:
    return LearningProgressService(db)


@router.get("/{student_id}/progress", response_model=StudentLearningStatsResponse)
async def get_student_learning_progress(
    student_id: UUID,
    progress_service: LearningProgressService = Depends(get_progress_service),
):
    stats = await progress_service.get_student_stats(student_id)
    return StudentLearningStatsResponse(**stats)


@router.get("/{student_id}/courses/{course_id}/progress", response_model=CourseProgressResponse)
async def get_course_learning_progress(
    student_id: UUID,
    course_id: UUID,
    progress_service: LearningProgressService = Depends(get_progress_service),
):
    progress = await progress_service.get_course_progress(student_id, course_id)
    return CourseProgressResponse(**progress)
