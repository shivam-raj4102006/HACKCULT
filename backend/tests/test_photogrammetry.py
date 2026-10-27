import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.seed import seed_gujarat_heritage_data
from app.models.site import HeritageSite

def test_photogrammetry_graceful_degradation_when_too_few_photos(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)
    site = db_session.query(HeritageSite).filter(HeritageSite.name == "Adalaj Stepwell").first()
    assert site is not None

    # Submit reconstruction with only 5 photos (below required 20 threshold)
    res = client.post(
        "/api/v1/photogrammetry/reconstruct",
        json={"site_id": site.id, "photo_count": 5, "engine": "COLMAP+OpenMVS"}
    )
    assert res.status_code == 202
    data = res.json()
    assert data["status"] == "DEGRADED_TO_2D"
    assert data["stage"] == "FALLBACK_2D_GALLERY"
    assert "below the required threshold of 20" in data["message"]
    assert data["model_3d_url"] is None

def test_photogrammetry_successful_reconstruction(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)
    site = db_session.query(HeritageSite).filter(HeritageSite.name == "Rani Ki Vav").first()
    assert site is not None

    # Submit reconstruction with 36 photos (above 20 threshold)
    res = client.post(
        "/api/v1/photogrammetry/reconstruct",
        json={"site_id": site.id, "photo_count": 36, "engine": "COLMAP+OpenMVS"}
    )
    assert res.status_code == 202
    data = res.json()
    assert data["status"] == "COMPLETED"
    assert data["stage"] == "GLB_EXPORTED"
    assert data["model_3d_url"] == "/models/stepwell_pavilion.glb"
    assert len(data["hotspots"]) == 3
    assert data["hotspots"][0]["verification_status"] == "verified"

    # Query status endpoint
    job_id = data["job_id"]
    status_res = client.get(f"/api/v1/photogrammetry/jobs/{job_id}")
    assert status_res.status_code == 200
    assert status_res.json()["job_id"] == job_id
