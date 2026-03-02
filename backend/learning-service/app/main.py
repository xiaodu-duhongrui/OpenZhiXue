from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine, Base
from app.routers import courses, lessons, students, reports
from app.utils.logger import logger
from app.utils.redis_client import RedisClient
from app.utils.storage import StorageClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting up Learning Service...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await StorageClient.ensure_buckets()
    
    logger.info("Learning Service started successfully")
    
    yield
    
    logger.info("Shutting down Learning Service...")
    await RedisClient.close()
    logger.info("Learning Service shut down complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="在线学习服务 - 提供课程管理、视频点播、学习进度追踪等功能",
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

app.include_router(courses.router, prefix=settings.API_PREFIX)
app.include_router(lessons.router, prefix=settings.API_PREFIX)
app.include_router(students.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)


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
        "message": "Welcome to Learning Service",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
