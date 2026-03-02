from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from uuid import UUID

from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


class SubjectService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        subject = Subject(
            name=subject_data.name,
            code=subject_data.code,
            total_score=subject_data.total_score,
            pass_score=subject_data.pass_score,
            excellent_score=subject_data.excellent_score,
            sort_order=subject_data.sort_order,
        )
        self.db.add(subject)
        await self.db.commit()
        await self.db.refresh(subject)
        return subject
    
    async def get_subject_by_id(self, subject_id: UUID) -> Optional[Subject]:
        result = await self.db.execute(
            select(Subject).where(Subject.id == subject_id)
        )
        return result.scalar_one_or_none()
    
    async def get_subject_by_code(self, code: str) -> Optional[Subject]:
        result = await self.db.execute(
            select(Subject).where(Subject.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_all_subjects(self, active_only: bool = True) -> List[Subject]:
        query = select(Subject)
        if active_only:
            query = query.where(Subject.is_active == True)
        query = query.order_by(Subject.sort_order, Subject.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_subject(self, subject_id: UUID, subject_data: SubjectUpdate) -> Optional[Subject]:
        subject = await self.get_subject_by_id(subject_id)
        if not subject:
            return None
        
        update_data = subject_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(subject, field, value)
        
        await self.db.commit()
        await self.db.refresh(subject)
        return subject
    
    async def delete_subject(self, subject_id: UUID) -> bool:
        subject = await self.get_subject_by_id(subject_id)
        if not subject:
            return False
        
        subject.is_active = False
        await self.db.commit()
        return True
