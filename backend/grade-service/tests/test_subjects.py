import pytest
from httpx import AsyncClient
from uuid import uuid4

from app.schemas.subject import SubjectCreate


@pytest.mark.asyncio
async def test_create_subject(client: AsyncClient):
    subject_data = {
        "name": "数学",
        "code": "MATH001",
        "total_score": 150.0,
        "pass_score": 90.0,
        "excellent_score": 135.0,
    }
    
    response = await client.post("/api/v1/subjects", json=subject_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == subject_data["name"]
    assert data["code"] == subject_data["code"]
    assert data["total_score"] == subject_data["total_score"]


@pytest.mark.asyncio
async def test_get_subjects(client: AsyncClient):
    subject_data = {
        "name": "语文",
        "code": "CHINESE001",
        "total_score": 150.0,
    }
    
    await client.post("/api/v1/subjects", json=subject_data)
    
    response = await client.get("/api/v1/subjects")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_subject_by_id(client: AsyncClient):
    subject_data = {
        "name": "英语",
        "code": "ENGLISH001",
        "total_score": 120.0,
    }
    
    create_response = await client.post("/api/v1/subjects", json=subject_data)
    subject_id = create_response.json()["id"]
    
    response = await client.get(f"/api/v1/subjects/{subject_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == subject_id
    assert data["name"] == subject_data["name"]
