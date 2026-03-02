import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID
from datetime import datetime

from app.services.grade_service import GradeService
from app.models.grade import Grade
from app.schemas.grade import GradeCreate, GradeUpdate, GradeFilter, GradeBatchCreate


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def grade_service(mock_db):
    return GradeService(mock_db)


@pytest.fixture
def sample_grade():
    return Grade(
        id=uuid4(),
        student_id=uuid4(),
        exam_id=uuid4(),
        subject_id=uuid4(),
        class_id=uuid4(),
        score=85.5,
        rank=10,
        class_rank=3,
    )


class TestGradeService:
    @pytest.mark.asyncio
    async def test_create_grade(self, grade_service, mock_db):
        grade_data = GradeCreate(
            student_id=uuid4(),
            exam_id=uuid4(),
            subject_id=uuid4(),
            class_id=uuid4(),
            score=90.0,
        )

        result = await grade_service.create_grade(grade_data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_create_grades(self, grade_service, mock_db):
        exam_id = uuid4()
        subject_id = uuid4()
        class_id = uuid4()
        
        grade_data = GradeBatchCreate(
            grades=[
                GradeCreate(
                    student_id=uuid4(),
                    exam_id=exam_id,
                    subject_id=subject_id,
                    class_id=class_id,
                    score=85.0,
                ),
                GradeCreate(
                    student_id=uuid4(),
                    exam_id=exam_id,
                    subject_id=subject_id,
                    class_id=class_id,
                    score=90.0,
                ),
            ]
        )

        result = await grade_service.batch_create_grades(grade_data)

        mock_db.add_all.assert_called_once()
        mock_db.commit.assert_called_once()
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_grade_by_id(self, grade_service, mock_db, sample_grade):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_grade
        mock_db.execute.return_value = mock_result

        result = await grade_service.get_grade_by_id(sample_grade.id)

        assert result == sample_grade

    @pytest.mark.asyncio
    async def test_get_grade_by_id_not_found(self, grade_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await grade_service.get_grade_by_id(uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_grades_with_filters(self, grade_service, mock_db, sample_grade):
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = [sample_grade]
        
        mock_db.execute.return_value = mock_execute_result
        mock_db.scalar.return_value = 1

        filters = GradeFilter(
            student_id=sample_grade.student_id,
            page=1,
            page_size=10,
        )

        grades, total = await grade_service.get_grades(filters)

        assert len(grades) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_grades_by_student(self, grade_service, mock_db, sample_grade):
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = [sample_grade]
        
        mock_db.execute.return_value = mock_execute_result
        mock_db.scalar.return_value = 1

        grades, total = await grade_service.get_grades_by_student(
            sample_grade.student_id,
            page=1,
            page_size=20,
        )

        assert len(grades) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_grades_by_exam(self, grade_service, mock_db, sample_grade):
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = [sample_grade]
        
        mock_db.execute.return_value = mock_execute_result
        mock_db.scalar.return_value = 1

        grades, total = await grade_service.get_grades_by_exam(
            sample_grade.exam_id,
            page=1,
            page_size=20,
        )

        assert len(grades) == 1
        assert total == 1

    @pytest.mark.asyncio
    async def test_get_grades_by_exam_with_class_filter(self, grade_service, mock_db, sample_grade):
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = [sample_grade]
        
        mock_db.execute.return_value = mock_execute_result
        mock_db.scalar.return_value = 1

        grades, total = await grade_service.get_grades_by_exam(
            sample_grade.exam_id,
            class_id=sample_grade.class_id,
            page=1,
            page_size=20,
        )

        assert len(grades) == 1

    @pytest.mark.asyncio
    async def test_update_grade_success(self, grade_service, mock_db, sample_grade):
        update_data = GradeUpdate(score=95.0)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_grade
        mock_db.execute.return_value = mock_result

        result = await grade_service.update_grade(sample_grade.id, update_data)

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_grade_not_found(self, grade_service, mock_db):
        update_data = GradeUpdate(score=95.0)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await grade_service.update_grade(uuid4(), update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_grade_success(self, grade_service, mock_db, sample_grade):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_grade
        mock_db.execute.return_value = mock_result

        result = await grade_service.delete_grade(sample_grade.id)

        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_grade_not_found(self, grade_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await grade_service.delete_grade(uuid4())

        assert result is False

    @pytest.mark.asyncio
    async def test_calculate_ranks(self, grade_service, mock_db):
        exam_id = uuid4()
        subject_id = uuid4()
        class_id = uuid4()
        
        grades = [
            Grade(id=uuid4(), student_id=uuid4(), exam_id=exam_id, subject_id=subject_id, 
                  class_id=class_id, score=95.0),
            Grade(id=uuid4(), student_id=uuid4(), exam_id=exam_id, subject_id=subject_id, 
                  class_id=class_id, score=85.0),
            Grade(id=uuid4(), student_id=uuid4(), exam_id=exam_id, subject_id=subject_id, 
                  class_id=class_id, score=90.0),
        ]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = grades
        mock_db.execute.return_value = mock_result

        await grade_service.calculate_ranks(exam_id, subject_id)

        mock_db.commit.assert_called_once()
        
        assert grades[0].rank == 1
        assert grades[1].rank == 3
        assert grades[2].rank == 2
