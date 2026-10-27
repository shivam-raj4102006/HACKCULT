import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.seed import seed_gujarat_heritage_data

def test_grounded_qa_with_valid_citations(client: TestClient, db_session: Session):
    # Ensure seed data is populated
    seed_gujarat_heritage_data(db_session)

    # Ask an evidence-grounded question regarding Rani Ki Vav
    response = client.post(
        "/api/v1/search/qa",
        json={"query": "Who commissioned Rani Ki Vav in Patan?", "only_verified": False}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "GROUNDED_ANSWER"
    assert "Udayamati" in data["answer"] or "Bhima I" in data["answer"] or "Patan" in data["answer"]
    assert len(data["citations"]) > 0
    citation = data["citations"][0]
    assert "document_name" in citation
    assert "page_or_slide_number" in citation
    assert len(citation["snippet"]) > 0
    assert citation["relevance_score"] >= 0.35


def test_qa_insufficient_evidence_when_sources_do_not_support(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)

    # Ask something completely unsupported by the Gujarat heritage archive
    response = client.post(
        "/api/v1/search/qa",
        json={"query": "Who constructed the Eiffel Tower iron trusses in 1889?", "only_verified": False}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "INSUFFICIENT_EVIDENCE"
    assert "Insufficient evidence" in data["answer"]
    assert len(data["citations"]) == 0


def test_search_endpoint_and_verified_filter(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)

    # Query without filter
    res_all = client.post(
        "/api/v1/search/query",
        json={"query": "stepwell Maru-Gurjara subterranean water", "only_verified": False}
    )
    assert res_all.status_code == 200
    hits_all = res_all.json()["hits"]
    assert len(hits_all) > 0

    # Query with only_verified=True
    res_verified = client.post(
        "/api/v1/search/query",
        json={"query": "stepwell Maru-Gurjara subterranean water", "only_verified": True}
    )
    assert res_verified.status_code == 200
    hits_verified = res_verified.json()["hits"]
    for hit in hits_verified:
        assert hit["verification_status"] == "verified"
