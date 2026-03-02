import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta


@pytest.fixture
async def setup_analysis_data(client: AsyncClient):
    subject_data = {
        "name": "物理",
        "code": "PHYSICS_ANALYSIS",
        "total_score": 100.0,
    }
    subject_response = await client.post("/api/v1/subjects", json=subject_data)
    subject_id = subject_response.json()["id"]
    
    exam_data = {
        "name": "分析测试考试",
        "type": "monthly",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
    }
    exam_response = await client.post("/api/v1/exams", json=exam_data)
    exam_id = exam_response.json()["id"]
    
    class_id = str(uuid4())
    
    for i in range(10):
        grade_data = {
            "student_id": str(uuid4()),
            "exam_id": exam_id,
            "subject_id": subject_id,
            "score": 50.0 + i * 5,
            "class_id": class_id,
        }
        await client.post("/api/v1/grades", json=grade_data)
    
    return {
        "subject_id": subject_id,
        "exam_id": exam_id,
        "class_id": class_id,
    }


@pytest.mark.asyncio
async def test_get_statistics(client: AsyncClient, setup_analysis_data):
    test_data = await setup_analysis_data
    
    response = await client.get(
        "/api/v1/grades/statistics",
        params={
            "exam_id": test_data["exam_id"],
            "subject_id": test_data["subject_id"],
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "avg_score" in data
    assert "max_score" in data
    assert "min_score" in data
    assert "pass_rate" in data
    assert "total_count" in data


@pytest.mark.asyncio
async def test_get_rankings(client: AsyncClient, setup_analysis_data):
    test_data = await setup_analysis_data
    
    response = await client.get(
        "/api/v1/grades/rankings",
        params={"exam_id": test_data["exam_id"]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "rankings" in data
    assert "total" in data
    assert len(data["rankings"]) >= 1


@pytest.mark.asyncio
async def test_get_class_comparison(client: AsyncClient, setup_analysis_data):
    test_data = await setup_analysis_data
    
    response = await client.get(
        "/api/v1/grades/class-comparison",
        params={
            "exam_id": test_data["exam_id"],
            "subject_id": test_data["subject_id"],
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "classes" in data
    assert "subject_name" in data
