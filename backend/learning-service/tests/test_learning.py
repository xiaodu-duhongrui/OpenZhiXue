import uuid
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import (
    Course,
    Chapter,
    Lesson,
    LearningProgress,
    CourseStatus,
    LessonType,
    LearningStatus,
)


class TestLearningProgressAPI:
    @pytest.mark.asyncio
    async def test_update_progress(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        teacher_id = uuid.uuid4()
        student_id = uuid.uuid4()

        course = Course(name="测试课程", teacher_id=teacher_id)
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        chapter = Chapter(course_id=course.id, title="第一章")
        db_session.add(chapter)
        await db_session.commit()
        await db_session.refresh(chapter)

        lesson = Lesson(
            chapter_id=chapter.id,
            title="第一课",
            type=LessonType.VIDEO,
            video_url="https://example.com/video.mp4",
            duration=1800,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        progress_data = {
            "progress": 50.0,
            "last_position": 900,
        }

        response = await client.post(
            f"/api/v1/lessons/{lesson.id}/progress",
            params={"student_id": str(student_id)},
            json=progress_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 50.0
        assert data["last_position"] == 900
        assert data["status"] == LearningStatus.IN_PROGRESS.value

    @pytest.mark.asyncio
    async def test_complete_lesson(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        teacher_id = uuid.uuid4()
        student_id = uuid.uuid4()

        course = Course(name="测试课程", teacher_id=teacher_id)
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        chapter = Chapter(course_id=course.id, title="第一章")
        db_session.add(chapter)
        await db_session.commit()
        await db_session.refresh(chapter)

        lesson = Lesson(
            chapter_id=chapter.id,
            title="第一课",
            type=LessonType.VIDEO,
            video_url="https://example.com/video.mp4",
            duration=1800,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        response = await client.post(
            f"/api/v1/lessons/{lesson.id}/complete",
            params={"student_id": str(student_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 100.0
        assert data["status"] == LearningStatus.COMPLETED.value
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_get_video_play_url(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        teacher_id = uuid.uuid4()
        student_id = uuid.uuid4()

        course = Course(name="测试课程", teacher_id=teacher_id)
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        chapter = Chapter(course_id=course.id, title="第一章")
        db_session.add(chapter)
        await db_session.commit()
        await db_session.refresh(chapter)

        lesson = Lesson(
            chapter_id=chapter.id,
            title="第一课",
            type=LessonType.VIDEO,
            video_url="https://example.com/video.mp4",
            duration=1800,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        response = await client.get(
            f"/api/v1/lessons/{lesson.id}/video",
            params={"student_id": str(student_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert "signed_url" in data
        assert "expires_at" in data
        assert data["duration"] == 1800

    @pytest.mark.asyncio
    async def test_get_student_progress(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        teacher_id = uuid.uuid4()
        student_id = uuid.uuid4()

        course = Course(name="测试课程", teacher_id=teacher_id)
        db_session.add(course)
        await db_session.commit()
        await db_session.refresh(course)

        chapter = Chapter(course_id=course.id, title="第一章")
        db_session.add(chapter)
        await db_session.commit()
        await db_session.refresh(chapter)

        for i in range(3):
            lesson = Lesson(
                chapter_id=chapter.id,
                title=f"第{i+1}课",
                type=LessonType.VIDEO,
                duration=1800,
            )
            db_session.add(lesson)
        await db_session.commit()

        lessons_result = await db_session.execute(
            "SELECT id FROM lessons WHERE chapter_id = :chapter_id",
            {"chapter_id": str(chapter.id)},
        )
        lessons = lessons_result.fetchall()

        for i, lesson_row in enumerate(lessons):
            progress = LearningProgress(
                student_id=student_id,
                lesson_id=lesson_row[0],
                progress=100.0 if i == 0 else 50.0 * i,
                status=LearningStatus.COMPLETED if i == 0 else LearningStatus.IN_PROGRESS,
            )
            db_session.add(progress)
        await db_session.commit()

        response = await client.get(f"/api/v1/students/{student_id}/progress")

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == str(student_id)
        assert "total_lessons" in data
        assert "completed_lessons" in data
