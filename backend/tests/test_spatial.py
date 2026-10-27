import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.services.seed import seed_gujarat_heritage_data

def test_sites_listing_and_filtering(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)

    # 1. List all sites
    res = client.get("/api/v1/sites")
    assert res.status_code == 200
    sites = res.json()
    assert len(sites) >= 3

    # 2. Filter by site_type=stepwell
    res_stepwells = client.get("/api/v1/sites?site_type=stepwell")
    assert res_stepwells.status_code == 200
    stepwells = res_stepwells.json()
    assert len(stepwells) >= 2
    for s in stepwells:
        assert s["site_type"] == "stepwell"

def test_spatial_bbox_query(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)

    # Query bounding box covering Northern Gujarat (approx 23.0 to 24.0 lat, 72.0 to 73.0 lng)
    res = client.get("/api/v1/sites/spatial/bbox?min_lat=23.0&max_lat=24.0&min_lng=72.0&max_lng=73.0")
    assert res.status_code == 200
    sites = res.json()
    assert len(sites) >= 3
    site_names = [s["name"] for s in sites]
    assert "Rani Ki Vav" in site_names
    assert "Sun Temple Modhera" in site_names

    # Query disjoint bounding box (e.g. South India)
    res_empty = client.get("/api/v1/sites/spatial/bbox?min_lat=10.0&max_lat=11.0&min_lng=76.0&max_lng=77.0")
    assert res_empty.status_code == 200
    assert len(res_empty.json()) == 0

def test_journeys_and_stops_api(client: TestClient, db_session: Session):
    seed_gujarat_heritage_data(db_session)

    # List journeys
    res = client.get("/api/v1/journeys")
    assert res.status_code == 200
    journeys = res.json()
    assert len(journeys) >= 1
    j_id = journeys[0]["id"]
    assert journeys[0]["stop_count"] == 3

    # Get journey detail with ordered stops
    res_detail = client.get(f"/api/v1/journeys/{j_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert len(detail["stops"]) == 3
    assert detail["stops"][0]["stop_order"] == 1
    assert "Adalaj" in detail["stops"][0]["title"]
    assert detail["stops"][0]["folklore_narrative"] is not None
    assert detail["stops"][0]["architectural_observation"] is not None

def test_create_custom_journey(client: TestClient, db_session: Session):
    payload = {
        "title": "Ahmedabad Heritage Walk",
        "description": "Historic walled city route",
        "region": "Central Gujarat",
        "era": "15th Century",
        "estimated_duration": "4 Hours",
        "stops": [
            {
                "stop_order": 1,
                "title": "Bhadra Fort",
                "folklore_narrative": "Founded by Ahmad Shah I in 1411 CE.",
                "architectural_observation": "Carved arches and royal palace gates.",
                "latitude": 23.0258,
                "longitude": 72.5797
            },
            {
                "stop_order": 2,
                "title": "Sidi Saiyyed Mosque",
                "folklore_narrative": "Famed for its intricate stone lattice Tree of Life.",
                "architectural_observation": "Ten semi-circular jali windows carved from yellow sandstone.",
                "latitude": 23.0270,
                "longitude": 72.5815
            }
        ]
    }
    res = client.post("/api/v1/journeys", json=payload)
    assert res.status_code == 201
    created = res.json()
    assert created["title"] == "Ahmedabad Heritage Walk"
    assert len(created["stops"]) == 2
