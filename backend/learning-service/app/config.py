import os
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Learning Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    DATABASE_URL: str = "postgresql+asyncpg://openzhixue:openzhixue123@localhost:5432/openzhixue_learning"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    
    JWT_SECRET: str = "your-super-secret-jwt-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRES_IN: int = 604800
    
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "openzhixue"
    MINIO_SECRET_KEY: str = "openzhixue123"
    MINIO_SECURE: bool = False
    MINIO_BUCKET_VIDEOS: str = "learning-videos"
    MINIO_BUCKET_RESOURCES: str = "learning-resources"
    
    VIDEO_SIGNATURE_SECRET: str = "video-signature-secret-key"
    VIDEO_SIGNATURE_EXPIRE: int = 3600
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
