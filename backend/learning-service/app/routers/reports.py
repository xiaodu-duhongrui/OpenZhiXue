import math
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.course import (
    LearningReportResponse,
    PaginatedResponse,
)
from app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_report_service(db: AsyncSession = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.post("/generate", response_model=LearningReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_learning_report(
    student_id: UUID = Query(..., description="学生ID"),
    report_type: str = Query("weekly", description="报告类型: daily/weekly/monthly"),
    course_id: Optional[UUID] = Query(None, description="课程ID(可选)"),
    report_service: ReportService = Depends(get_report_service),
):
    report = await report_service.generate_report(
        student_id=student_id,
        report_type=report_type,
        course_id=course_id,
    )
    return report


@router.get("/{report_id}", response_model=LearningReportResponse)
async def get_report(
    report_id: UUID,
    report_service: ReportService = Depends(get_report_service),
):
    report = await report_service.get_report_by_id(report_id)
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with id {report_id} not found",
        )
    return report


@router.get("", response_model=PaginatedResponse)
async def get_student_reports(
    student_id: UUID = Query(..., description="学生ID"),
    report_type: Optional[str] = Query(None, description="报告类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    report_service: ReportService = Depends(get_report_service),
):
    reports, total = await report_service.get_student_reports(
        student_id=student_id,
        report_type=report_type,
        page=page,
        page_size=page_size,
    )
    return PaginatedResponse(
        items=[LearningReportResponse.model_validate(r) for r in reports],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/analysis/{student_id}")
async def get_learning_analysis(
    student_id: UUID,
    course_id: Optional[UUID] = Query(None, description="课程ID(可选)"),
    report_service: ReportService = Depends(get_report_service),
):
    analysis = await report_service.analyze_learning_data(student_id, course_id)
    return analysis
