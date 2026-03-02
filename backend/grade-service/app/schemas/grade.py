from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any


class GradeBase(BaseModel):
    student_id: UUID
    exam_id: UUID
    subject_id: UUID
    score: float = Field(..., ge=0)
    class_id: Optional[UUID] = None


class GradeCreate(GradeBase):
    pass


class GradeBatchCreate(BaseModel):
    grades: List[GradeCreate]


class GradeUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0)
    rank: Optional[int] = Field(None, ge=1)
    class_rank: Optional[int] = Field(None, ge=1)
    grade_rank: Optional[int] = Field(None, ge=1)


class GradeResponse(GradeBase):
    id: UUID
    rank: Optional[int] = None
    class_rank: Optional[int] = None
    grade_rank: Optional[int] = None
    total_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GradeListResponse(BaseModel):
    items: List[GradeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class GradeFilter(BaseModel):
    student_id: Optional[UUID] = None
    exam_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None
    class_id: Optional[UUID] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class GradeDetailResponse(GradeResponse):
    subject_name: Optional[str] = None
    exam_name: Optional[str] = None
    subject_total_score: Optional[float] = None
