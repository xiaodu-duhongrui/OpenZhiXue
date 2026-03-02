from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.class_model import ClassStatus
from app.models.student import StudentStatus
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse, ClassListResponse
from app.schemas.student import StudentResponse
from app.services.class_service import ClassService

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.get("", response_model=ClassListResponse)
async def get_classes(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    grade: Optional[int] = None,
    year: Optional[int] = None,
    status: Optional[ClassStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    service = ClassService(db)
    classes, total, page, page_size, total_pages = await service.get_classes(
        page=page,
        page_size=page_size,
        name=name,
        grade=grade,
        year=year,
        status=status,
    )
    return ClassListResponse(
        items=[ClassResponse.model_validate(c) for c in classes],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{class_id}", response_model=ClassResponse)
async def get_class(class_id: int, db: AsyncSession = Depends(get_db)):
    service = ClassService(db)
    class_ = await service.get_class_by_id(class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassResponse.model_validate(class_)


@router.post("", response_model=ClassResponse, status_code=201)
async def create_class(class_data: ClassCreate, db: AsyncSession = Depends(get_db)):
    service = ClassService(db)
    class_ = await service.create_class(class_data)
    return ClassResponse.model_validate(class_)


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = ClassService(db)
    class_ = await service.update_class(class_id, class_data)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    return ClassResponse.model_validate(class_)


@router.delete("/{class_id}", status_code=204)
async def delete_class(class_id: int, db: AsyncSession = Depends(get_db)):
    service = ClassService(db)
    deleted = await service.delete_class(class_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Class not found")
    return None


@router.get("/{class_id}/students", response_model=list[StudentResponse])
async def get_class_students(class_id: int, db: AsyncSession = Depends(get_db)):
    service = ClassService(db)
    class_ = await service.get_class_by_id(class_id)
    if not class_:
        raise HTTPException(status_code=404, detail="Class not found")
    students = await service.get_class_students(class_id)
    return [StudentResponse.model_validate(s) for s in students]
