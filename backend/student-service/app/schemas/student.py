from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.student import Gender, StudentStatus


class StudentBase(BaseModel):
    student_no: str
    name: str
    gender: Gender = Gender.MALE
    birth_date: Optional[date] = None
    class_id: Optional[int] = None
    parent_id: Optional[int] = None
    status: StudentStatus = StudentStatus.ACTIVE


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    student_no: Optional[str] = None
    name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[date] = None
    class_id: Optional[int] = None
    parent_id: Optional[int] = None
    status: Optional[StudentStatus] = None


class StudentResponse(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class StudentListResponse(BaseModel):
    items: list[StudentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
