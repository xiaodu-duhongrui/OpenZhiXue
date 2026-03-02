import pytest
from httpx import AsyncClient
from uuid import uuid4
from datetime import datetime, timedelta

from app.schemas.exam import ExamType


@pytest.mark.asyncio
async def test_create_exam(client: AsyncClient):
    exam_data = {
        "name": "2024年期中考试",
        "type": "midterm",
        "start_time": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "end_time": (datetime.utcnow() + timedelta(days=7, hours=3)).isoformat(),
        "grade_level": "高一",
        "semester": "2024春季学期",
    }
    
    response = await client.post("/api/v1/exams", json=exam_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == exam_data["name"]
    assert data["type"] == exam_data["type"]
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_get_exams(client: AsyncClient):
    exam_data = {
        "name": "2024年月考",
        "type": "monthly",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=2)).isoformat(),
    }
    
    await client.post("/api/v1/exams", json=exam_data)
    
    response = await client.get("/api/v1/exams")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_update_exam_status(client: AsyncClient):
    exam_data = {
        "name": "测试考试",
        "type": "daily",
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }
    
    create_response = await client.post("/api/v1/exams", json=exam_data)
    exam_id = create_response.json()["id"]
    
    response = await client.patch(
        f"/api/v1/exams/{exam_id}/status",
        params={"status": "scheduled"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "scheduled"
