from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from enum import Enum


class ExamType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MIDTERM = "midterm"
    FINAL = "final"
    MOCK = "mock"


class ExamStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    PUBLISHED = "published"


class ExamBase(BaseModel):
    name: str = Field(..., max_length=200)
    type: ExamType = ExamType.DAILY
    start_time: datetime
    end_time: datetime
    grade_level: Optional[str] = Field(None, max_length=50)
    semester: Optional[str] = Field(None, max_length=50)
    school_id: Optional[UUID] = None
    description: Optional[str] = None
    total_score: Optional[float] = None


class ExamCreate(ExamBase):
    pass


class ExamUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    type: Optional[ExamType] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[ExamStatus] = None
    grade_level: Optional[str] = Field(None, max_length=50)
    semester: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    total_score: Optional[float] = None


class ExamResponse(ExamBase):
    id: UUID
    status: ExamStatus = ExamStatus.DRAFT
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ExamListResponse(BaseModel):
    items: List[ExamResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ExamFilter(BaseModel):
    type: Optional[ExamType] = None
    status: Optional[ExamStatus] = None
    grade_level: Optional[str] = None
    semester: Optional[str] = None
    school_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
