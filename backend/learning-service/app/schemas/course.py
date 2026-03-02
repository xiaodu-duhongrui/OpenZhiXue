from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.course import (
    ChapterStatus,
    CourseStatus,
    LessonStatus,
    LessonType,
    LearningStatus,
    ResourceType,
)


class CourseBase(BaseModel):
    name: str = Field(..., max_length=255, description="课程名称")
    description: Optional[str] = Field(None, description="课程描述")
    subject: Optional[str] = Field(None, max_length=100, description="学科")
    cover_image: Optional[str] = Field(None, max_length=500, description="封面图片URL")


class CourseCreate(CourseBase):
    teacher_id: UUID = Field(..., description="教师ID")


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=100)
    cover_image: Optional[str] = Field(None, max_length=500)
    status: Optional[CourseStatus] = None


class CourseResponse(CourseBase):
    id: UUID
    teacher_id: UUID
    status: CourseStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    chapters: list["ChapterResponse"] = []


class ChapterBase(BaseModel):
    title: str = Field(..., max_length=255, description="章节标题")
    order: int = Field(default=0, ge=0, description="排序")


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    order: Optional[int] = Field(None, ge=0)
    status: Optional[ChapterStatus] = None


class ChapterResponse(ChapterBase):
    id: UUID
    course_id: UUID
    status: ChapterStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterDetailResponse(ChapterResponse):
    lessons: list["LessonResponse"] = []


class LessonBase(BaseModel):
    title: str = Field(..., max_length=255, description="课时标题")
    type: LessonType = Field(default=LessonType.VIDEO, description="课时类型")
    content: Optional[str] = Field(None, description="课时内容")
    video_url: Optional[str] = Field(None, max_length=500, description="视频URL")
    duration: Optional[int] = Field(None, ge=0, description="时长(秒)")
    order: int = Field(default=0, ge=0, description="排序")


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    type: Optional[LessonType] = None
    content: Optional[str] = None
    video_url: Optional[str] = Field(None, max_length=500)
    duration: Optional[int] = Field(None, ge=0)
    order: Optional[int] = Field(None, ge=0)
    status: Optional[LessonStatus] = None


class LessonResponse(LessonBase):
    id: UUID
    chapter_id: UUID
    status: LessonStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LessonDetailResponse(LessonResponse):
    resources: list["ResourceResponse"] = []


class ResourceBase(BaseModel):
    name: str = Field(..., max_length=255, description="资源名称")
    type: ResourceType = Field(default=ResourceType.OTHER, description="资源类型")
    url: str = Field(..., max_length=500, description="资源URL")
    size: Optional[int] = Field(None, ge=0, description="文件大小(字节)")


class ResourceCreate(ResourceBase):
    pass


class ResourceResponse(ResourceBase):
    id: UUID
    lesson_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LearningProgressBase(BaseModel):
    progress: float = Field(..., ge=0, le=100, description="进度百分比")
    last_position: int = Field(default=0, ge=0, description="最后播放位置(秒)")


class LearningProgressCreate(LearningProgressBase):
    student_id: UUID
    lesson_id: UUID


class LearningProgressUpdate(BaseModel):
    progress: Optional[float] = Field(None, ge=0, le=100)
    last_position: Optional[int] = Field(None, ge=0)
    status: Optional[LearningStatus] = None


class LearningProgressResponse(BaseModel):
    id: UUID
    student_id: UUID
    lesson_id: UUID
    progress: float
    status: LearningStatus
    last_position: int
    last_access_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoPlayResponse(BaseModel):
    video_url: str
    signed_url: str
    expires_at: datetime
    duration: Optional[int] = None


class CourseProgressResponse(BaseModel):
    course_id: UUID
    total_lessons: int
    completed_lessons: int
    in_progress_lessons: int
    total_duration: int
    learned_duration: int
    progress_percentage: float


class StudentLearningStatsResponse(BaseModel):
    student_id: UUID
    total_courses: int
    total_lessons: int
    completed_lessons: int
    total_learning_time: int
    average_progress: float
    courses_progress: list[CourseProgressResponse]


class LearningReportBase(BaseModel):
    student_id: UUID
    course_id: Optional[UUID] = None
    report_type: str = Field(default="weekly", description="报告类型: daily/weekly/monthly")
    start_date: datetime
    end_date: datetime


class LearningReportCreate(LearningReportBase):
    pass


class LearningReportResponse(BaseModel):
    id: UUID
    student_id: UUID
    course_id: Optional[UUID]
    report_type: str
    total_lessons: int
    completed_lessons: int
    total_duration: int
    average_progress: float
    start_date: datetime
    end_date: datetime
    generated_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


CourseDetailResponse.model_rebuild()
ChapterDetailResponse.model_rebuild()
LessonDetailResponse.model_rebuild()
