from datetime import datetime, date
from typing import Any, Optional
from uuid import UUID


def datetime_to_iso(dt: datetime) -> str:
    return dt.isoformat() if dt else None


def iso_to_datetime(iso_str: str) -> Optional[datetime]:
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    except ValueError:
        return None


def calculate_age(birth_date: date) -> int:
    today = date.today()
    age = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def format_score(score: float, decimal_places: int = 2) -> str:
    return f"{score:.{decimal_places}f}"


def calculate_grade_level(score: float, total_score: float = 100.0) -> str:
    percentage = (score / total_score) * 100
    
    if percentage >= 90:
        return "优秀"
    elif percentage >= 80:
        return "良好"
    elif percentage >= 70:
        return "中等"
    elif percentage >= 60:
        return "及格"
    else:
        return "不及格"


def uuid_to_str(uuid_value: UUID) -> str:
    return str(uuid_value) if uuid_value else None


def str_to_uuid(uuid_str: str) -> Optional[UUID]:
    if not uuid_str:
        return None
    try:
        return UUID(uuid_str)
    except ValueError:
        return None


def paginate_list(items: list, page: int, page_size: int) -> dict:
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        "items": items[start_idx:end_idx],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
