from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.class_model import ClassStatus


class ClassBase(BaseModel):
    name: str
    grade: int
    year: int
    head_teacher_id: Optional[int] = None
    status: ClassStatus = ClassStatus.ACTIVE


class ClassCreate(ClassBase):
    pass


class ClassUpdate(BaseModel):
    name: Optional[str] = None
    grade: Optional[int] = None
    year: Optional[int] = None
    head_teacher_id: Optional[int] = None
    status: Optional[ClassStatus] = None


class ClassResponse(ClassBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class ClassListResponse(BaseModel):
    items: list[ClassResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
