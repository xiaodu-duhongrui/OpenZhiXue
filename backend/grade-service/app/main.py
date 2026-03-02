from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from app.config import settings
from app.database import init_db, close_db
from app.mongodb import init_mongodb, close_mongodb
from app.redis_client import init_redis, close_redis
from app.routers import (
    grades_router,
    students_router,
    exams_router,
    exam_management_router,
    subjects_router,
    analysis_router,
    reports_router,
)

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Grade Service...")
    
    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    try:
        await init_mongodb()
        logger.info("MongoDB initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
    
    try:
        await init_redis()
        logger.info("Redis initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")
    
    yield
    
    logger.info("Shutting down Grade Service...")
    
    await close_db()
    await close_mongodb()
    await close_redis()
    
    logger.info("Grade Service shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="成绩管理服务 - 提供成绩录入、查询、统计分析和报告生成功能",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(grades_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1")
app.include_router(exams_router, prefix="/api/v1")
app.include_router(exam_management_router, prefix="/api/v1")
app.include_router(subjects_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "An internal server error occurred",
            "detail": str(exc) if settings.DEBUG else None,
        },
    )


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/", tags=["root"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


def main():
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    main()
