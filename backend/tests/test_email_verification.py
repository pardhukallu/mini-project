import httpx
import pytest

from app.core.config import settings
from app.services.email_verification import (
    EmailVerificationResult,
    _common_status_error,
    _interpret_smtp_code,
    _map_abstract,
    _map_hunter,
    _map_zerobounce,
    verify_email,
)


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"deliverability": "DELIVERABLE"}, "valid"),
        ({"deliverability": "UNDELIVERABLE"}, "invalid"),
        ({"deliverability": "UNKNOWN"}, "unknown"),
        ({"email_deliverability": {"status": "deliverable"}}, "valid"),
        ({"email_deliverability": {"status": "undeliverable"}}, "invalid"),
        ({"email_deliverability": {"status": "risky"}}, "unknown"),
        ({}, "unknown"),
    ],
)
def test_abstract_mapping(payload, expected):
    assert _map_abstract(payload).status == expected


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"data": {"status": "valid"}}, "valid"),
        ({"data": {"status": "invalid"}}, "invalid"),
        ({"data": {"result": "deliverable"}}, "valid"),
        ({"data": {"result": "undeliverable"}}, "invalid"),
        ({"data": {"status": "accept_all"}}, "unknown"),
        ({"data": {"status": "unknown"}}, "unknown"),
    ],
)
def test_hunter_mapping(payload, expected):
    assert _map_hunter(payload).status == expected


@pytest.mark.parametrize(
    "payload, expected",
    [
        ({"status": "valid"}, "valid"),
        ({"status": "invalid"}, "invalid"),
        ({"status": "spamtrap"}, "invalid"),
        ({"status": "catch-all"}, "unknown"),
        ({"status": "unknown"}, "unknown"),
        ({"error": "Invalid API key"}, "unknown"),
    ],
)
def test_zerobounce_mapping(payload, expected):
    assert _map_zerobounce(payload).status == expected


@pytest.mark.parametrize("status_code", [401, 403])
def test_rejected_api_key_is_reported(status_code):
    request = httpx.Request("GET", "https://example.com")
    result = _common_status_error(httpx.Response(status_code, request=request))
    assert result is not None
    assert "API key" in result.reason


def test_rate_limit_is_reported():
    request = httpx.Request("GET", "https://example.com")
    result = _common_status_error(httpx.Response(429, request=request))
    assert result is not None
    assert "rate limit" in result.reason


def test_ok_status_has_no_common_error():
    request = httpx.Request("GET", "https://example.com")
    assert _common_status_error(httpx.Response(200, request=request)) is None


@pytest.mark.parametrize(
    "code, expected",
    [
        (250, "valid"),
        (251, "valid"),
        (550, "invalid"),
        (551, "invalid"),
        (553, "invalid"),
        (450, "unknown"),
        (451, "unknown"),
        (421, "unknown"),
        (503, "unknown"),
    ],
)
def test_smtp_code_interpretation(code, expected):
    assert _interpret_smtp_code(code).status == expected


@pytest.mark.asyncio
async def test_verify_email_without_key_uses_smtp(monkeypatch):
    async def fake_smtp(email):
        return EmailVerificationResult("invalid", "The recipient server reports that this mailbox does not exist.")

    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_API_KEY", None)
    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_PROVIDER", "abstract")
    monkeypatch.setattr("app.services.email_verification._verify_smtp", fake_smtp)

    result = await verify_email("missing@example.com")
    assert result.status == "invalid"


@pytest.mark.asyncio
async def test_verify_email_defaults_to_smtp(monkeypatch):
    async def fake_smtp(email):
        return EmailVerificationResult("valid", "The recipient server accepted this mailbox.")

    monkeypatch.setattr(settings, "EMAIL_VERIFICATION_PROVIDER", "smtp")
    monkeypatch.setattr("app.services.email_verification._verify_smtp", fake_smtp)

    result = await verify_email("user@example.com")
    assert result.status == "valid"
