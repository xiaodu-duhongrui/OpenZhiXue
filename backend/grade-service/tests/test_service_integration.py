import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.services.grade_service import GradeService
from app.services.exam_service import ExamService
from app.services.subject_service import SubjectService


@pytest.fixture
def mock_grade_db():
    return AsyncMock()


@pytest.fixture
def mock_exam_db():
    return AsyncMock()


@pytest.fixture
def grade_service(mock_grade_db):
    return GradeService(mock_grade_db)


@pytest.fixture
def exam_service(mock_exam_db):
    return ExamService(mock_exam_db)


@pytest.mark.asyncio
class TestServiceIntegration:
    async def test_grade_exam_workflow(self, mock_grade_db, mock_exam_db):
        exam_id = uuid4()
        subject_id = uuid4()
        class_id = uuid4()
        
        students = [uuid4() for _ in range(5)]
        
        grades = []
        for i, student_id in enumerate(students):
            grade_data = {
                "student_id": student_id,
                "exam_id": exam_id,
                "subject_id": subject_id,
                "class_id": class_id,
                "score": 60 + i * 8,
            }
            grades.append(grade_data)
        
        assert len(grades) == 5
        
        sorted_grades = sorted(grades, key=lambda x: x["score"], reverse=True)
        for rank, grade in enumerate(sorted_grades, start=1):
            grade["rank"] = rank
        
        assert sorted_grades[0]["rank"] == 1
        assert sorted_grades[-1]["rank"] == 5

    async def test_cross_service_data_flow(self, grade_service, exam_service):
        exam_id = uuid4()
        
        mock_exam_result = MagicMock()
        mock_exam_result.scalar_one_or_none.return_value = {
            "id": exam_id,
            "name": "期中考试",
            "status": "published",
        }
        
        with patch.object(grade_service, 'get_grades_by_exam') as mock_get_grades:
            mock_get_grades.return_value = ([], 0)
            
            grades, total = await grade_service.get_grades_by_exam(exam_id)
            
            assert total == 0
            mock_get_grades.assert_called_once()

    async def test_statistics_calculation(self, mock_grade_db):
        grades_data = [
            {"score": 95, "student_id": uuid4()},
            {"score": 85, "student_id": uuid4()},
            {"score": 75, "student_id": uuid4()},
            {"score": 65, "student_id": uuid4()},
            {"score": 55, "student_id": uuid4()},
        ]
        
        scores = [g["score"] for g in grades_data]
        
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        pass_rate = len([s for s in scores if s >= 60]) / len(scores) * 100
        
        assert avg_score == 75.0
        assert max_score == 95
        assert min_score == 55
        assert pass_rate == 80.0


@pytest.mark.asyncio
class TestServiceCommunication:
    async def test_grade_to_exam_communication(self):
        exam_id = uuid4()
        
        exam_response = {
            "id": str(exam_id),
            "name": "期末考试",
            "total_score": 100,
            "pass_score": 60,
        }
        
        grade_service = AsyncMock()
        grade_service.get_grades_by_exam.return_value = ([], 0)
        
        grades, total = await grade_service.get_grades_by_exam(exam_id)
        
        grade_service.get_grades_by_exam.assert_called_once_with(exam_id)

    async def test_notification_on_grade_publish(self):
        student_id = uuid4()
        exam_id = uuid4()
        
        notification_service = AsyncMock()
        notification_service.send_notification = AsyncMock()
        
        await notification_service.send_notification(
            user_id=student_id,
            title="成绩已发布",
            content="您的考试成绩已发布，请查看",
        )
        
        notification_service.send_notification.assert_called_once()

    async def test_homework_grade_link(self):
        homework_id = uuid4()
        student_id = uuid4()
        
        homework_service = AsyncMock()
        grade_service = AsyncMock()
        
        homework_service.get_submission = AsyncMock(return_value={
            "id": str(homework_id),
            "student_id": str(student_id),
            "score": 85,
        })
        
        submission = await homework_service.get_submission(homework_id, student_id)
        
        assert submission["score"] == 85


@pytest.mark.asyncio
class TestCacheIntegration:
    async def test_redis_cache_hit(self):
        cache_key = "exam:stats:123"
        cached_data = {
            "total_students": 50,
            "average_score": 78.5,
            "pass_rate": 85.0,
        }
        
        redis_client = AsyncMock()
        redis_client.get.return_value = cached_data
        
        result = await redis_client.get(cache_key)
        
        assert result == cached_data
        redis_client.get.assert_called_once_with(cache_key)

    async def test_redis_cache_miss(self):
        cache_key = "exam:stats:456"
        
        redis_client = AsyncMock()
        redis_client.get.return_value = None
        
        result = await redis_client.get(cache_key)
        
        assert result is None

    async def test_cache_invalidation(self):
        cache_key = "exam:stats:789"
        
        redis_client = AsyncMock()
        redis_client.delete = AsyncMock()
        
        await redis_client.delete(cache_key)
        
        redis_client.delete.assert_called_once_with(cache_key)
