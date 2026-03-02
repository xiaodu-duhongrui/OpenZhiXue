from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_async_session
from app.services.subject_service import SubjectService
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_async_session)
):
    service = SubjectService(db)
    
    existing = await service.get_subject_by_code(subject_data.code)
    if existing:
        raise HTTPException(status_code=400, detail="Subject code already exists")
    
    subject = await service.create_subject(subject_data)
    return subject


@router.get("", response_model=List[SubjectResponse])
async def get_subjects(
    active_only: bool = True,
    db: AsyncSession = Depends(get_async_session)
):
    service = SubjectService(db)
    subjects = await service.get_all_subjects(active_only)
    return [SubjectResponse.model_validate(s) for s in subjects]


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = SubjectService(db)
    subject = await service.get_subject_by_id(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: UUID,
    subject_data: SubjectUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    service = SubjectService(db)
    subject = await service.update_subject(subject_id, subject_data)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.delete("/{subject_id}", response_model=SuccessResponse)
async def delete_subject(
    subject_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = SubjectService(db)
    success = await service.delete_subject(subject_id)
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return SuccessResponse(message="Subject deleted successfully")
