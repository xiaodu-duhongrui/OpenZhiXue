from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_async_session
from app.services.analysis_service import AnalysisService
from app.schemas.analysis import (
    GradeStatisticsResponse, GradeRankingResponse,
    GradeTrendResponse, RadarChartResponse, ClassComparisonResponse
)

router = APIRouter(prefix="/grades", tags=["analysis"])


@router.get("/statistics", response_model=GradeStatisticsResponse)
async def get_statistics(
    exam_id: UUID = Query(...),
    subject_id: Optional[UUID] = Query(None),
    class_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    service = AnalysisService(db)
    statistics = await service.calculate_statistics(exam_id, subject_id, class_id)
    return statistics


@router.get("/rankings", response_model=GradeRankingResponse)
async def get_rankings(
    exam_id: UUID = Query(...),
    class_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_async_session)
):
    service = AnalysisService(db)
    rankings = await service.get_rankings(exam_id, class_id, page, page_size)
    return rankings


@router.get("/trends", response_model=GradeTrendResponse)
async def get_trends(
    student_id: UUID = Query(...),
    subject_id: Optional[UUID] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_session)
):
    service = AnalysisService(db)
    trends = await service.get_trends(student_id, subject_id, limit)
    return trends


@router.get("/radar-chart", response_model=RadarChartResponse)
async def get_radar_chart(
    student_id: UUID = Query(...),
    exam_id: UUID = Query(...),
    db: AsyncSession = Depends(get_async_session)
):
    service = AnalysisService(db)
    radar = await service.get_radar_chart(student_id, exam_id)
    return radar


@router.get("/class-comparison", response_model=ClassComparisonResponse)
async def get_class_comparison(
    exam_id: UUID = Query(...),
    subject_id: UUID = Query(...),
    db: AsyncSession = Depends(get_async_session)
):
    service = AnalysisService(db)
    comparison = await service.get_class_comparison(exam_id, subject_id)
    return comparison
