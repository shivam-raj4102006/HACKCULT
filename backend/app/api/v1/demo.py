from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.seed import seed_gujarat_heritage_data, reset_demo_data
from app.models.site import HeritageSite
from app.models.document import Document
from app.models.evidence import EvidenceRecord
from app.models.journey import Journey

router = APIRouter(prefix="/demo", tags=["Demo Mode & Automated Synthetic Data"])

@router.get("/status")
def get_demo_status(db: Session = Depends(get_db)):
    """Returns the current synthetic demo state and summary metrics."""
    sites_count = db.query(HeritageSite).count()
    docs_count = db.query(Document).count()
    ev_total = db.query(EvidenceRecord).count()
    ev_verified = db.query(EvidenceRecord).filter(EvidenceRecord.verification_status == "verified").count()
    ev_unverified = db.query(EvidenceRecord).filter(EvidenceRecord.verification_status == "unverified").count()
    ev_rejected = db.query(EvidenceRecord).filter(EvidenceRecord.verification_status == "rejected").count()
    journeys_count = db.query(Journey).count()

    return {
        "status": "ready",
        "demo_mode": True,
        "label": "Demo Mode — Synthetic Sample Data",
        "counts": {
            "sites": sites_count,
            "documents": docs_count,
            "evidence_total": ev_total,
            "evidence_verified": ev_verified,
            "evidence_pending": ev_unverified,
            "evidence_rejected": ev_rejected,
            "journeys": journeys_count
        },
        "description": "Fictional sample records inspired by Gujarat heritage documentation for demonstration purposes only."
    }

@router.post("/seed")
def trigger_seed_demo_data(db: Session = Depends(get_db)):
    """Idempotently ensures all canonical synthetic demo data is loaded."""
    try:
        seed_gujarat_heritage_data(db)
        return {
            "success": True,
            "message": "Synthetic demo data verified and loaded successfully.",
            "demo_mode": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to seed demo data: {str(e)}")

@router.post("/reset")
def trigger_reset_demo_data(db: Session = Depends(get_db)):
    """Resets demo data to initial clean state without altering user-created non-demo records."""
    try:
        reset_demo_data(db)
        return {
            "success": True,
            "message": "Demo data safely reset to canonical initial state.",
            "demo_mode": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset demo data: {str(e)}")
