import os
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
from app.services.seed import seed_gujarat_heritage_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure storage directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.REPORT_DIR, exist_ok=True)
    
    # Initialize database tables
    Base.metadata.create_all(bind=engine)
    
    # Seed canonical demo monuments (Rani Ki Vav, Modhera, Adalaj)
    db = SessionLocal()
    try:
        seed_gujarat_heritage_data(db)
    finally:
        db.close()

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
