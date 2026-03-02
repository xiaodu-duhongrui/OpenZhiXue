from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

from app.database import get_async_session
from app.services.report_service import ReportService
from app.schemas.report import ReportCreate, ReportResponse, ReportListResponse
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/grades/reports", tags=["reports"])


@router.post("", response_model=SuccessResponse, status_code=201)
async def generate_report(
    report_data: ReportCreate,
    db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    result = await service.generate_report(report_data)
    
    if result.get("status") == "failed":
        raise HTTPException(
            status_code=500,
            detail=result.get("error_message", "Failed to generate report")
        )
    
    return SuccessResponse(
        message="Report generated successfully",
        data=result
    )


@router.get("/{report_id}", response_model=SuccessResponse)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    report = await service.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return SuccessResponse(data=report)


@router.get("/{report_id}/pdf")
async def export_report_pdf(
    report_id: UUID,
    db: AsyncSession = Depends(get_async_session)
):
    service = ReportService(db)
    report = await service.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    pdf_bytes = await service.export_to_pdf(report)
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=report_{report_id}.pdf"
        }
    )
