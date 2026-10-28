import os
from pathlib import Path
from fastapi.testclient import TestClient
from app.core.config import Settings
from app.main import app

def test_vercel_environment_detection(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    settings = Settings(_env_file=None)
    
    assert settings.STORAGE_DIR != ""
    assert "heritageproof.db" in settings.DATABASE_URL
    assert settings.DATABASE_URL.startswith("sqlite:///")

def test_vercel_health_and_root_endpoints(client):
    # Test root endpoint
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "HeritageProof"
    assert data["version"] == "1.0.0"
    assert data["api_v1"] == "/api/v1"

    # Test health endpoint
    res_health = client.get("/api/v1/health")
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["status"] == "healthy"
    assert health_data["database_status"] == "healthy"

def test_cors_configuration(client):
    # Test that CORS allows vercel.app domains via regex
    res = client.options(
        "/api/v1/health",
        headers={
            "Origin": "https://heritageproof-frontend.vercel.app",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "https://heritageproof-frontend.vercel.app"
