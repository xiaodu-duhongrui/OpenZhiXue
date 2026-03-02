from datetime import date, datetime
from sqlalchemy import String, Date, DateTime, Integer, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class StudentStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    GRADUATED = "graduated"
    TRANSFERRED = "transferred"


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    student_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[Gender] = mapped_column(SQLEnum(Gender), default=Gender.MALE)
    birth_date: Mapped[date] = mapped_column(Date, nullable=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"), nullable=True)
    parent_id: Mapped[int] = mapped_column(Integer, nullable=True)
    status: Mapped[StudentStatus] = mapped_column(SQLEnum(StudentStatus), default=StudentStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile: Mapped["StudentProfile"] = relationship("StudentProfile", back_populates="student", uselist=False)
    class_: Mapped["Class"] = relationship("Class", back_populates="students")
