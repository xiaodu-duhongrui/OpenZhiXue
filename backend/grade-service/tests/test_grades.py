import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta


@pytest.fixture
async def setup_test_data(client: AsyncClient):
    subject_data = {
        "name": "数学",
        "code": "MATH_TEST",
        "total_score": 100.0,
    }
    subject_response = await client.post("/api/v1/subjects", json=subject_data)
    subject_id = subject_response.json()["id"]
    
    exam_data = {
        "name": "测试考试",
        "type": "daily",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }
    exam_response = await client.post("/api/v1/exams", json=exam_data)
    exam_id = exam_response.json()["id"]
    
    return {
        "subject_id": subject_id,
        "exam_id": exam_id,
        "student_id": str(uuid4()),
        "class_id": str(uuid4()),
    }


@pytest.mark.asyncio
async def test_create_grade(client: AsyncClient, setup_test_data):
    test_data = await setup_test_data
    
    grade_data = {
        "student_id": test_data["student_id"],
        "exam_id": test_data["exam_id"],
        "subject_id": test_data["subject_id"],
        "score": 85.5,
        "class_id": test_data["class_id"],
    }
    
    response = await client.post("/api/v1/grades", json=grade_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["score"] == grade_data["score"]
    assert data["student_id"] == grade_data["student_id"]


@pytest.mark.asyncio
async def test_get_grades(client: AsyncClient, setup_test_data):
    test_data = await setup_test_data
    
    grade_data = {
        "student_id": test_data["student_id"],
        "exam_id": test_data["exam_id"],
        "subject_id": test_data["subject_id"],
        "score": 90.0,
        "class_id": test_data["class_id"],
    }
    
    await client.post("/api/v1/grades", json=grade_data)
    
    response = await client.get("/api/v1/grades")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_grade_by_id(client: AsyncClient, setup_test_data):
    test_data = await setup_test_data
    
    grade_data = {
        "student_id": test_data["student_id"],
        "exam_id": test_data["exam_id"],
        "subject_id": test_data["subject_id"],
        "score": 95.0,
        "class_id": test_data["class_id"],
    }
    
    create_response = await client.post("/api/v1/grades", json=grade_data)
    grade_id = create_response.json()["id"]
    
    response = await client.get(f"/api/v1/grades/{grade_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == grade_id
    assert data["score"] == 95.0


@pytest.mark.asyncio
async def test_get_student_grades(client: AsyncClient, setup_test_data):
    test_data = await setup_test_data
    
    grade_data = {
        "student_id": test_data["student_id"],
        "exam_id": test_data["exam_id"],
        "subject_id": test_data["subject_id"],
        "score": 88.0,
        "class_id": test_data["class_id"],
    }
    
    await client.post("/api/v1/grades", json=grade_data)
    
    response = await client.get(f"/api/v1/students/{test_data['student_id']}/grades")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
