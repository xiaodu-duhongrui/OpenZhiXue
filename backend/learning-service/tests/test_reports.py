import uuid
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import (
    Course,
    Chapter,
    Lesson,
    LearningProgress,
    LearningReport,
    CourseStatus,
    LessonType,
    LearningStatus,
)


class TestReportAPI:
    @pytest.mark.asyncio
    async def test_generate_report(
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
            duration=1800,
        )
        db_session.add(lesson)
        await db_session.commit()
        await db_session.refresh(lesson)

        progress = LearningProgress(
            student_id=student_id,
            lesson_id=lesson.id,
            progress=100.0,
            status=LearningStatus.COMPLETED,
            last_access_at=datetime.utcnow(),
        )
        db_session.add(progress)
        await db_session.commit()

        response = await client.post(
            "/api/v1/reports/generate",
            params={
                "student_id": str(student_id),
                "report_type": "weekly",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == str(student_id)
        assert data["report_type"] == "weekly"
        assert data["total_lessons"] == 1
        assert data["completed_lessons"] == 1

    @pytest.mark.asyncio
    async def test_get_student_reports(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        student_id = uuid.uuid4()

        for i in range(3):
            report = LearningReport(
                student_id=student_id,
                report_type="weekly",
                total_lessons=10,
                completed_lessons=5 + i,
                total_duration=3600 * (i + 1),
                average_progress=50.0 + i * 10,
                start_date=datetime.utcnow() - timedelta(days=7 * (i + 1)),
                end_date=datetime.utcnow() - timedelta(days=7 * i),
            )
            db_session.add(report)
        await db_session.commit()

        response = await client.get(
            "/api/v1/reports",
            params={"student_id": str(student_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    @pytest.mark.asyncio
    async def test_get_learning_analysis(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        teacher_id = uuid.uuid4()
        student_id = uuid.uuid4()

        course = Course(
            name="数学课程",
            subject="数学",
            teacher_id=teacher_id,
        )
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
                progress=100.0 if i == 0 else 50.0,
                status=LearningStatus.COMPLETED if i == 0 else LearningStatus.IN_PROGRESS,
                last_access_at=datetime.utcnow() - timedelta(days=i),
            )
            db_session.add(progress)
        await db_session.commit()

        response = await client.get(f"/api/v1/reports/analysis/{student_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["student_id"] == str(student_id)
        assert data["total_lessons"] == 3
        assert data["completed_lessons"] == 1
        assert "daily_activity" in data
        assert "subject_distribution" in data
