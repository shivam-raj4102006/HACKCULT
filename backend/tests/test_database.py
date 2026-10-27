from sqlalchemy.orm import Session
from app.models.user import User
from app.models.document import Document
from app.models.site import HeritageSite
from app.models.evidence import EvidenceRecord
from app.models.audit import AuditLog
from app.core.security import get_password_hash, verify_password

def test_user_creation_and_hashing(db_session: Session):
    pwd = "SecureVerifierPassword123!"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed)
    assert not verify_password("WrongPassword", hashed)

    user = User(
        username="lead_verifier",
        email="verifier@heritageproof.org",
        hashed_password=hashed,
        role="verifier"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.role == "verifier"
    assert user.is_active is True

def test_document_and_evidence_relationship(db_session: Session):
    doc = Document(
        original_filename="rani_ki_vav_survey.pdf",
        storage_path="/data/storage/uploads/test.pdf",
        mime_type="application/pdf",
        file_size=10240,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        status="COMPLETED",
        total_pages_or_slides=12
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)

    site = HeritageSite(
        name="Rani Ki Vav",
        alternate_names="Queen's Stepwell",
        site_type="stepwell",
        historical_period="Solanki Dynasty (11th Century CE)",
        latitude=23.8589,
        longitude=72.1017,
        city="Patan",
        state="Gujarat"
    )
    db_session.add(site)
    db_session.commit()
    db_session.refresh(site)

    evidence = EvidenceRecord(
        document_id=doc.id,
        site_id=site.id,
        page_or_slide_number=3,
        chunk_index=1,
        raw_extracted_text="The stepwell was constructed during the reign of the Chaulukya dynasty.",
        claim_statement="Built in 11th century CE by Queen Udayamati.",
        extraction_confidence=0.98,
        verification_status="PENDING_REVIEW"
    )
    db_session.add(evidence)
    db_session.commit()
    db_session.refresh(evidence)

    assert evidence.id is not None
    assert evidence.document_id == doc.id
    assert evidence.site_id == site.id
    assert evidence.page_or_slide_number == 3
    assert evidence.verification_status == "PENDING_REVIEW"
    assert len(doc.evidence_records) == 1
