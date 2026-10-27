from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.evidence import EvidenceRecord
from app.models.site import HeritageSite
from app.models.checklist import ChecklistItem
from app.models.audit import AuditLog
from app.models.user import User
from app.api.deps import get_current_user, require_roles
from app.services.gap_analysis import compute_gap_analysis

router = APIRouter(prefix="/evidence", tags=["Pathway 4: Evidence Graph & Verification"])

class EvidenceReviewRequest(BaseModel):
    evidence_id: str
    status: str = Field(..., pattern="^(verified|reviewed|rejected|unverified)$")
    verification_notes: Optional[str] = "Human verification sign-off"
    site_id: Optional[str] = None

class EvidenceReviewResponse(BaseModel):
    id: str
    document_id: str
    site_id: Optional[str]
    page_or_slide_number: int
    claim_statement: Optional[str]
    raw_extracted_text: str
    verification_status: str
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    verification_notes: Optional[str]

    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[EvidenceReviewResponse])
def list_evidence(
    verification_status: Optional[str] = Query(None),
    site_id: Optional[str] = Query(None),
    document_id: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(EvidenceRecord)
    if verification_status:
        query = query.filter(EvidenceRecord.verification_status == verification_status)
    if site_id:
        query = query.filter(EvidenceRecord.site_id == site_id)
    if document_id:
        query = query.filter(EvidenceRecord.document_id == document_id)

    return query.order_by(EvidenceRecord.created_at.desc()).limit(limit).all()

@router.post("/review", response_model=EvidenceReviewResponse)
def review_claim(
    review_req: EvidenceReviewRequest,
    current_user: User = Depends(require_roles(["researcher", "admin", "verifier"])),
    db: Session = Depends(get_db)
):
    """
    Strict Human-Only Verification Rule:
    Only authenticated users with 'researcher', 'verifier', or 'admin' roles can verify/reject claims.
    AI can never mark a claim verified.
    """
    evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == review_req.evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence record not found")

    old_status = evidence.verification_status
    evidence.verification_status = review_req.status
    evidence.verified_by = current_user.id
    evidence.verified_at = datetime.now(timezone.utc)
    evidence.verification_notes = review_req.verification_notes

    if review_req.site_id:
        evidence.site_id = review_req.site_id

    # Create immutable audit log
    audit = AuditLog(
        user_id=current_user.id,
        action=f"CLAIM_{review_req.status.upper()}",
        entity_name="EvidenceRecord",
        entity_id=evidence.id,
        details={
            "old_status": old_status,
            "new_status": review_req.status,
            "verifier_username": current_user.username,
            "verifier_role": current_user.role,
            "notes": review_req.verification_notes
        }
    )
    db.add(audit)
    db.commit()
    db.refresh(evidence)
    return evidence

@router.get("/gap-analysis/{site_id}")
def get_site_gap_analysis(site_id: str, db: Session = Depends(get_db)):
    data = compute_gap_analysis(site_id, db)
    if not data:
        raise HTTPException(status_code=404, detail="Heritage site not found")
    return data

@router.post("/checklist/{item_id}/fulfill")
def fulfill_checklist_item(
    item_id: str,
    evidence_id: Optional[str] = None,
    current_user: User = Depends(require_roles(["researcher", "admin", "verifier"])),
    db: Session = Depends(get_db)
):
    item = db.query(ChecklistItem).filter(ChecklistItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")

    item.is_fulfilled = True
    item.evidence_id = evidence_id
    db.commit()

    # Re-compute score
    compute_gap_analysis(item.site_id, db)
    return {"status": "success", "message": f"Category '{item.category}' marked fulfilled."}
