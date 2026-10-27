from fastapi.testclient import TestClient

def test_user_registration_and_duplicate_handling(client: TestClient):
    payload = {
        "username": "archivist_riya",
        "email": "riya@heritageproof.org",
        "password": "StrongPassword123!",
        "role": "researcher",
        "organization": "Gujarat Heritage Board"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "archivist_riya"
    assert data["email"] == "riya@heritageproof.org"
    assert data["role"] == "researcher"
    assert data["organization"] == "Gujarat Heritage Board"
    assert "id" in data
    assert "hashed_password" not in data

    # Try registering same username again
    dup_response = client.post("/api/v1/auth/register", json=payload)
    assert dup_response.status_code == 400
    assert "Username already registered" in dup_response.json()["detail"]

def test_user_login_success_and_failure(client: TestClient):
    # Register user
    user_payload = {
        "username": "lead_verifier_arjun",
        "email": "arjun@heritageproof.org",
        "password": "CorrectPassword2026!",
        "role": "verifier",
        "organization": "Archaeological Survey"
    }
    client.post("/api/v1/auth/register", json=user_payload)

    # Valid Login
    login_res = client.post("/api/v1/auth/login", json={
        "username": "lead_verifier_arjun",
        "password": "CorrectPassword2026!"
    })
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user"]["username"] == "lead_verifier_arjun"

    # Invalid Password Login
    bad_login = client.post("/api/v1/auth/login", json={
        "username": "lead_verifier_arjun",
        "password": "WrongPassword!"
    })
    assert bad_login.status_code == 401

def test_auth_me_endpoint_and_protection(client: TestClient):
    # Unauthenticated request
    unauth = client.get("/api/v1/auth/me")
    assert unauth.status_code == 401

    # Register & Login
    client.post("/api/v1/auth/register", json={
        "username": "viewer_dev",
        "email": "dev@heritageproof.org",
        "password": "DevPassword123!",
        "role": "viewer"
    })
    login_res = client.post("/api/v1/auth/login", json={
        "username": "viewer_dev",
        "password": "DevPassword123!"
    })
    token = login_res.json()["access_token"]

    # Authorized request with Bearer header
    headers = {"Authorization": f"Bearer {token}"}
    me_res = client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["username"] == "viewer_dev"
    assert me_res.json()["role"] == "viewer"
