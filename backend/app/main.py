import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.ocr import router as ocr_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.reports import router as reports_router
from app.api.v1.search import router as search_router
from app.api.v1.sites import router as sites_router
from app.api.v1.journeys import router as journeys_router
from app.api.v1.photogrammetry import router as photogrammetry_router
from app.api.v1.demo import router as demo_router
from app.services.seed import seed_gujarat_heritage_data

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure storage directories exist safely
    try:
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.REPORT_DIR, exist_ok=True)
    except (OSError, PermissionError) as e:
        logger.warning(f"Could not create storage in {settings.UPLOAD_DIR}: {e}. Falling back to temp directory.")
        import tempfile
        tmp_base = Path(tempfile.gettempdir()) / "storage"
        settings.STORAGE_DIR = str(tmp_base)
        settings.UPLOAD_DIR = str(tmp_base / "uploads")
        settings.REPORT_DIR = str(tmp_base / "reports")
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(settings.REPORT_DIR, exist_ok=True)
    
    # Initialize database tables & seed canonical demo monuments
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            seed_gujarat_heritage_data(db)
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Database initialization / seed warning: {e}")

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="HeritageProof: Archival Evidence Verification & Spatial Exploration Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^https:\/\/.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "Content-Length", "Content-Type"],
)

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(ocr_router, prefix=settings.API_V1_STR)
app.include_router(evidence_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(sites_router, prefix=settings.API_V1_STR)
app.include_router(journeys_router, prefix=settings.API_V1_STR)
app.include_router(photogrammetry_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix=settings.API_V1_STR)
app.include_router(health_router, prefix="", tags=["Root Health"])

@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }
