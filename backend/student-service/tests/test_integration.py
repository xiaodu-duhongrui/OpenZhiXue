import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

from app.main import app
from app.database import Base, get_db
from app.models.student import Student, StudentStatus
from app.models.class_model import Class


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_class(db_session):
    class_obj = Class(
        id=1,
        name="高三(1)班",
        grade=12,
    )
    db_session.add(class_obj)
    await db_session.commit()
    return class_obj


@pytest.mark.asyncio
class TestStudentAPIIntegration:
    async def test_create_student(self, client, sample_class):
        response = await client.post(
            "/api/students",
            json={
                "student_no": "S2024001",
                "name": "张三",
                "class_id": 1,
                "status": "active",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["student_no"] == "S2024001"
        assert data["name"] == "张三"

    async def test_create_duplicate_student(self, client, sample_class, db_session):
        student = Student(
            student_no="S2024002",
            name="李四",
            class_id=1,
            status=StudentStatus.ACTIVE,
        )
        db_session.add(student)
        await db_session.commit()
        
        response = await client.post(
            "/api/students",
            json={
                "student_no": "S2024002",
                "name": "王五",
                "class_id": 1,
            },
        )
        
        assert response.status_code == 400

    async def test_get_student(self, client, sample_class, db_session):
        student = Student(
            student_no="S2024003",
            name="王五",
            class_id=1,
            status=StudentStatus.ACTIVE,
        )
        db_session.add(student)
        await db_session.commit()
        await db_session.refresh(student)
        
        response = await client.get(f"/api/students/{student.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "王五"

    async def test_get_student_not_found(self, client):
        response = await client.get("/api/students/99999")
        
        assert response.status_code == 404

    async def test_list_students(self, client, sample_class, db_session):
        for i in range(5):
            student = Student(
                student_no=f"S20240{i+10}",
                name=f"学生{i}",
                class_id=1,
                status=StudentStatus.ACTIVE,
            )
            db_session.add(student)
        await db_session.commit()
        
        response = await client.get("/api/students?page=1&page_size=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    async def test_update_student(self, client, sample_class, db_session):
        student = Student(
            student_no="S2024020",
            name="原名字",
            class_id=1,
            status=StudentStatus.ACTIVE,
        )
        db_session.add(student)
        await db_session.commit()
        await db_session.refresh(student)
        
        response = await client.put(
            f"/api/students/{student.id}",
            json={"name": "新名字"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新名字"

    async def test_delete_student(self, client, sample_class, db_session):
        student = Student(
            student_no="S2024030",
            name="待删除",
            class_id=1,
            status=StudentStatus.ACTIVE,
        )
        db_session.add(student)
        await db_session.commit()
        await db_session.refresh(student)
        
        response = await client.delete(f"/api/students/{student.id}")
        
        assert response.status_code == 204
        
        result = await db_session.execute(
            select(Student).where(Student.id == student.id)
        )
        assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
class TestDatabaseIntegration:
    async def test_transaction_rollback(self, db_session):
        student = Student(
            student_no="S2024040",
            name="测试事务",
            class_id=1,
            status=StudentStatus.ACTIVE,
        )
        db_session.add(student)
        await db_session.flush()
        
        await db_session.rollback()
        
        result = await db_session.execute(
            select(Student).where(Student.student_no == "S2024040")
        )
        assert result.scalar_one_or_none() is None

    async def test_concurrent_operations(self, db_session):
        students = [
            Student(
                student_no=f"S20240{i+50}",
                name=f"并发测试{i}",
                class_id=1,
                status=StudentStatus.ACTIVE,
            )
            for i in range(10)
        ]
        
        for student in students:
            db_session.add(student)
        
        await db_session.commit()
        
        result = await db_session.execute(
            select(Student).where(Student.class_id == 1)
        )
        all_students = result.scalars().all()
        assert len(all_students) >= 10
