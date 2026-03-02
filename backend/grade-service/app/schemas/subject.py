from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class SubjectBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    total_score: float = Field(default=100.0, ge=0)
    pass_score: float = Field(default=60.0, ge=0)
    excellent_score: float = Field(default=90.0, ge=0)
    sort_order: int = Field(default=0, ge=0)


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=20)
    total_score: Optional[float] = Field(None, ge=0)
    pass_score: Optional[float] = Field(None, ge=0)
    excellent_score: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    sort_order: Optional[int] = Field(None, ge=0)


class SubjectResponse(SubjectBase):
    id: UUID
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class SubjectListResponse(BaseModel):
    items: List[SubjectResponse]
    total: int
