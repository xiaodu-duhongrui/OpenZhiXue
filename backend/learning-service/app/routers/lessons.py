import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.course import (
    LearningProgressResponse,
    LearningProgressUpdate,
    VideoPlayResponse,
    CourseProgressResponse,
    StudentLearningStatsResponse,
    PaginatedResponse,
)
from app.services.course_service import CourseService
from app.services.learning_service import VideoService, LearningProgressService

router = APIRouter(prefix="/lessons", tags=["lessons"])


def get_video_service(db: AsyncSession = Depends(get_db)) -> VideoService:
    return VideoService(db)


def get_progress_service(
    db: AsyncSession = Depends(get_db),
) -> LearningProgressService:
    return LearningProgressService(db)


def get_course_service(db: AsyncSession = Depends(get_db)) -> CourseService:
    return CourseService(db)


@router.get("/{lesson_id}/video", response_model=VideoPlayResponse)
async def get_video_play_url(
    lesson_id: UUID,
    student_id: UUID = Query(..., description="学生ID"),
    video_service: VideoService = Depends(get_video_service),
    course_service: CourseService = Depends(get_course_service),
):
    lesson = await course_service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found",
        )

    if not lesson.video_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This lesson does not have a video",
        )

    play_info = await video_service.get_video_play_info(lesson_id, student_id)
    if not play_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    return VideoPlayResponse(**play_info)


@router.post("/{lesson_id}/progress", response_model=LearningProgressResponse)
async def update_lesson_progress(
    lesson_id: UUID,
    progress_data: LearningProgressUpdate,
    student_id: UUID = Query(..., description="学生ID"),
    progress_service: LearningProgressService = Depends(get_progress_service),
):
    progress = await progress_service.update_progress(
        student_id, lesson_id, progress_data
    )
    return progress


@router.get("/{lesson_id}/progress", response_model=LearningProgressResponse)
async def get_lesson_progress(
    lesson_id: UUID,
    student_id: UUID = Query(..., description="学生ID"),
    progress_service: LearningProgressService = Depends(get_progress_service),
):
    progress = await progress_service.get_progress(student_id, lesson_id)
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found",
        )
    return progress


@router.post("/{lesson_id}/complete", response_model=LearningProgressResponse)
async def complete_lesson(
    lesson_id: UUID,
    student_id: UUID = Query(..., description="学生ID"),
    progress_service: LearningProgressService = Depends(get_progress_service),
):
    progress = await progress_service.complete_lesson(student_id, lesson_id)
    return progress


@router.get("/{lesson_id}/verify-video")
async def verify_video_access(
    lesson_id: UUID,
    student_id: UUID = Query(..., description="学生ID"),
    token: str = Query(..., description="签名令牌"),
    expires: int = Query(..., description="过期时间戳"),
    video_service: VideoService = Depends(get_video_service),
    course_service: CourseService = Depends(get_course_service),
):
    lesson = await course_service.get_lesson_by_id(lesson_id)
    if not lesson or not lesson.video_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found",
        )

    is_valid = video_service.verify_signed_url(
        lesson.video_url, token, expires, lesson_id, student_id
    )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired video token",
        )

    return {"valid": True, "lesson_id": str(lesson_id)}
