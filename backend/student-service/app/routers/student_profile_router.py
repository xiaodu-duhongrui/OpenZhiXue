from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.student_profile import StudentProfileUpdate, StudentProfileResponse
from app.services.student_profile_service import StudentProfileService
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Student Profiles"])


@router.get("/{student_id}/profile", response_model=StudentProfileResponse)
async def get_student_profile(student_id: int, db: AsyncSession = Depends(get_db)):
    student_service = StudentService(db)
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    profile_service = StudentProfileService(db)
    profile = await profile_service.get_profile_by_student_id(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return StudentProfileResponse.model_validate(profile)


@router.put("/{student_id}/profile", response_model=StudentProfileResponse)
async def update_student_profile(
    student_id: int,
    profile_data: StudentProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    student_service = StudentService(db)
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    profile_service = StudentProfileService(db)
    profile = await profile_service.update_profile(student_id, profile_data)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return StudentProfileResponse.model_validate(profile)


@router.post("/{student_id}/profile/photo", response_model=StudentProfileResponse)
async def upload_student_photo(
    student_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    student_service = StudentService(db)
    student = await student_service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    profile_service = StudentProfileService(db)
    profile = await profile_service.get_profile_by_student_id(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    profile = await profile_service.upload_photo(student_id, file)
    return StudentProfileResponse.model_validate(profile)
