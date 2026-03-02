from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any


class GradeAnalysisBase(BaseModel):
    exam_id: UUID
    subject_id: UUID
    class_id: Optional[UUID] = None


class GradeAnalysisResponse(GradeAnalysisBase):
    id: UUID
    avg_score: float
    max_score: float
    min_score: float
    median_score: Optional[float] = None
    std_deviation: Optional[float] = None
    pass_count: int
    pass_rate: float
    excellent_count: int
    excellent_rate: float
    total_count: int
    score_distribution: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class GradeStatisticsResponse(BaseModel):
    exam_id: UUID
    subject_id: Optional[UUID] = None
    class_id: Optional[UUID] = None
    
    avg_score: float
    max_score: float
    min_score: float
    median_score: float
    std_deviation: float
    
    pass_count: int
    pass_rate: float
    excellent_count: int
    excellent_rate: float
    fail_count: int
    fail_rate: float
    
    total_count: int
    score_distribution: Dict[str, int]
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_90: float


class GradeRankingItem(BaseModel):
    rank: int
    student_id: UUID
    student_name: Optional[str] = None
    class_name: Optional[str] = None
    total_score: float
    subject_scores: Dict[str, float]
    
    model_config = ConfigDict(from_attributes=True)


class GradeRankingResponse(BaseModel):
    exam_id: UUID
    class_id: Optional[UUID] = None
    rankings: List[GradeRankingItem]
    total: int
    page: int
    page_size: int


class GradeTrendItem(BaseModel):
    exam_id: UUID
    exam_name: str
    exam_date: datetime
    score: float
    rank: Optional[int] = None
    avg_score: float
    class_avg_score: Optional[float] = None


class GradeTrendResponse(BaseModel):
    student_id: UUID
    subject_id: Optional[UUID] = None
    subject_name: Optional[str] = None
    trends: List[GradeTrendItem]


class RadarChartItem(BaseModel):
    subject: str
    score: float
    avg_score: float
    max_score: float


class RadarChartResponse(BaseModel):
    student_id: UUID
    exam_id: UUID
    data: List[RadarChartItem]


class ClassComparisonItem(BaseModel):
    class_id: UUID
    class_name: str
    avg_score: float
    max_score: float
    min_score: float
    pass_rate: float
    excellent_rate: float
    student_count: int


class ClassComparisonResponse(BaseModel):
    exam_id: UUID
    subject_id: UUID
    subject_name: str
    classes: List[ClassComparisonItem]
