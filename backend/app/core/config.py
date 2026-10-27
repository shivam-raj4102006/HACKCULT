from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "HeritageProof"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Security
    SECRET_KEY: str = "heritageproof-super-secret-jwt-key-2026-production-ready"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/heritageproof.db"
    
    # Storage
    STORAGE_DIR: str = str(BASE_DIR / "storage")
    UPLOAD_DIR: str = str(BASE_DIR / "storage" / "uploads")
    REPORT_DIR: str = str(BASE_DIR / "storage" / "reports")
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50MB
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
