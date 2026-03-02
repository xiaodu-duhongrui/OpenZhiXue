from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "AI Paper Analysis Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    PORT: int = 8084

    DATABASE_URL: str = "postgresql+asyncpg://openzhixue:openzhixue123@localhost:5432/openzhixue"
    DATABASE_SYNC_URL: str = "postgresql://openzhixue:openzhixue123@localhost:5432/openzhixue"

    REDIS_URL: str = "redis://localhost:6379"

    MONGODB_URL: str = "mongodb://admin:admin123@localhost:27017/openzhixue?authSource=admin"
    MONGODB_DB_NAME: str = "openzhixue"

    JWT_SECRET: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24

    CORS_ORIGINS: list[str] = ["*"]

    # AI Model Paths
    QWEN_MODEL_PATH: str = "e:/openzhixue/model/qwen3-0.5b"
    DEEPSEEK_OCR_MODEL_PATH: str = "e:/openzhixue/model/deepseek-ocr2"

    # Model Device Settings
    MODEL_DEVICE: str = "auto"  # auto/cuda/cpu
    MAX_NEW_TOKENS: int = 2048
    TEMPERATURE: float = 0.7
    TOP_P: float = 0.9
    MODEL_CACHE_ENABLED: bool = True

    # OCR Model Settings
    OCR_DEVICE: str = "auto"  # auto/cuda/cpu
    OCR_MAX_NEW_TOKENS: int = 8192
    OCR_TEMPERATURE: float = 0.0
    OCR_CACHE_ENABLED: bool = True
    OCR_BASE_SIZE: int = 1024
    OCR_IMAGE_SIZE: int = 640
    OCR_CROP_MODE: bool = True

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    PAPER_STORAGE_PATH: str = "./papers"
    ANALYSIS_RESULT_PATH: str = "./analysis_results"

    # Model Settings
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FILE_TYPES: list[str] = ["pdf", "docx", "doc", "txt", "png", "jpg", "jpeg"]

    # OCR Settings
    OCR_CONFIDENCE_THRESHOLD: float = 0.8
    OCR_LANGUAGE: str = "ch"  # Chinese

    # Analysis Settings
    MAX_CONCURRENT_TASKS: int = 5
    TASK_TIMEOUT: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
