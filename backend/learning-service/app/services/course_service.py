import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course import (
    Course,
    Chapter,
    Lesson,
    Resource,
    LearningProgress,
    LearningReport,
    CourseStatus,
    ChapterStatus,
    LessonStatus,
    LearningStatus,
)
from app.schemas.course import (
    CourseCreate,
    CourseUpdate,
    ChapterCreate,
    ChapterUpdate,
    LessonCreate,
    LessonUpdate,
    ResourceCreate,
    LearningProgressCreate,
    LearningProgressUpdate,
    LearningReportCreate,
)


class CourseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_course(self, course_data: CourseCreate) -> Course:
        course = Course(**course_data.model_dump())
        self.db.add(course)
        await self.db.flush()
        await self.db.refresh(course)
        return course

    async def get_courses(
        self,
        teacher_id: Optional[uuid.UUID] = None,
        subject: Optional[str] = None,
        status: Optional[CourseStatus] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[Course], int]:
        query = select(Course)
        count_query = select(func.count(Course.id))

        if teacher_id:
            query = query.where(Course.teacher_id == teacher_id)
            count_query = count_query.where(Course.teacher_id == teacher_id)
        if subject:
            query = query.where(Course.subject == subject)
            count_query = count_query.where(Course.subject == subject)
        if status:
            query = query.where(Course.status == status)
            count_query = count_query.where(Course.status == status)

        query = query.order_by(Course.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        courses = result.scalars().all()

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        return list(courses), total

    async def get_course_by_id(self, course_id: uuid.UUID) -> Optional[Course]:
        query = (
            select(Course)
            .options(selectinload(Course.chapters).selectinload(Chapter.lessons))
            .where(Course.id == course_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_course(
        self, course_id: uuid.UUID, course_data: CourseUpdate
    ) -> Optional[Course]:
        course = await self.get_course_by_id(course_id)
        if not course:
            return None

        update_data = course_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(course, field, value)

        await self.db.flush()
        await self.db.refresh(course)
        return course

    async def delete_course(self, course_id: uuid.UUID) -> bool:
        course = await self.get_course_by_id(course_id)
        if not course:
            return False

        await self.db.delete(course)
        await self.db.flush()
        return True

    async def add_chapter(
        self, course_id: uuid.UUID, chapter_data: ChapterCreate
    ) -> Optional[Chapter]:
        course = await self.get_course_by_id(course_id)
        if not course:
            return None

        chapter = Chapter(course_id=course_id, **chapter_data.model_dump())
        self.db.add(chapter)
        await self.db.flush()
        await self.db.refresh(chapter)
        return chapter

    async def get_chapter_by_id(self, chapter_id: uuid.UUID) -> Optional[Chapter]:
        query = (
            select(Chapter)
            .options(selectinload(Chapter.lessons))
            .where(Chapter.id == chapter_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_chapter(
        self, chapter_id: uuid.UUID, chapter_data: ChapterUpdate
    ) -> Optional[Chapter]:
        chapter = await self.get_chapter_by_id(chapter_id)
        if not chapter:
            return None

        update_data = chapter_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chapter, field, value)

        await self.db.flush()
        await self.db.refresh(chapter)
        return chapter

    async def delete_chapter(self, chapter_id: uuid.UUID) -> bool:
        chapter = await self.get_chapter_by_id(chapter_id)
        if not chapter:
            return False

        await self.db.delete(chapter)
        await self.db.flush()
        return True

    async def add_lesson(
        self, chapter_id: uuid.UUID, lesson_data: LessonCreate
    ) -> Optional[Lesson]:
        chapter = await self.get_chapter_by_id(chapter_id)
        if not chapter:
            return None

        lesson = Lesson(chapter_id=chapter_id, **lesson_data.model_dump())
        self.db.add(lesson)
        await self.db.flush()
        await self.db.refresh(lesson)
        return lesson

    async def get_lesson_by_id(self, lesson_id: uuid.UUID) -> Optional[Lesson]:
        query = (
            select(Lesson)
            .options(selectinload(Lesson.resources))
            .where(Lesson.id == lesson_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_lesson(
        self, lesson_id: uuid.UUID, lesson_data: LessonUpdate
    ) -> Optional[Lesson]:
        lesson = await self.get_lesson_by_id(lesson_id)
        if not lesson:
            return None

        update_data = lesson_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lesson, field, value)

        await self.db.flush()
        await self.db.refresh(lesson)
        return lesson

    async def delete_lesson(self, lesson_id: uuid.UUID) -> bool:
        lesson = await self.get_lesson_by_id(lesson_id)
        if not lesson:
            return False

        await self.db.delete(lesson)
        await self.db.flush()
        return True

    async def add_resource(
        self, lesson_id: uuid.UUID, resource_data: ResourceCreate
    ) -> Optional[Resource]:
        lesson = await self.get_lesson_by_id(lesson_id)
        if not lesson:
            return None

        resource = Resource(lesson_id=lesson_id, **resource_data.model_dump())
        self.db.add(resource)
        await self.db.flush()
        await self.db.refresh(resource)
        return resource
