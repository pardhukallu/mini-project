import pytest
from httpx import AsyncClient

from app.services.email_verification import EmailVerificationResult


@pytest.fixture(autouse=True)
def stub_email_verification(monkeypatch):
    """Keep scan tests deterministic: never probe a live mail server."""
    async def fake_verify(email):
        return EmailVerificationResult("valid", "Stubbed for tests.")

    monkeypatch.setattr("app.api.v1.scans.verify_email", fake_verify)


async def get_auth_token(client: AsyncClient, email: str = "security@shadowwatch.io") -> str:
    """Helper to create and authenticate a test user, returning the JWT access token."""
    payload = {
        "email": email,
        "password": "SecurePassword123!",
        "full_name": "Security Tester"
    }
    res = await client.post("/api/v1/auth/register", json=payload)
    return res.json()["tokens"]["access_token"]


@pytest.mark.asyncio
async def test_email_breach_live_xposedornot_result(client: AsyncClient, monkeypatch):
    token = await get_auth_token(client, "test.breach@shadowwatch.io")
    headers = {"Authorization": f"Bearer {token}"}

    async def fake_email_lookup(email):
        return ([{"name": "ExampleBreach", "title": "ExampleBreach", "domain": "", "breach_date": "", "added_date": None, "pwn_count": 0, "description": "Reported by XposedOrNot", "logo_path": None, "data_classes": [], "is_verified": True, "is_sensitive": False}], "xposedornot_api")
    monkeypatch.setattr("app.api.v1.scans.check_email_breaches", fake_email_lookup)

    res = await client.post(
        "/api/v1/scans/email-breach",
        headers=headers,
        json={"email": "victim@example.com"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_breached"] is True
    assert data["breach_count"] >= 1
    assert len(data["breaches"]) >= 1
    assert data["source"] == "xposedornot_api"
    assert data["score_impact"] > 0
    assert data["source"] == "xposedornot_api"


@pytest.mark.asyncio
async def test_email_breach_clean_address(client: AsyncClient, monkeypatch):
    token = await get_auth_token(client, "clean.user@shadowwatch.io")
    headers = {"Authorization": f"Bearer {token}"}

    async def fake_clean_lookup(email):
        return [], "xposedornot_api"
    monkeypatch.setattr("app.api.v1.scans.check_email_breaches", fake_clean_lookup)

    res = await client.post(
        "/api/v1/scans/email-breach",
        headers=headers,
        json={"email": "clean.account@safe.org"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_breached"] is False
    assert data["breach_count"] == 0
    assert data["risk_level"] == "clean"
    assert data["score_impact"] == 0


@pytest.mark.asyncio
async def test_scans_update_dashboard_metrics(client: AsyncClient, monkeypatch):
    token = await get_auth_token(client, "dashboard.tester@shadowwatch.io")
    headers = {"Authorization": f"Bearer {token}"}

    async def fake_email_lookup(email):
        return ([{"name": "DashboardBreach", "title": "DashboardBreach", "domain": "", "breach_date": "", "added_date": None, "pwn_count": 0, "description": "Reported by XposedOrNot", "logo_path": None, "data_classes": [], "is_verified": True, "is_sensitive": False}], "xposedornot_api")
    monkeypatch.setattr("app.api.v1.scans.check_email_breaches", fake_email_lookup)

    # 1. Check baseline dashboard score (100)
    dash_before = await client.get("/api/v1/dashboard/overview", headers=headers)
    assert dash_before.json()["metrics"]["privacy_score"] == 100

    # 2. Execute a verified XposedOrNot-result scan
    await client.post(
        "/api/v1/scans/email-breach",
        headers=headers,
        json={"email": "breached.sample@domain.com"}
    )

    # 3. Check updated dashboard score
    dash_after = await client.get("/api/v1/dashboard/overview", headers=headers)
    after_data = dash_after.json()
    assert after_data["metrics"]["total_breaches"] == 1
    assert after_data["metrics"]["total_scans_performed"] >= 1
    assert after_data["metrics"]["privacy_score"] < 100
    assert not after_data["score_breakdown"]["verification_warnings"]
    assert len(after_data["recent_scans"]) >= 1

