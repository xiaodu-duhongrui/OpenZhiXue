import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import (
    Course,
    Chapter,
    Lesson,
    LearningProgress,
    LearningReport,
    LearningStatus,
)
from app.schemas.course import LearningReportCreate


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_report(
        self,
        student_id: uuid.UUID,
        report_type: str = "weekly",
        course_id: Optional[uuid.UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> LearningReport:
        if not start_date or not end_date:
            if report_type == "daily":
                start_date = datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                end_date = start_date + timedelta(days=1)
            elif report_type == "weekly":
                today = datetime.utcnow()
                start_date = today - timedelta(days=today.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = start_date + timedelta(days=7)
            else:
                today = datetime.utcnow()
                start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if today.month == 12:
                    end_date = today.replace(
                        year=today.year + 1, month=1, day=1
                    )
                else:
                    end_date = today.replace(month=today.month + 1, day=1)

        query = select(LearningProgress).where(
            and_(
                LearningProgress.student_id == student_id,
                LearningProgress.last_access_at >= start_date,
                LearningProgress.last_access_at < end_date,
            )
        )

        if course_id:
            query = query.join(Lesson).join(Chapter).where(Chapter.course_id == course_id)

        result = await self.db.execute(query)
        progresses = result.scalars().all()

        total_lessons = len(progresses)
        completed_lessons = sum(
            1 for p in progresses if p.status == LearningStatus.COMPLETED
        )

        total_duration = 0
        for progress in progresses:
            lesson_query = select(Lesson).where(Lesson.id == progress.lesson_id)
            lesson_result = await self.db.execute(lesson_query)
            lesson = lesson_result.scalar_one_or_none()
            if lesson:
                if progress.status == LearningStatus.COMPLETED:
                    total_duration += lesson.duration or 0
                else:
                    total_duration += int(
                        (lesson.duration or 0) * (progress.progress / 100)
                    )

        average_progress = (
            sum(p.progress for p in progresses) / len(progresses)
            if progresses
            else 0
        )

        report = LearningReport(
            student_id=student_id,
            course_id=course_id,
            report_type=report_type,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            total_duration=total_duration,
            average_progress=round(average_progress, 2),
            start_date=start_date,
            end_date=end_date,
        )

        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)

        return report

    async def get_student_reports(
        self,
        student_id: uuid.UUID,
        report_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> tuple[list[LearningReport], int]:
        query = select(LearningReport).where(LearningReport.student_id == student_id)
        count_query = select(func.count(LearningReport.id)).where(
            LearningReport.student_id == student_id
        )

        if report_type:
            query = query.where(LearningReport.report_type == report_type)
            count_query = count_query.where(LearningReport.report_type == report_type)

        query = query.order_by(LearningReport.generated_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        reports = result.scalars().all()

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        return list(reports), total

    async def get_report_by_id(self, report_id: uuid.UUID) -> Optional[LearningReport]:
        query = select(LearningReport).where(LearningReport.id == report_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def analyze_learning_data(
        self,
        student_id: uuid.UUID,
        course_id: Optional[uuid.UUID] = None,
    ) -> dict:
        progress_query = select(LearningProgress).where(
            LearningProgress.student_id == student_id
        )

        if course_id:
            progress_query = progress_query.join(Lesson).join(Chapter).where(
                Chapter.course_id == course_id
            )

        progress_result = await self.db.execute(progress_query)
        progresses = progress_result.scalars().all()

        total_lessons = len(progresses)
        if total_lessons == 0:
            return {
                "student_id": student_id,
                "total_lessons": 0,
                "completed_lessons": 0,
                "completion_rate": 0,
                "average_progress": 0,
                "total_learning_time": 0,
                "daily_activity": [],
                "subject_distribution": {},
            }

        completed_lessons = sum(
            1 for p in progresses if p.status == LearningStatus.COMPLETED
        )
        completion_rate = completed_lessons / total_lessons * 100
        average_progress = sum(p.progress for p in progresses) / total_lessons

        total_learning_time = 0
        for progress in progresses:
            lesson_query = select(Lesson).where(Lesson.id == progress.lesson_id)
            lesson_result = await self.db.execute(lesson_query)
            lesson = lesson_result.scalar_one_or_none()
            if lesson:
                if progress.status == LearningStatus.COMPLETED:
                    total_learning_time += lesson.duration or 0
                else:
                    total_learning_time += int(
                        (lesson.duration or 0) * (progress.progress / 100)
                    )

        daily_activity = {}
        for progress in progresses:
            if progress.last_access_at:
                date_key = progress.last_access_at.strftime("%Y-%m-%d")
                daily_activity[date_key] = daily_activity.get(date_key, 0) + 1

        daily_activity_list = [
            {"date": date, "count": count}
            for date, count in sorted(daily_activity.items())
        ]

        subject_distribution = {}
        if not course_id:
            for progress in progresses:
                lesson_query = select(Lesson).where(Lesson.id == progress.lesson_id)
                lesson_result = await self.db.execute(lesson_query)
                lesson = lesson_result.scalar_one_or_none()
                if lesson:
                    chapter_query = select(Chapter).where(Chapter.id == lesson.chapter_id)
                    chapter_result = await self.db.execute(chapter_query)
                    chapter = chapter_result.scalar_one_or_none()
                    if chapter:
                        course_query = select(Course).where(Course.id == chapter.course_id)
                        course_result = await self.db.execute(course_query)
                        course = course_result.scalar_one_or_none()
                        if course and course.subject:
                            subject_distribution[course.subject] = (
                                subject_distribution.get(course.subject, 0) + 1
                            )

        return {
            "student_id": student_id,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "completion_rate": round(completion_rate, 2),
            "average_progress": round(average_progress, 2),
            "total_learning_time": total_learning_time,
            "daily_activity": daily_activity_list,
            "subject_distribution": subject_distribution,
        }
