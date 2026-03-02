from app.routers.upload import router as upload_router
from app.routers.tasks import router as tasks_router
from app.routers.analysis import router as analysis_router
from app.routers.ocr import router as ocr_router

__all__ = [
    "upload_router",
    "tasks_router",
    "analysis_router",
    "ocr_router",
]
