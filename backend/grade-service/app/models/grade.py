from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Grade(Base):
    __tablename__ = "grades"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False, index=True)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False, index=True)
    score = Column(Float, nullable=False)
    rank = Column(Integer, nullable=True)
    class_rank = Column(Integer, nullable=True)
    grade_rank = Column(Integer, nullable=True)
    total_score = Column(Float, nullable=True)
    class_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('ix_grades_student_exam_subject', 'student_id', 'exam_id', 'subject_id', unique=True),
    )
    
    exam = relationship("Exam", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")
