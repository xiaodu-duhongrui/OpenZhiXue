from sqlalchemy import Column, String, Float, Boolean, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)
    code = Column(String(20), nullable=False, unique=True)
    total_score = Column(Float, default=100.0, nullable=False)
    pass_score = Column(Float, default=60.0, nullable=False)
    excellent_score = Column(Float, default=90.0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    grades = relationship("Grade", back_populates="subject")
    analyses = relationship("GradeAnalysis", back_populates="subject")
