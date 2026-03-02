from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class ClassStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class Class(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    grade: Mapped[int] = mapped_column(Integer)
    year: Mapped[int] = mapped_column(Integer)
    head_teacher_id: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[ClassStatus] = mapped_column(SQLEnum(ClassStatus), default=ClassStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    students: Mapped[list["Student"]] = relationship("Student", back_populates="class_")
