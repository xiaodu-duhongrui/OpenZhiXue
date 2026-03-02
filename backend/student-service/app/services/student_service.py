from typing import Optional
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.student import Student, StudentStatus
from app.schemas.student import StudentCreate, StudentUpdate


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_students(
        self,
        page: int = 1,
        page_size: int = 10,
        name: Optional[str] = None,
        student_no: Optional[str] = None,
        class_id: Optional[int] = None,
        status: Optional[StudentStatus] = None,
    ):
        query = select(Student)
        count_query = select(func.count(Student.id))

        if name:
            query = query.where(Student.name.ilike(f"%{name}%"))
            count_query = count_query.where(Student.name.ilike(f"%{name}%"))
        if student_no:
            query = query.where(Student.student_no.ilike(f"%{student_no}%"))
            count_query = count_query.where(Student.student_no.ilike(f"%{student_no}%"))
        if class_id:
            query = query.where(Student.class_id == class_id)
            count_query = count_query.where(Student.class_id == class_id)
        if status:
            query = query.where(Student.status == status)
            count_query = count_query.where(Student.status == status)

        total = await self.db.scalar(count_query)
        total = total or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Student.created_at.desc())

        result = await self.db.execute(query)
        students = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size

        return students, total, page, page_size, total_pages

    async def get_student_by_id(self, student_id: int):
        query = select(Student).where(Student.id == student_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_student_by_student_no(self, student_no: str):
        query = select(Student).where(Student.student_no == student_no)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_student(self, student_data: StudentCreate):
        existing = await self.get_student_by_student_no(student_data.student_no)
        if existing:
            raise ValueError(f"Student with student_no '{student_data.student_no}' already exists")

        student = Student(**student_data.model_dump())
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def update_student(self, student_id: int, student_data: StudentUpdate):
        student = await self.get_student_by_id(student_id)
        if not student:
            return None

        update_data = student_data.model_dump(exclude_unset=True)
        
        if "student_no" in update_data and update_data["student_no"] != student.student_no:
            existing = await self.get_student_by_student_no(update_data["student_no"])
            if existing:
                raise ValueError(f"Student with student_no '{update_data['student_no']}' already exists")

        for key, value in update_data.items():
            setattr(student, key, value)

        await self.db.commit()
        await self.db.refresh(student)
        return student

    async def delete_student(self, student_id: int):
        student = await self.get_student_by_id(student_id)
        if not student:
            return False

        await self.db.delete(student)
        await self.db.commit()
        return True
