from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.student import StudentStatus
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=StudentListResponse)
async def get_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None,
    student_no: Optional[str] = None,
    class_id: Optional[int] = None,
    status: Optional[StudentStatus] = None,
    db: AsyncSession = Depends(get_db),
):
    service = StudentService(db)
    students, total, page, page_size, total_pages = await service.get_students(
        page=page,
        page_size=page_size,
        name=name,
        student_no=student_no,
        class_id=class_id,
        status=status,
    )
    return StudentListResponse(
        items=[StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    service = StudentService(db)
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return StudentResponse.model_validate(student)


@router.post("", response_model=StudentResponse, status_code=201)
async def create_student(student_data: StudentCreate, db: AsyncSession = Depends(get_db)):
    service = StudentService(db)
    try:
        student = await service.create_student(student_data)
        return StudentResponse.model_validate(student)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = StudentService(db)
    try:
        student = await service.update_student(student_id, student_data)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return StudentResponse.model_validate(student)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{student_id}", status_code=204)
async def delete_student(student_id: int, db: AsyncSession = Depends(get_db)):
    service = StudentService(db)
    deleted = await service.delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")
    return None
