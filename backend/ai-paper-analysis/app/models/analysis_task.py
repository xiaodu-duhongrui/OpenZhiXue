from sqlalchemy import Column, String, DateTime, Text, Enum, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum
from app.database import Base


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileType(str, enum.Enum):
    """文件类型枚举"""
    PDF = "pdf"
    WORD = "word"


class AnalysisTask(Base):
    """试卷分析任务模型"""
    __tablename__ = "analysis_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(
        Enum(TaskStatus),
        default=TaskStatus.PENDING,
        nullable=False,
        index=True
    )
    file_path = Column(String(500), nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    original_filename = Column(String(255), nullable=False)
    extracted_text = Column(Text, nullable=True)
    analysis_result = Column(JSONB, nullable=True)
    similar_questions = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('ix_analysis_tasks_status_created', 'status', 'created_at'),
    )

    def __repr__(self):
        return f"<AnalysisTask(id={self.id}, status={self.status}, file={self.original_filename})>"

    def to_dict(self):
        """转换为字典"""
        return {
            "id": str(self.id),
            "status": self.status.value if self.status else None,
            "file_path": self.file_path,
            "file_type": self.file_type.value if self.file_type else None,
            "original_filename": self.original_filename,
            "extracted_text": self.extracted_text,
            "analysis_result": self.analysis_result,
            "similar_questions": self.similar_questions,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
