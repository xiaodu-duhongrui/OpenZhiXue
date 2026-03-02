from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class GradeAnalysis(Base):
    __tablename__ = "grade_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False, index=True)
    class_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    avg_score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    min_score = Column(Float, nullable=False)
    median_score = Column(Float, nullable=True)
    std_deviation = Column(Float, nullable=True)
    
    pass_count = Column(Integer, default=0, nullable=False)
    pass_rate = Column(Float, nullable=False)
    excellent_count = Column(Integer, default=0, nullable=False)
    excellent_rate = Column(Float, nullable=False)
    
    total_count = Column(Integer, default=0, nullable=False)
    
    score_distribution = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('ix_grade_analyses_exam_subject_class', 'exam_id', 'subject_id', 'class_id', unique=True),
    )
    
    exam = relationship("Exam", back_populates="analyses")
    subject = relationship("Subject", back_populates="analyses")
