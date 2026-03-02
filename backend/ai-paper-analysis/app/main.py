from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys
import os
import asyncio

from app.config import settings
from app.database import init_db, close_db
from app.utils.redis_client import init_redis, close_redis
from app.routers import upload_router, tasks_router, analysis_router, ocr_router
from app.services.ai_service import get_ai_service
from app.services.ocr_service import get_ocr_service

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up AI Paper Analysis Service...")

    # Create necessary directories
    for dir_path in [settings.UPLOAD_DIR, settings.PAPER_STORAGE_PATH, settings.ANALYSIS_RESULT_PATH]:
        os.makedirs(dir_path, exist_ok=True)
        logger.info(f"Created directory: {dir_path}")

    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    try:
        await init_redis()
        logger.info("Redis initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {e}")

    # Preload AI model (optional, can be lazy loaded on first use)
    if settings.MODEL_CACHE_ENABLED:
        try:
            logger.info("Preloading AI model...")
            ai_service = get_ai_service()
            # Run model loading in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, ai_service.load_model)
            if success:
                logger.info("AI model preloaded successfully")
            else:
                logger.warning("AI model preload failed, will use lazy loading")
        except Exception as e:
            logger.warning(f"AI model preload error: {e}, will use lazy loading")
    else:
        logger.info("Model cache disabled, using lazy loading")

    # Preload OCR model (optional, can be lazy loaded on first use)
    if settings.OCR_CACHE_ENABLED:
        try:
            logger.info("Preloading OCR model...")
            ocr_service = get_ocr_service()
            # Run model loading in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, ocr_service.load_model)
            if success:
                logger.info("OCR model preloaded successfully")
            else:
                logger.warning("OCR model preload failed, will use lazy loading")
        except Exception as e:
            logger.warning(f"OCR model preload error: {e}, will use lazy loading")
    else:
        logger.info("OCR model cache disabled, using lazy loading")

    logger.info("AI Paper Analysis Service started successfully")

    yield

    logger.info("Shutting down AI Paper Analysis Service...")

    # Unload AI model
    try:
        ai_service = get_ai_service()
        ai_service.unload_model()
        logger.info("AI model unloaded")
    except Exception as e:
        logger.error(f"Error unloading AI model: {e}")

    # Unload OCR model
    try:
        ocr_service = get_ocr_service()
        ocr_service.unload_model()
        logger.info("OCR model unloaded")
    except Exception as e:
        logger.error(f"Error unloading OCR model: {e}")

    await close_redis()
    logger.info("Redis connection closed")

    await close_db()
    logger.info("Database connection closed")

    logger.info("AI Paper Analysis Service shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI试卷分析服务 - 提供试卷OCR识别、智能分析、知识点提取等功能",
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

# 注册路由
app.include_router(upload_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(ocr_router, prefix="/api/v1")


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
    ai_service = get_ai_service()
    ocr_service = get_ocr_service()
    model_status = ai_service.get_model_status()
    ocr_status = ocr_service.get_model_status()
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "model": model_status,
        "ocr": ocr_status,
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
