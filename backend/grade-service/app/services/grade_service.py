from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime

from app.models.grade import Grade
from app.models.exam import Exam
from app.models.subject import Subject
from app.models.grade_analysis import GradeAnalysis
from app.schemas.grade import GradeCreate, GradeUpdate, GradeFilter, GradeBatchCreate


class GradeService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_grade(self, grade_data: GradeCreate) -> Grade:
        grade = Grade(
            student_id=grade_data.student_id,
            exam_id=grade_data.exam_id,
            subject_id=grade_data.subject_id,
            score=grade_data.score,
            class_id=grade_data.class_id,
        )
        self.db.add(grade)
        await self.db.commit()
        await self.db.refresh(grade)
        return grade
    
    async def batch_create_grades(self, grade_data: GradeBatchCreate) -> List[Grade]:
        grades = []
        for item in grade_data.grades:
            grade = Grade(
                student_id=item.student_id,
                exam_id=item.exam_id,
                subject_id=item.subject_id,
                score=item.score,
                class_id=item.class_id,
            )
            grades.append(grade)
        
        self.db.add_all(grades)
        await self.db.commit()
        
        for grade in grades:
            await self.db.refresh(grade)
        
        return grades
    
    async def get_grade_by_id(self, grade_id: UUID) -> Optional[Grade]:
        result = await self.db.execute(
            select(Grade)
            .options(selectinload(Grade.exam), selectinload(Grade.subject))
            .where(Grade.id == grade_id)
        )
        return result.scalar_one_or_none()
    
    async def get_grades(self, filters: GradeFilter) -> Tuple[List[Grade], int]:
        query = select(Grade).options(
            selectinload(Grade.exam), 
            selectinload(Grade.subject)
        )
        
        conditions = []
        if filters.student_id:
            conditions.append(Grade.student_id == filters.student_id)
        if filters.exam_id:
            conditions.append(Grade.exam_id == filters.exam_id)
        if filters.subject_id:
            conditions.append(Grade.subject_id == filters.subject_id)
        if filters.class_id:
            conditions.append(Grade.class_id == filters.class_id)
        if filters.min_score is not None:
            conditions.append(Grade.score >= filters.min_score)
        if filters.max_score is not None:
            conditions.append(Grade.score <= filters.max_score)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)
        query = query.order_by(Grade.created_at.desc())
        
        result = await self.db.execute(query)
        grades = result.scalars().all()
        
        return list(grades), total
    
    async def get_grades_by_student(
        self, 
        student_id: UUID,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Grade], int]:
        query = select(Grade).options(
            selectinload(Grade.exam),
            selectinload(Grade.subject)
        ).where(Grade.student_id == student_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(Grade.created_at.desc())
        
        result = await self.db.execute(query)
        grades = result.scalars().all()
        
        return list(grades), total
    
    async def get_grades_by_exam(
        self,
        exam_id: UUID,
        class_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Grade], int]:
        query = select(Grade).options(
            selectinload(Grade.exam),
            selectinload(Grade.subject)
        ).where(Grade.exam_id == exam_id)
        
        if class_id:
            query = query.where(Grade.class_id == class_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(Grade.score.desc())
        
        result = await self.db.execute(query)
        grades = result.scalars().all()
        
        return list(grades), total
    
    async def update_grade(self, grade_id: UUID, grade_data: GradeUpdate) -> Optional[Grade]:
        grade = await self.get_grade_by_id(grade_id)
        if not grade:
            return None
        
        update_data = grade_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(grade, field, value)
        
        grade.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(grade)
        return grade
    
    async def delete_grade(self, grade_id: UUID) -> bool:
        grade = await self.get_grade_by_id(grade_id)
        if not grade:
            return False
        
        await self.db.delete(grade)
        await self.db.commit()
        return True
    
    async def calculate_ranks(self, exam_id: UUID, subject_id: UUID) -> None:
        grades = await self.db.execute(
            select(Grade)
            .where(and_(Grade.exam_id == exam_id, Grade.subject_id == subject_id))
            .order_by(Grade.score.desc())
        )
        grades_list = grades.scalars().all()
        
        for rank, grade in enumerate(grades_list, start=1):
            grade.rank = rank
        
        class_grades = {}
        for grade in grades_list:
            if grade.class_id:
                if grade.class_id not in class_grades:
                    class_grades[grade.class_id] = []
                class_grades[grade.class_id].append(grade)
        
        for class_id, class_grade_list in class_grades.items():
            class_grade_list.sort(key=lambda x: x.score, reverse=True)
            for class_rank, grade in enumerate(class_grade_list, start=1):
                grade.class_rank = class_rank
        
        await self.db.commit()
