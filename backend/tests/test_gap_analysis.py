import os
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.site import HeritageSite
from app.models.evidence import EvidenceRecord
from app.models.user import User
from app.core.security import create_access_token
from app.services.seed import seed_gujarat_heritage_data
from app.services.gap_analysis import compute_gap_analysis, initialize_site_checklist, SAFETY_DISCLAIMER
from app.services.report_generator import generate_pdf_dossier

def test_human_only_verification_rbac_rules(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)

    site = db_session.query(HeritageSite).filter(HeritageSite.name == "Rani Ki Vav").first()
    assert site is not None

    evidence = EvidenceRecord(
        document_id="doc-test-101",
        site_id=site.id,
        page_or_slide_number=2,
        chunk_index=0,
        raw_extracted_text="Inscriptional pillar frieze in level 3.",
        claim_statement="Pillar frieze contains Solanki insignia.",
        extraction_confidence=0.91,
        verification_status="unverified"  # AI starts claim as unverified
    )
    db_session.add(evidence)
    db_session.commit()
    db_session.refresh(evidence)

    # 1. Unauthenticated user cannot verify (401)
    unauth_res = client.post("/api/v1/evidence/review", json={
        "evidence_id": evidence.id,
        "status": "verified"
    })
    assert unauth_res.status_code == 401

    # 2. Viewer / Public role CANNOT verify (403 Forbidden)
    viewer_user = User(
        id="viewer-user-1",
        username="public_tourist_1",
        email="tourist@heritageproof.org",
        hashed_password="hashedpwd",
        role="viewer"
    )
    db_session.add(viewer_user)
    db_session.commit()

    viewer_token = create_access_token(subject="viewer-user-1", role="viewer")
    viewer_res = client.post(
        "/api/v1/evidence/review",
        json={"evidence_id": evidence.id, "status": "verified"},
        headers={"Authorization": f"Bearer {viewer_token}"}
    )
    assert viewer_res.status_code == 403
    assert "Operation not permitted" in viewer_res.json()["detail"]

    # 3. Verified Researcher CAN verify (200 OK)
    researcher = User(
        id="researcher-arjun-id",
        username="lead_researcher_arjun",
        email="arjun.research@heritageproof.org",
        hashed_password="hashedpassword123",
        role="researcher"
    )
    db_session.add(researcher)
    db_session.commit()

    researcher_token = create_access_token(subject="researcher-arjun-id", role="researcher")
    verify_res = client.post(
        "/api/v1/evidence/review",
        json={
            "evidence_id": evidence.id,
            "status": "verified",
            "verification_notes": "Corroborated by ASI epigraphic survey."
        },
        headers={"Authorization": f"Bearer {researcher_token}"}
    )
    assert verify_res.status_code == 200
    data = verify_res.json()
    assert data["verification_status"] == "verified"
    assert data["verified_by"] == "researcher-arjun-id"
    assert "ASI epigraphic survey" in data["verification_notes"]

def test_completeness_score_and_safety_disclaimer(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)

    # Check Adalaj (deliberately incomplete archive with only 2 categories fulfilled)
    adalaj = db_session.query(HeritageSite).filter(HeritageSite.name == "Adalaj Stepwell").first()
    assert adalaj is not None

    gap_data = compute_gap_analysis(adalaj.id, db_session)
    assert gap_data["completeness_score"] < 50.0  # Intentional gap demo
    assert "DISCLAIMER" in gap_data["disclaimer"]
    assert "NOT a structural safety" in gap_data["disclaimer"]
    assert len(gap_data["missing_tasks"]) >= 4

    # API endpoint check
    api_res = client.get(f"/api/v1/evidence/gap-analysis/{adalaj.id}")
    assert api_res.status_code == 200
    assert api_res.json()["completeness_score"] == gap_data["completeness_score"]

def test_pdf_dossier_generation_and_download(client: TestClient, db_session: Session):
    import io
    from pypdf import PdfReader

    seed_gujarat_heritage_data(db_session)

    site = db_session.query(HeritageSite).filter(HeritageSite.name == "Rani Ki Vav").first()
    assert site is not None

    # 1. Generate PDF directly via service
    pdf_path = generate_pdf_dossier(site.id, db_session)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000  # Non-trivial PDF

    with open(pdf_path, "rb") as f:
        header = f.read(4)
        assert header == b"%PDF"

    # 2. Test via API filename download endpoint
    filename = os.path.basename(pdf_path)
    res = client.get(f"/api/v1/reports/{filename}/download")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert "attachment" in res.headers["content-disposition"]

    # 3. Test direct site download endpoint using UUID
    direct_res = client.get(f"/api/v1/reports/site/{site.id}/download-direct")
    assert direct_res.status_code == 200
    assert direct_res.headers["content-type"] == "application/pdf"
    assert "attachment" in direct_res.headers["content-disposition"]
    assert "filename=" in direct_res.headers["content-disposition"]
    assert direct_res.content[:4] == b"%PDF"

    # Multi-page check and content validation
    reader = PdfReader(io.BytesIO(direct_res.content))
    assert len(reader.pages) >= 2
    full_text = " ".join([page.extract_text() for page in reader.pages])
    assert "HERITAGEPROOF ARCHIVAL DOSSIER" in full_text
    assert "DOCUMENTATION COMPLETENESS SCORE" in full_text
    assert "CRITICAL NOTICE" in full_text
    assert "Verification Audit Trail" in full_text

    # 4. Test direct site download endpoint using slug (e.g. 'rani-ki-vav-id')
    slug_res = client.get("/api/v1/reports/site/rani-ki-vav-id/download-direct")
    assert slug_res.status_code == 200
    assert slug_res.headers["content-type"] == "application/pdf"
    assert "attachment" in slug_res.headers["content-disposition"]
    assert slug_res.content[:4] == b"%PDF"

    # 5. Test 404 error handling for non-existent site
    invalid_res = client.get("/api/v1/reports/site/non-existent-site/download-direct")
    assert invalid_res.status_code == 404
    assert "not found" in invalid_res.json()["detail"].lower()

