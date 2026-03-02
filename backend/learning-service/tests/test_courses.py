import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course, Chapter, Lesson, CourseStatus, LessonType
from app.schemas.course import CourseCreate, ChapterCreate, LessonCreate


class TestCourseAPI:
    @pytest.mark.asyncio
    async def test_create_course(self, client: AsyncClient, db_session: AsyncSession):
        teacher_id = uuid.uuid4()
        course_data = {
            "name": "Python 入门课程",
            "description": "学习 Python 编程基础",
            "subject": "编程",
            "teacher_id": str(teacher_id),
        }

        response = await client.post("/api/v1/courses", json=course_data)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == course_data["name"]
        assert data["description"] == course_data["description"]
        assert data["subject"] == course_data["subject"]
        assert data["teacher_id"] == str(teacher_id)
        assert data["status"] == CourseStatus.DRAFT.value

    @pytest.mark.asyncio
    async def test_get_courses(self, client: AsyncClient, db_session: AsyncSession):
        teacher_id = uuid.uuid4()
        for i in range(3):
            course = Course(
                name=f"课程 {i}",
                description=f"描述 {i}",
                subject="数学",
                teacher_id=teacher_id,
                status=CourseStatus.PUBLISHED,
            )
            db_session.add(course)
        await db_session.commit()

        response = await client.get("/api/v1/courses")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    @pytest.mark.asyncio
    async def test_get_course_by_id(self, client: AsyncClient, db_session: AsyncSession):
        teacher_id = uuid.uuid4()
        course = Course(
            name="测试课程",
            description="测试描述",
            subject="物理",
            teacher_id=teacher_id,
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        response = await client.get(f"/api/v1/courses/{course.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "测试课程"
        assert data["id"] == str(course.id)

    @pytest.mark.asyncio
    async def test_update_course(self, client: AsyncClient, db_session: AsyncSession):
        teacher_id = uuid.uuid4()
        course = Course(
            name="原始课程名",
            description="原始描述",
            teacher_id=teacher_id,
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        update_data = {
            "name": "更新后的课程名",
            "status": CourseStatus.PUBLISHED.value,
        }

        response = await client.put(
            f"/api/v1/courses/{course.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的课程名"
        assert data["status"] == CourseStatus.PUBLISHED.value

    @pytest.mark.asyncio
    async def test_delete_course(self, client: AsyncClient, db_session: AsyncSession):
        teacher_id = uuid.uuid4()
        course = Course(
            name="待删除课程",
            teacher_id=teacher_id,
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        response = await client.delete(f"/api/v1/courses/{course.id}")

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_add_chapter(self, client: AsyncClient, db_session: AsyncSession):
        teacher_id = uuid.uuid4()
        course = Course(
            name="测试课程",
            teacher_id=teacher_id,
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        chapter_data = {
            "title": "第一章",
            "order": 1,
        }

        response = await client.post(
            f"/api/v1/courses/{course.id}/chapters", json=chapter_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "第一章"
        assert data["course_id"] == str(course.id)

    @pytest.mark.asyncio
    async def test_add_lesson(self, client: AsyncClient, db_session: AsyncSession):
        teacher_id = uuid.uuid4()
        course = Course(
            name="测试课程",
            teacher_id=teacher_id,
        )
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        chapter = Chapter(
            course_id=course.id,
            title="第一章",
            order=1,
        )
        db_session.add(chapter)
        await db_session.commit()
        await db_session.refresh(chapter)

        lesson_data = {
            "title": "第一课",
            "type": LessonType.VIDEO.value,
            "video_url": "https://example.com/video.mp4",
            "duration": 1800,
            "order": 1,
        }

        response = await client.post(
            f"/api/v1/courses/chapters/{chapter.id}/lessons", json=lesson_data
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "第一课"
        assert data["chapter_id"] == str(chapter.id)
