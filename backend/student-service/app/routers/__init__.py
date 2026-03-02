from .student_router import router as student_router
from .class_router import router as class_router
from .student_profile_router import router as profile_router

__all__ = ["student_router", "class_router", "profile_router"]
