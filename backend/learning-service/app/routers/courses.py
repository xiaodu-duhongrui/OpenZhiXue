import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.course import CourseStatus
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseDetailResponse,
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    ChapterDetailResponse,
    LessonCreate,
    LessonUpdate,
    LessonResponse,
    LessonDetailResponse,
    ResourceCreate,
    ResourceResponse,
    PaginatedResponse,
)
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


def get_course_service(db: AsyncSession = Depends(get_db)) -> CourseService:
    return CourseService(db)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    service: CourseService = Depends(get_course_service),
):
    course = await service.create_course(course_data)
    return course


@router.get("", response_model=PaginatedResponse)
async def get_courses(
    teacher_id: Optional[UUID] = Query(None, description="教师ID筛选"),
    subject: Optional[str] = Query(None, description="学科筛选"),
    status: Optional[CourseStatus] = Query(None, description="状态筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    service: CourseService = Depends(get_course_service),
):
    courses, total = await service.get_courses(
        teacher_id=teacher_id,
        subject=subject,
        status=status,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[CourseResponse.model_validate(c) for c in courses],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course(
    course_id: UUID,
    service: CourseService = Depends(get_course_service),
):
    course = await service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found",
        )
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: UUID,
    course_data: CourseUpdate,
    service: CourseService = Depends(get_course_service),
):
    course = await service.update_course(course_id, course_data)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found",
        )
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: UUID,
    service: CourseService = Depends(get_course_service),
):
    deleted = await service.delete_course(course_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found",
        )


@router.post(
    "/{course_id}/chapters",
    response_model=ChapterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_chapter(
    course_id: UUID,
    chapter_data: ChapterCreate,
    service: CourseService = Depends(get_course_service),
):
    chapter = await service.add_chapter(course_id, chapter_data)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found",
        )
    return chapter


@router.get("/chapters/{chapter_id}", response_model=ChapterDetailResponse)
async def get_chapter(
    chapter_id: UUID,
    service: CourseService = Depends(get_course_service),
):
    chapter = await service.get_chapter_by_id(chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id {chapter_id} not found",
        )
    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: UUID,
    chapter_data: ChapterUpdate,
    service: CourseService = Depends(get_course_service),
):
    chapter = await service.update_chapter(chapter_id, chapter_data)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id {chapter_id} not found",
        )
    return chapter


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    chapter_id: UUID,
    service: CourseService = Depends(get_course_service),
):
    deleted = await service.delete_chapter(chapter_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id {chapter_id} not found",
        )


@router.post(
    "/chapters/{chapter_id}/lessons",
    response_model=LessonResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_lesson(
    chapter_id: UUID,
    lesson_data: LessonCreate,
    service: CourseService = Depends(get_course_service),
):
    lesson = await service.add_lesson(chapter_id, lesson_data)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter with id {chapter_id} not found",
        )
    return lesson


@router.get("/lessons/{lesson_id}", response_model=LessonDetailResponse)
async def get_lesson(
    lesson_id: UUID,
    service: CourseService = Depends(get_course_service),
):
    lesson = await service.get_lesson_by_id(lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found",
        )
    return lesson


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
async def update_lesson(
    lesson_id: UUID,
    lesson_data: LessonUpdate,
    service: CourseService = Depends(get_course_service),
):
    lesson = await service.update_lesson(lesson_id, lesson_data)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found",
        )
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lesson(
    lesson_id: UUID,
    service: CourseService = Depends(get_course_service),
):
    deleted = await service.delete_lesson(lesson_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found",
        )


@router.post(
    "/lessons/{lesson_id}/resources",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_resource(
    lesson_id: UUID,
    resource_data: ResourceCreate,
    service: CourseService = Depends(get_course_service),
):
    resource = await service.add_resource(lesson_id, resource_data)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found",
        )
    return resource
