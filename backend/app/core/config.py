import os
import tempfile
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Detect Vercel serverless environment
IS_VERCEL = bool(
    os.environ.get("VERCEL")
    or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    or os.environ.get("VERCEL_ENV")
)

# On serverless (Vercel / AWS Lambda), the deployment root is read-only.
# All temporary storage and the default SQLite database must reside in /tmp.
if IS_VERCEL:
    TMP_DIR = Path(tempfile.gettempdir())
    DEFAULT_STORAGE_DIR = str(TMP_DIR / "storage")
    DEFAULT_UPLOAD_DIR = str(TMP_DIR / "storage" / "uploads")
    DEFAULT_REPORT_DIR = str(TMP_DIR / "storage" / "reports")
    DEFAULT_DATABASE_URL = f"sqlite:///{ (TMP_DIR / 'heritageproof.db').as_posix() }"
else:
    DEFAULT_STORAGE_DIR = str(BASE_DIR / "storage")
    DEFAULT_UPLOAD_DIR = str(BASE_DIR / "storage" / "uploads")
    DEFAULT_REPORT_DIR = str(BASE_DIR / "storage" / "reports")
    DEFAULT_DATABASE_URL = f"sqlite:///{ (BASE_DIR / 'heritageproof.db').as_posix() }"

class Settings(BaseSettings):
    PROJECT_NAME: str = "HeritageProof"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.environ.get("VERCEL_ENV", "development")
    
    # Security
    SECRET_KEY: str = "heritageproof-super-secret-jwt-key-2026-production-ready"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = DEFAULT_DATABASE_URL
    
    # Storage
    STORAGE_DIR: str = DEFAULT_STORAGE_DIR
    UPLOAD_DIR: str = DEFAULT_UPLOAD_DIR
    REPORT_DIR: str = DEFAULT_REPORT_DIR
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50MB
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        if not v:
            return DEFAULT_DATABASE_URL
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        if IS_VERCEL and v.startswith("sqlite"):
            # On serverless, relative paths or /var/task paths are read-only
            if ":memory:" not in v:
                clean_path = v.replace("sqlite:///", "")
                if not os.path.isabs(clean_path) or clean_path.startswith("/var/task") or clean_path.startswith("."):
                    return DEFAULT_DATABASE_URL
        return v

    @field_validator("STORAGE_DIR", mode="before")
    @classmethod
    def assemble_storage_dir(cls, v: str) -> str:
        if IS_VERCEL:
            if not v or not os.path.isabs(v) or v.startswith("/var/task") or v.startswith("."):
                return DEFAULT_STORAGE_DIR
        return v

    @field_validator("UPLOAD_DIR", mode="before")
    @classmethod
    def assemble_upload_dir(cls, v: str) -> str:
        if IS_VERCEL:
            if not v or not os.path.isabs(v) or v.startswith("/var/task") or v.startswith("."):
                return DEFAULT_UPLOAD_DIR
        return v

    @field_validator("REPORT_DIR", mode="before")
    @classmethod
    def assemble_report_dir(cls, v: str) -> str:
        if IS_VERCEL:
            if not v or not os.path.isabs(v) or v.startswith("/var/task") or v.startswith("."):
                return DEFAULT_REPORT_DIR
        return v

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env") if (BASE_DIR / ".env").exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
