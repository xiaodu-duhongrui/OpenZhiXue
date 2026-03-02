import hashlib
import hmac
import time
import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.course import Lesson, LearningProgress, LearningStatus
from app.schemas.course import LearningProgressUpdate


class VideoService:
    def __init__(self, db: AsyncSession):
        self.db = db

    def generate_signed_url(
        self,
        video_url: str,
        lesson_id: uuid.UUID,
        student_id: uuid.UUID,
        expires_in: int = 3600,
    ) -> tuple[str, datetime]:
        expire_timestamp = int(time.time()) + expires_in
        expires_at = datetime.fromtimestamp(expire_timestamp)

        message = f"{lesson_id}:{student_id}:{expire_timestamp}"
        signature = hmac.new(
            settings.VIDEO_SIGNATURE_SECRET.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        separator = "&" if "?" in video_url else "?"
        signed_url = f"{video_url}{separator}token={signature}&expires={expire_timestamp}&lesson={lesson_id}&student={student_id}"

        return signed_url, expires_at

    def verify_signed_url(
        self,
        video_url: str,
        token: str,
        expires: int,
        lesson_id: uuid.UUID,
        student_id: uuid.UUID,
    ) -> bool:
        if int(time.time()) > expires:
            return False

        message = f"{lesson_id}:{student_id}:{expires}"
        expected_signature = hmac.new(
            settings.VIDEO_SIGNATURE_SECRET.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(token, expected_signature)

    async def get_video_play_info(
        self, lesson_id: uuid.UUID, student_id: uuid.UUID
    ) -> Optional[dict]:
        query = select(Lesson).where(Lesson.id == lesson_id)
        result = await self.db.execute(query)
        lesson = result.scalar_one_or_none()

        if not lesson or not lesson.video_url:
            return None

        signed_url, expires_at = self.generate_signed_url(
            lesson.video_url, lesson_id, student_id
        )

        return {
            "video_url": lesson.video_url,
            "signed_url": signed_url,
            "expires_at": expires_at,
            "duration": lesson.duration,
        }


class LearningProgressService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_progress(
        self, student_id: uuid.UUID, lesson_id: uuid.UUID
    ) -> LearningProgress:
        query = select(LearningProgress).where(
            and_(
                LearningProgress.student_id == student_id,
                LearningProgress.lesson_id == lesson_id,
            )
        )
        result = await self.db.execute(query)
        progress = result.scalar_one_or_none()

        if not progress:
            progress = LearningProgress(
                student_id=student_id,
                lesson_id=lesson_id,
                progress=0.0,
                status=LearningStatus.NOT_STARTED,
                last_position=0,
            )
            self.db.add(progress)
            await self.db.flush()
            await self.db.refresh(progress)

        return progress

    async def update_progress(
        self,
        student_id: uuid.UUID,
        lesson_id: uuid.UUID,
        progress_data: LearningProgressUpdate,
    ) -> Optional[LearningProgress]:
        progress = await self.get_or_create_progress(student_id, lesson_id)

        update_data = progress_data.model_dump(exclude_unset=True)

        if "progress" in update_data:
            progress.progress = update_data["progress"]
            if progress.progress > 0:
                progress.status = LearningStatus.IN_PROGRESS
            if progress.progress >= 100:
                progress.status = LearningStatus.COMPLETED
                progress.completed_at = datetime.utcnow()

        if "last_position" in update_data:
            progress.last_position = update_data["last_position"]

        if "status" in update_data:
            progress.status = update_data["status"]
            if progress.status == LearningStatus.COMPLETED:
                progress.completed_at = datetime.utcnow()
                progress.progress = 100.0

        progress.last_access_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(progress)
        return progress

    async def complete_lesson(
        self, student_id: uuid.UUID, lesson_id: uuid.UUID
    ) -> Optional[LearningProgress]:
        return await self.update_progress(
            student_id,
            lesson_id,
            LearningProgressUpdate(
                progress=100.0,
                status=LearningStatus.COMPLETED,
            ),
        )

    async def get_progress(
        self, student_id: uuid.UUID, lesson_id: uuid.UUID
    ) -> Optional[LearningProgress]:
        query = select(LearningProgress).where(
            and_(
                LearningProgress.student_id == student_id,
                LearningProgress.lesson_id == lesson_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_student_progress(
        self, student_id: uuid.UUID, course_id: Optional[uuid.UUID] = None
    ) -> list[LearningProgress]:
        query = select(LearningProgress).where(
            LearningProgress.student_id == student_id
        )

        if course_id:
            query = query.join(Lesson).join(Chapter).where(Chapter.course_id == course_id)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_course_progress(
        self, student_id: uuid.UUID, course_id: uuid.UUID
    ) -> dict:
        from app.models.course import Course, Chapter

        lessons_query = (
            select(Lesson)
            .join(Chapter)
            .where(Chapter.course_id == course_id)
        )
        lessons_result = await self.db.execute(lessons_query)
        lessons = lessons_result.scalars().all()

        total_lessons = len(lessons)
        total_duration = sum(lesson.duration or 0 for lesson in lessons)

        lesson_ids = [lesson.id for lesson in lessons]

        progress_query = select(LearningProgress).where(
            and_(
                LearningProgress.student_id == student_id,
                LearningProgress.lesson_id.in_(lesson_ids),
            )
        )
        progress_result = await self.db.execute(progress_query)
        progresses = progress_result.scalars().all()

        progress_map = {p.lesson_id: p for p in progresses}

        completed_lessons = 0
        in_progress_lessons = 0
        learned_duration = 0

        for lesson in lessons:
            progress = progress_map.get(lesson.id)
            if progress:
                if progress.status == LearningStatus.COMPLETED:
                    completed_lessons += 1
                    learned_duration += lesson.duration or 0
                elif progress.status == LearningStatus.IN_PROGRESS:
                    in_progress_lessons += 1
                    learned_duration += int(
                        (lesson.duration or 0) * (progress.progress / 100)
                    )

        progress_percentage = (
            (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        )

        return {
            "course_id": course_id,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "in_progress_lessons": in_progress_lessons,
            "total_duration": total_duration,
            "learned_duration": learned_duration,
            "progress_percentage": round(progress_percentage, 2),
        }

    async def get_student_stats(self, student_id: uuid.UUID) -> dict:
        from app.models.course import Course, Chapter

        all_progress = await self.get_student_progress(student_id)

        completed_lessons = sum(
            1 for p in all_progress if p.status == LearningStatus.COMPLETED
        )

        total_learning_time = 0
        course_ids = set()

        for progress in all_progress:
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

                chapter_query = select(Chapter).where(Chapter.id == lesson.chapter_id)
                chapter_result = await self.db.execute(chapter_query)
                chapter = chapter_result.scalar_one_or_none()
                if chapter:
                    course_ids.add(chapter.course_id)

        total_lessons = len(all_progress)
        average_progress = (
            sum(p.progress for p in all_progress) / len(all_progress)
            if all_progress
            else 0
        )

        courses_progress = []
        for course_id in course_ids:
            course_progress = await self.get_course_progress(student_id, course_id)
            courses_progress.append(course_progress)

        return {
            "student_id": student_id,
            "total_courses": len(course_ids),
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "total_learning_time": total_learning_time,
            "average_progress": round(average_progress, 2),
            "courses_progress": courses_progress,
        }
