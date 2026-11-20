"""
Phase 3 backend tests — Digital Footprint & OSINT
Tests use mocks for external DNS and HTTP calls to ensure determinism.
"""
from __future__ import annotations
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from httpx import AsyncClient

from app.schemas.footprint import PlatformPresence, DnsRecordCheck


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_token(client: AsyncClient) -> str:
    """Register + login a test user, return access token."""
    await client.post("/api/v1/auth/register", json={
        "email": "footprint@test.com",
        "password": "SecurePass!99",
        "full_name": "Footprint Tester",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "footprint@test.com",
        "password": "SecurePass!99",
    })
    # Login response: {"tokens": {"access_token": ..., ...}, "user": {...}}
    return resp.json()["tokens"]["access_token"]


# ---------------------------------------------------------------------------
# Username OSINT tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_username_scan_returns_results(client: AsyncClient):
    """Username scan returns a list of platform results."""
    token = await _get_token(client)

    # Mock the actual HTTP calls to avoid network dependency
    mock_results = [
        PlatformPresence(
            platform="GitHub", url="https://github.com/testuser",
            present=True, status_code=200, note="Profile page found"
        ),
        PlatformPresence(
            platform="Reddit", url="https://www.reddit.com/user/testuser",
            present=False, status_code=404, note="No profile found"
        ),
    ]
    with patch("app.api.v1.footprint.scan_username", new=AsyncMock(return_value=mock_results)):
        resp = await client.post(
            "/api/v1/footprint/username-scan",
            json={"username": "testuser"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["platforms_checked"] == 2
    assert data["platforms_found"] == 1
    assert len(data["results"]) == 2
    assert "scan_id" in data


@pytest.mark.asyncio
async def test_username_scan_invalid_username(client: AsyncClient):
    """Invalid username (special chars) returns 422."""
    token = await _get_token(client)
    resp = await client.post(
        "/api/v1/footprint/username-scan",
        json={"username": "user name with spaces!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_username_scan_requires_auth(client: AsyncClient):
    """Endpoint requires JWT — unauthenticated returns 401."""
    resp = await client.post(
        "/api/v1/footprint/username-scan",
        json={"username": "testuser"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Domain audit tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_domain_audit_returns_checks(client: AsyncClient):
    """Domain audit returns SPF, DMARC, DKIM, MX checks."""
    token = await _get_token(client)

    mock_checks = [
        DnsRecordCheck(record_type="SPF", present=True, value="v=spf1 include:_spf.google.com -all",
                       policy="fail", risk_level="none", note="Hard fail"),
        DnsRecordCheck(record_type="DMARC", present=True, value="v=DMARC1; p=reject;",
                       policy="reject", risk_level="none", note="Reject policy"),
        DnsRecordCheck(record_type="DKIM", present=True, value="v=DKIM1; k=rsa; p=abc",
                       policy="google", risk_level="none", note="DKIM found"),
        DnsRecordCheck(record_type="MX", present=True, value="aspmx.l.google.com",
                       risk_level="none", note="1 MX record"),
    ]

    with patch("app.api.v1.footprint.audit_domain", return_value=(["aspmx.l.google.com"], mock_checks, "none")):
        resp = await client.post(
            "/api/v1/footprint/domain-audit",
            json={"domain": "gmail.com"},
            headers={"Authorization": f"Bearer {token}"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["domain"] == "gmail.com"
    assert data["overall_risk"] == "none"
    assert len(data["checks"]) == 4
    record_types = {c["record_type"] for c in data["checks"]}
    assert record_types == {"SPF", "DMARC", "DKIM", "MX"}
    assert "scan_id" in data


@pytest.mark.asyncio
async def test_domain_audit_invalid_domain(client: AsyncClient):
    """Invalid domain format returns 422."""
    token = await _get_token(client)
    resp = await client.post(
        "/api/v1/footprint/domain-audit",
        json={"domain": "not a domain!"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 422
