from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class StudentProfileBase(BaseModel):
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    medical_info: Optional[str] = None
    photo_url: Optional[str] = None


class StudentProfileCreate(StudentProfileBase):
    student_id: int


class StudentProfileUpdate(StudentProfileBase):
    pass


class StudentProfileResponse(StudentProfileBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    student_id: int
    created_at: datetime
    updated_at: datetime
