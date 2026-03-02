import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.student_service import StudentService
from app.models.student import Student, StudentStatus
from app.schemas.student import StudentCreate, StudentUpdate


@pytest.fixture
def mock_db():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def student_service(mock_db):
    return StudentService(mock_db)


@pytest.fixture
def sample_student():
    return Student(
        id=1,
        student_no="S2024001",
        name="张三",
        class_id=1,
        status=StudentStatus.ACTIVE,
    )


class TestStudentService:
    @pytest.mark.asyncio
    async def test_get_student_by_id(self, student_service, mock_db, sample_student):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_student
        mock_db.execute.return_value = mock_result

        result = await student_service.get_student_by_id(1)

        assert result == sample_student
        mock_db.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_student_by_id_not_found(self, student_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await student_service.get_student_by_id(999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_student_by_student_no(self, student_service, mock_db, sample_student):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_student
        mock_db.execute.return_value = mock_result

        result = await student_service.get_student_by_student_no("S2024001")

        assert result == sample_student

    @pytest.mark.asyncio
    async def test_create_student_success(self, student_service, mock_db):
        student_data = StudentCreate(
            student_no="S2024002",
            name="李四",
            class_id=1,
            status=StudentStatus.ACTIVE,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await student_service.create_student(student_data)

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_student_duplicate_student_no(self, student_service, mock_db, sample_student):
        student_data = StudentCreate(
            student_no="S2024001",
            name="李四",
            class_id=1,
            status=StudentStatus.ACTIVE,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_student
        mock_db.execute.return_value = mock_result

        with pytest.raises(ValueError, match="already exists"):
            await student_service.create_student(student_data)

    @pytest.mark.asyncio
    async def test_update_student_success(self, student_service, mock_db, sample_student):
        update_data = StudentUpdate(name="张三丰")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_student
        mock_db.execute.return_value = mock_result

        result = await student_service.update_student(1, update_data)

        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_student_not_found(self, student_service, mock_db):
        update_data = StudentUpdate(name="张三丰")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await student_service.update_student(999, update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_update_student_duplicate_student_no(self, student_service, mock_db, sample_student):
        existing_student = Student(
            id=2,
            student_no="S2024002",
            name="李四",
            class_id=1,
        )
        
        update_data = StudentUpdate(student_no="S2024002")

        mock_results = [
            MagicMock(),
            MagicMock(),
        ]
        mock_results[0].scalar_one_or_none.return_value = sample_student
        mock_results[1].scalar_one_or_none.return_value = existing_student
        mock_db.execute.side_effect = mock_results

        with pytest.raises(ValueError, match="already exists"):
            await student_service.update_student(1, update_data)

    @pytest.mark.asyncio
    async def test_delete_student_success(self, student_service, mock_db, sample_student):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_student
        mock_db.execute.return_value = mock_result

        result = await student_service.delete_student(1)

        assert result is True
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_student_not_found(self, student_service, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await student_service.delete_student(999)

        assert result is False
        mock_db.delete.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_students_with_filters(self, student_service, mock_db, sample_student):
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = [sample_student]
        
        mock_scalar_result = MagicMock()
        mock_scalar_result.return_value = 1

        mock_db.execute.return_value = mock_execute_result
        mock_db.scalar = mock_scalar_result

        students, total, page, page_size, total_pages = await student_service.get_students(
            page=1,
            page_size=10,
            name="张",
            status=StudentStatus.ACTIVE,
        )

        assert len(students) == 1
        assert total == 1
        assert page == 1
        assert page_size == 10

    @pytest.mark.asyncio
    async def test_get_students_pagination(self, student_service, mock_db):
        students = [Student(id=i, student_no=f"S{i}", name=f"学生{i}", class_id=1) for i in range(1, 6)]
        
        mock_execute_result = MagicMock()
        mock_execute_result.scalars.return_value.all.return_value = students
        
        mock_db.execute.return_value = mock_execute_result
        mock_db.scalar.return_value = 25

        result_students, total, page, page_size, total_pages = await student_service.get_students(
            page=2,
            page_size=5,
        )

        assert len(result_students) == 5
        assert total == 25
        assert page == 2
        assert page_size == 5
        assert total_pages == 5
