from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from app.models.exam import Exam, ExamType, ExamStatus
from app.schemas.exam import ExamCreate, ExamUpdate, ExamFilter


class ExamService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_exam(self, exam_data: ExamCreate) -> Exam:
        exam = Exam(
            name=exam_data.name,
            type=exam_data.type,
            start_time=exam_data.start_time,
            end_time=exam_data.end_time,
            grade_level=exam_data.grade_level,
            semester=exam_data.semester,
            school_id=exam_data.school_id,
            description=exam_data.description,
            total_score=exam_data.total_score,
        )
        self.db.add(exam)
        await self.db.commit()
        await self.db.refresh(exam)
        return exam
    
    async def get_exam_by_id(self, exam_id: UUID) -> Optional[Exam]:
        result = await self.db.execute(
            select(Exam).where(Exam.id == exam_id)
        )
        return result.scalar_one_or_none()
    
    async def get_exams(self, filters: ExamFilter) -> Tuple[List[Exam], int]:
        query = select(Exam)
        
        conditions = []
        if filters.type:
            conditions.append(Exam.type == filters.type)
        if filters.status:
            conditions.append(Exam.status == filters.status)
        if filters.grade_level:
            conditions.append(Exam.grade_level == filters.grade_level)
        if filters.semester:
            conditions.append(Exam.semester == filters.semester)
        if filters.school_id:
            conditions.append(Exam.school_id == filters.school_id)
        if filters.start_date:
            conditions.append(Exam.start_time >= filters.start_date)
        if filters.end_date:
            conditions.append(Exam.end_time <= filters.end_date)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        query = query.order_by(Exam.start_time.desc())
        
        result = await self.db.execute(query)
        exams = result.scalars().all()
        
        return list(exams), total
    
    async def update_exam(self, exam_id: UUID, exam_data: ExamUpdate) -> Optional[Exam]:
        exam = await self.get_exam_by_id(exam_id)
        if not exam:
            return None
        
        update_data = exam_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(exam, field, value)
        
        exam.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(exam)
        return exam
    
    async def update_exam_status(self, exam_id: UUID, status: ExamStatus) -> Optional[Exam]:
        exam = await self.get_exam_by_id(exam_id)
        if not exam:
            return None
        
        exam.status = status
        exam.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(exam)
        return exam
    
    async def delete_exam(self, exam_id: UUID) -> bool:
        exam = await self.get_exam_by_id(exam_id)
        if not exam:
            return False
        
        await self.db.delete(exam)
        await self.db.commit()
        return True
