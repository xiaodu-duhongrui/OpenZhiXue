from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.class_model import Class, ClassStatus
from app.schemas.class_schema import ClassCreate, ClassUpdate


class ClassService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_classes(
        self,
        page: int = 1,
        page_size: int = 10,
        name: Optional[str] = None,
        grade: Optional[int] = None,
        year: Optional[int] = None,
        status: Optional[ClassStatus] = None,
    ):
        query = select(Class)
        count_query = select(func.count(Class.id))

        if name:
            query = query.where(Class.name.ilike(f"%{name}%"))
            count_query = count_query.where(Class.name.ilike(f"%{name}%"))
        if grade:
            query = query.where(Class.grade == grade)
            count_query = count_query.where(Class.grade == grade)
        if year:
            query = query.where(Class.year == year)
            count_query = count_query.where(Class.year == year)
        if status:
            query = query.where(Class.status == status)
            count_query = count_query.where(Class.status == status)

        total = await self.db.scalar(count_query)
        total = total or 0

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(Class.created_at.desc())

        result = await self.db.execute(query)
        classes = result.scalars().all()

        total_pages = (total + page_size - 1) // page_size

        return classes, total, page, page_size, total_pages

    async def get_class_by_id(self, class_id: int):
        query = select(Class).where(Class.id == class_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_class(self, class_data: ClassCreate):
        class_ = Class(**class_data.model_dump())
        self.db.add(class_)
        await self.db.commit()
        await self.db.refresh(class_)
        return class_

    async def update_class(self, class_id: int, class_data: ClassUpdate):
        class_ = await self.get_class_by_id(class_id)
        if not class_:
            return None

        update_data = class_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(class_, key, value)

        await self.db.commit()
        await self.db.refresh(class_)
        return class_

    async def delete_class(self, class_id: int):
        class_ = await self.get_class_by_id(class_id)
        if not class_:
            return False

        await self.db.delete(class_)
        await self.db.commit()
        return True

    async def get_class_students(self, class_id: int):
        from app.models.student import Student

        query = select(Student).where(Student.class_id == class_id)
        result = await self.db.execute(query)
        return result.scalars().all()
