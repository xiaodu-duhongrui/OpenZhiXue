from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from enum import Enum


class ReportType(str, Enum):
    STUDENT = "student"
    CLASS = "class"
    EXAM = "exam"
    SUBJECT = "subject"


class ReportStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class ReportCreate(BaseModel):
    report_type: ReportType
    exam_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    class_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None
    include_analysis: bool = True
    include_rankings: bool = True
    include_trends: bool = False


class ReportResponse(BaseModel):
    id: UUID
    report_type: ReportType
    status: ReportStatus
    exam_id: Optional[UUID] = None
    student_id: Optional[UUID] = None
    class_id: Optional[UUID] = None
    subject_id: Optional[UUID] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    items: List[ReportResponse]
    total: int
    page: int
    page_size: int


class StudentReportData(BaseModel):
    student_id: UUID
    student_name: str
    class_name: str
    exam_name: str
    exam_date: datetime
    
    total_score: float
    total_rank: int
    total_students: int
    
    subject_scores: List[Dict[str, Any]]
    radar_chart_data: List[Dict[str, Any]]
    
    class_avg_score: float
    grade_avg_score: float
    
    strengths: List[str]
    weaknesses: List[str]
    
    trend_data: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None


class ClassReportData(BaseModel):
    class_id: UUID
    class_name: str
    exam_name: str
    exam_date: datetime
    
    total_students: int
    avg_total_score: float
    
    subject_analyses: List[Dict[str, Any]]
    
    score_distribution: Dict[str, int]
    rank_distribution: Dict[str, int]
    
    top_students: List[Dict[str, Any]]
    improvement_students: List[Dict[str, Any]]
    
    comparison_with_grade: Dict[str, Any]
