from sqlalchemy import Column, String, DateTime, Enum, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid
from app.database import Base


class ExamType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MIDTERM = "midterm"
    FINAL = "final"
    MOCK = "mock"


class ExamStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    PUBLISHED = "published"


class Exam(Base):
    __tablename__ = "exams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    type = Column(Enum(ExamType), default=ExamType.DAILY, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(Enum(ExamStatus), default=ExamStatus.DRAFT, nullable=False)
    grade_level = Column(String(50), nullable=True)
    semester = Column(String(50), nullable=True)
    school_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    description = Column(Text, nullable=True)
    total_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    grades = relationship("Grade", back_populates="exam")
    analyses = relationship("GradeAnalysis", back_populates="exam")
