import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ShadowWatch"


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    payload = {
        "email": "analyst@shadowwatch.io",
        "password": "SecurePassword123!",
        "full_name": "Security Analyst"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert "refresh_token" in data["tokens"]
    assert data["tokens"]["token_type"] == "bearer"
    assert data["user"]["email"] == "analyst@shadowwatch.io"
    assert data["user"]["full_name"] == "Security Analyst"
    assert "password" not in data["user"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    payload = {
        "email": "duplicate@shadowwatch.io",
        "password": "SecurePassword123!",
        "full_name": "User One"
    }
    first_res = await client.post("/api/v1/auth/register", json=payload)
    assert first_res.status_code == 201

    second_res = await client.post("/api/v1/auth/register", json=payload)
    assert second_res.status_code == 400
    assert "already exists" in second_res.json()["detail"]


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    payload = {
        "email": "weak@shadowwatch.io",
        "password": "weak",
        "full_name": "Weak User"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # Register first
    reg_payload = {
        "email": "agent@shadowwatch.io",
        "password": "AgentPassword2026$",
        "full_name": "Field Agent"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201

    # Login
    login_payload = {
        "email": "agent@shadowwatch.io",
        "password": "AgentPassword2026$"
    }
    login_res = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200
    data = login_res.json()
    assert "tokens" in data
    assert "access_token" in data["tokens"]
    assert data["user"]["email"] == "agent@shadowwatch.io"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    reg_payload = {
        "email": "target@shadowwatch.io",
        "password": "CorrectPassword123#",
        "full_name": "Target User"
    }
    await client.post("/api/v1/auth/register", json=reg_payload)

    login_res = await client.post("/api/v1/auth/login", json={
        "email": "target@shadowwatch.io",
        "password": "WrongPassword999!"
    })
    assert login_res.status_code == 401
    assert "Incorrect email or password" in login_res.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user_profile(client: AsyncClient):
    # Register and get token
    reg_payload = {
        "email": "profile@shadowwatch.io",
        "password": "ProfilePassword123!",
        "full_name": "Profile Owner"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["tokens"]["access_token"]

    # Access /me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "profile@shadowwatch.io"
    assert me_res.json()["full_name"] == "Profile Owner"

    # Access without token
    unauth_res = await client.get("/api/v1/auth/me")
    assert unauth_res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    reg_payload = {
        "email": "refresh@shadowwatch.io",
        "password": "RefreshPassword123!",
        "full_name": "Refresh Tester"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    refresh_token = reg_res.json()["tokens"]["refresh_token"]

    refresh_res = await client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_res.status_code == 200
    new_tokens = refresh_res.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens


@pytest.mark.asyncio
async def test_dashboard_overview(client: AsyncClient):
    reg_payload = {
        "email": "dash@shadowwatch.io",
        "password": "DashPassword123!",
        "full_name": "Dash User"
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    token = reg_res.json()["tokens"]["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    res = await client.get("/api/v1/dashboard/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["metrics"]["privacy_score"] == 100
    assert data["metrics"]["total_breaches"] == 0
    assert isinstance(data["recent_scans"], list)


@pytest.mark.asyncio
async def test_logout_revokes_access_and_refresh_tokens(client: AsyncClient):
    reg = await client.post("/api/v1/auth/register", json={
        "email": "logout@shadowwatch.io", "password": "LogoutPassword123!", "full_name": "Logout Tester"
    })
    tokens = reg.json()["tokens"]
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    logout = await client.post("/api/v1/auth/logout", headers=headers, json={"refresh_token": tokens["refresh_token"]})
    assert logout.status_code == 200
    assert (await client.get("/api/v1/auth/me", headers=headers)).status_code == 401
    refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 401
