from app.routers.grades import router as grades_router
from app.routers.students import router as students_router
from app.routers.exams import router as exams_router
from app.routers.exam_management import router as exam_management_router
from app.routers.subjects import router as subjects_router
from app.routers.analysis import router as analysis_router
from app.routers.reports import router as reports_router

__all__ = [
    "grades_router",
    "students_router",
    "exams_router",
    "exam_management_router",
    "subjects_router",
    "analysis_router",
    "reports_router",
]
