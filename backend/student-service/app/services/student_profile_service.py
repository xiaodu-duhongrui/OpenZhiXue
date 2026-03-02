import os
import uuid
from typing import Optional
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student_profile import StudentProfile
from app.schemas.student_profile import StudentProfileCreate, StudentProfileUpdate


class StudentProfileService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile_by_student_id(self, student_id: int):
        query = select(StudentProfile).where(StudentProfile.student_id == student_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_profile_by_id(self, profile_id: int):
        query = select(StudentProfile).where(StudentProfile.id == profile_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_profile(self, profile_data: StudentProfileCreate):
        existing = await self.get_profile_by_student_id(profile_data.student_id)
        if existing:
            raise ValueError(f"Profile for student_id '{profile_data.student_id}' already exists")

        profile = StudentProfile(**profile_data.model_dump())
        self.db.add(profile)
        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def update_profile(self, student_id: int, profile_data: StudentProfileUpdate):
        profile = await self.get_profile_by_student_id(student_id)
        if not profile:
            return None

        update_data = profile_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(profile, key, value)

        await self.db.commit()
        await self.db.refresh(profile)
        return profile

    async def upload_photo(self, student_id: int, file: UploadFile, upload_dir: str = "uploads/photos"):
        profile = await self.get_profile_by_student_id(student_id)
        if not profile:
            return None

        os.makedirs(upload_dir, exist_ok=True)

        file_ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        filename = f"{student_id}_{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(upload_dir, filename)

        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        profile.photo_url = f"/{upload_dir}/{filename}"
        await self.db.commit()
        await self.db.refresh(profile)

        return profile
