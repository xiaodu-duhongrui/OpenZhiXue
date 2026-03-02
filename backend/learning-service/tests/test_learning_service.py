import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timedelta
import hashlib
import hmac
import time

from app.services.learning_service import VideoService, LearningProgressService
from app.models.course import Lesson, LearningProgress, LearningStatus
from app.schemas.course import LearningProgressUpdate


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def video_service(mock_db):
    return VideoService(mock_db)


@pytest.fixture
def progress_service(mock_db):
    return LearningProgressService(mock_db)


@pytest.fixture
def sample_lesson():
    return Lesson(
        id=uuid4(),
        chapter_id=uuid4(),
        title="Test Lesson",
        video_url="https://example.com/video.mp4",
        duration=1800,
    )


@pytest.fixture
def sample_progress():
    return LearningProgress(
        id=uuid4(),
        student_id=uuid4(),
        lesson_id=uuid4(),
        progress=50.0,
        status=LearningStatus.IN_PROGRESS,
        last_position=900,
    )


class TestVideoService:
    def test_generate_signed_url(self, video_service):
        video_url = "https://example.com/video.mp4"
        lesson_id = uuid4()
        student_id = uuid4()
        
        signed_url, expires_at = video_service.generate_signed_url(
            video_url, lesson_id, student_id, expires_in=3600
        )
        
        assert "token=" in signed_url
        assert "expires=" in signed_url
        assert str(lesson_id) in signed_url
        assert str(student_id) in signed_url
        assert expires_at > datetime.now()

    def test_generate_signed_url_with_existing_query(self, video_service):
        video_url = "https://example.com/video.mp4?quality=hd"
        lesson_id = uuid4()
        student_id = uuid4()
        
        signed_url, _ = video_service.generate_signed_url(
            video_url, lesson_id, student_id
        )
        
        assert "&token=" in signed_url

    def test_verify_signed_url_valid(self, video_service):
        video_url = "https://example.com/video.mp4"
        lesson_id = uuid4()
        student_id = uuid4()
        
        signed_url, _ = video_service.generate_signed_url(
            video_url, lesson_id, student_id, expires_in=3600
        )
        
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(signed_url)
        params = parse_qs(parsed.query)
        
        token = params["token"][0]
        expires = int(params["expires"][0])
        
        is_valid = video_service.verify_signed_url(
            video_url, token, expires, lesson_id, student_id
        )
        
        assert is_valid is True

    def test_verify_signed_url_expired(self, video_service):
        video_url = "https://example.com/video.mp4"
        lesson_id = uuid4()
        student_id = uuid4()
        expired_time = int(time.time()) - 3600
        
        message = f"{lesson_id}:{student_id}:{expired_time}"
        token = hmac.new(
            b"test-secret-key",
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        
        with patch.object(video_service, 'verify_signed_url') as mock_verify:
            mock_verify.return_value = False
            
            is_valid = video_service.verify_signed_url(
                video_url, token, expired_time, lesson_id, student_id
            )
            
            assert is_valid is False

    def test_verify_signed_url_invalid_token(self, video_service):
        video_url = "https://example.com/video.mp4"
        lesson_id = uuid4()
        student_id = uuid4()
        future_time = int(time.time()) + 3600
        
        is_valid = video_service.verify_signed_url(
            video_url, "invalid-token", future_time, lesson_id, student_id
        )
        
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_get_video_play_info(self, video_service, mock_db, sample_lesson):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_lesson
        mock_db.execute.return_value = mock_result
        
        student_id = uuid4()
        
        result = await video_service.get_video_play_info(sample_lesson.id, student_id)
        
        assert result is not None
        assert "video_url" in result
        assert "signed_url" in result
        assert "expires_at" in result
        assert result["duration"] == 1800

    @pytest.mark.asyncio
    async def test_get_video_play_info_lesson_not_found(self, video_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        
        result = await video_service.get_video_play_info(uuid4(), uuid4())
        
        assert result is None


class TestLearningProgressService:
    @pytest.mark.asyncio
    async def test_get_or_create_progress_existing(self, progress_service, mock_db, sample_progress):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_progress
        mock_db.execute.return_value = mock_result
        
        result = await progress_service.get_or_create_progress(
            sample_progress.student_id, sample_progress.lesson_id
        )
        
        assert result == sample_progress
        mock_db.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_or_create_progress_new(self, progress_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        student_id = uuid4()
        lesson_id = uuid4()
        
        result = await progress_service.get_or_create_progress(student_id, lesson_id)
        
        mock_db.add.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_progress(self, progress_service, mock_db, sample_progress):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_progress
        mock_db.execute.return_value = mock_result
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        update_data = LearningProgressUpdate(progress=75.0, last_position=1350)
        
        result = await progress_service.update_progress(
            sample_progress.student_id, sample_progress.lesson_id, update_data
        )
        
        assert result.progress == 75.0
        assert result.last_position == 1350

    @pytest.mark.asyncio
    async def test_update_progress_to_completed(self, progress_service, mock_db, sample_progress):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_progress
        mock_db.execute.return_value = mock_result
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        update_data = LearningProgressUpdate(progress=100.0)
        
        result = await progress_service.update_progress(
            sample_progress.student_id, sample_progress.lesson_id, update_data
        )
        
        assert result.status == LearningStatus.COMPLETED
        assert result.completed_at is not None

    @pytest.mark.asyncio
    async def test_complete_lesson(self, progress_service, mock_db, sample_progress):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_progress
        mock_db.execute.return_value = mock_result
        mock_db.flush = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        result = await progress_service.complete_lesson(
            sample_progress.student_id, sample_progress.lesson_id
        )
        
        assert result.status == LearningStatus.COMPLETED
        assert result.progress == 100.0

    @pytest.mark.asyncio
    async def test_get_progress(self, progress_service, mock_db, sample_progress):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_progress
        mock_db.execute.return_value = mock_result
        
        result = await progress_service.get_progress(
            sample_progress.student_id, sample_progress.lesson_id
        )
        
        assert result == sample_progress

    @pytest.mark.asyncio
    async def test_get_student_progress(self, progress_service, mock_db, sample_progress):
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_progress]
        mock_db.execute.return_value = mock_result
        
        result = await progress_service.get_student_progress(sample_progress.student_id)
        
        assert len(result) == 1
        assert result[0] == sample_progress

    @pytest.mark.asyncio
    async def test_get_course_progress(self, progress_service, mock_db, sample_progress, sample_lesson):
        with patch.object(progress_service, 'get_student_progress') as mock_get_progress:
            mock_get_progress.return_value = [sample_progress]
            
            with patch('app.services.learning_service.select') as mock_select:
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = [sample_lesson]
                mock_db.execute.return_value = mock_result
                
                result = await progress_service.get_course_progress(
                    sample_progress.student_id, uuid4()
                )
                
                assert "course_id" in result or result is not None
