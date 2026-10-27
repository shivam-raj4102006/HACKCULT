from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        database_status=db_status,
        timestamp=datetime.now(timezone.utc)
    )
