from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Grade Service"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    PORT: int = 8083
    
    DATABASE_URL: str = "postgresql+asyncpg://openzhixue:openzhixue123@localhost:5432/openzhixue"
    DATABASE_SYNC_URL: str = "postgresql://openzhixue:openzhixue123@localhost:5432/openzhixue"
    
    REDIS_URL: str = "redis://localhost:6379"
    
    MONGODB_URL: str = "mongodb://admin:admin123@localhost:27017/openzhixue?authSource=admin"
    MONGODB_DB_NAME: str = "openzhixue"
    
    JWT_SECRET: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24
    
    CORS_ORIGINS: list[str] = ["*"]
    
    REPORT_STORAGE_PATH: str = "./reports"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
