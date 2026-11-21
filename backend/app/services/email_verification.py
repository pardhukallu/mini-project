"""Email-existence verification.

Breach databases cannot confirm that a mailbox exists. This module supports a
free, keyless SMTP probe (default) plus optional third-party providers.

The SMTP probe performs a standard RCPT TO handshake and never sends a message.
It only returns "invalid" when the recipient server explicitly says the mailbox
does not exist; timeouts, blocked probes, greylisting and catch-all servers are
reported as "unknown" so they never block a legitimate breach check.
"""
from __future__ import annotations

import asyncio
import smtplib
import socket
from dataclasses import dataclass

import dns.asyncresolver
import dns.exception
import dns.resolver
import httpx

from app.core.config import settings

SMTP_PORT = 25
SMTP_TIMEOUT_SECONDS = 8.0
SMTP_MAX_HOSTS = 2


@dataclass(frozen=True)
class EmailVerificationResult:
    # "valid" | "invalid" | "unknown" | "not_configured"
    status: str
    reason: str = ""


def _interpret_smtp_code(code: int) -> EmailVerificationResult:
    if code in (250, 251):
        return EmailVerificationResult("valid", "The recipient server accepted this mailbox.")
    if code in (550, 551, 553):
        return EmailVerificationResult(
            "invalid", "The recipient server reports that this mailbox does not exist."
        )
    return EmailVerificationResult("unknown", f"The recipient server returned SMTP {code}.")


async def _resolve_mx(domain: str) -> list[str]:
    try:
        answers = await dns.asyncresolver.resolve(domain, "MX", lifetime=SMTP_TIMEOUT_SECONDS)
    except dns.exception.DNSException:
        return []

    hosts = sorted((int(record.preference), str(record.exchange).rstrip(".")) for record in answers)
    return [host for _, host in hosts if host]


def _smtp_probe_sync(mx_host: str, email: str) -> EmailVerificationResult:
    try:
        with smtplib.SMTP(mx_host, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS) as smtp:
            smtp.ehlo_or_helo_if_needed()
            mail_code, _ = smtp.mail("")
            if mail_code >= 400:
                return EmailVerificationResult(
                    "unknown", "The recipient server rejected the verification probe."
                )
            code, _ = smtp.rcpt(email)
            return _interpret_smtp_code(code)
    except (smtplib.SMTPException, OSError, socket.timeout):
        return EmailVerificationResult("unknown", "SMTP verification could not complete.")


async def _verify_smtp(email: str) -> EmailVerificationResult:
    domain = email.rpartition("@")[2]
    if not domain:
        return EmailVerificationResult("unknown", "The email address has no domain.")

    mx_hosts = await _resolve_mx(domain)
    if not mx_hosts:
        return EmailVerificationResult(
            "unknown", "No mail server (MX) records were found for this domain."
        )

    last_reason = "SMTP verification could not complete."
    for mx_host in mx_hosts[:SMTP_MAX_HOSTS]:
        result = await asyncio.to_thread(_smtp_probe_sync, mx_host, email)
        if result.status != "unknown":
            return result
        last_reason = result.reason
    return EmailVerificationResult("unknown", last_reason)


def _map_abstract(payload: dict) -> EmailVerificationResult:
    # Abstract has used both a flat `deliverability` field and the nested
    # `email_deliverability.status` shape, so support either.
    deliverability = payload.get("deliverability")
    if not deliverability and isinstance(payload.get("email_deliverability"), dict):
        deliverability = payload["email_deliverability"].get("status")
    deliverability = str(deliverability or "").strip().upper()
    if deliverability == "DELIVERABLE":
        return EmailVerificationResult("valid", "The provider reports this address as deliverable.")
    if deliverability == "UNDELIVERABLE":
        return EmailVerificationResult("invalid", "The provider reports this address as undeliverable.")
    return EmailVerificationResult("unknown", "The provider could not confirm this address.")


def _map_hunter(payload: dict) -> EmailVerificationResult:
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    status = str(data.get("status", "")).strip().lower()
    result = str(data.get("result", "")).strip().lower()
    if status == "valid" or result == "deliverable":
        return EmailVerificationResult("valid", "The provider reports this address as deliverable.")
    if status == "invalid" or result == "undeliverable":
        return EmailVerificationResult("invalid", "The provider reports this address as undeliverable.")
    return EmailVerificationResult("unknown", "The provider could not confirm this address.")


def _map_zerobounce(payload: dict) -> EmailVerificationResult:
    if payload.get("error"):
        return EmailVerificationResult("unknown", "The provider could not confirm this address.")
    status = str(payload.get("status", "")).strip().lower()
    if status == "valid":
        return EmailVerificationResult("valid", "The provider reports this address as valid.")
    if status in {"invalid", "spamtrap", "abuse", "do_not_mail"}:
        return EmailVerificationResult("invalid", "The provider reports this address as undeliverable.")
    return EmailVerificationResult("unknown", "The provider could not confirm this address.")


def _common_status_error(response: httpx.Response) -> EmailVerificationResult | None:
    if response.status_code in (401, 403):
        return EmailVerificationResult(
            "unknown",
            "The email verification API key was rejected. Check EMAIL_VERIFICATION_API_KEY.",
        )
    if response.status_code == 429:
        return EmailVerificationResult("unknown", "Email verification rate limit reached.")
    return None


async def _verify_abstract(client: httpx.AsyncClient, email: str, api_key: str) -> EmailVerificationResult:
    response = await client.get(
        "https://emailvalidation.abstractapi.com/v1/",
        params={"api_key": api_key, "email": email},
    )
    status_error = _common_status_error(response)
    if status_error:
        return status_error
    response.raise_for_status()
    return _map_abstract(response.json())


async def _verify_hunter(client: httpx.AsyncClient, email: str, api_key: str) -> EmailVerificationResult:
    response = await client.get(
        "https://api.hunter.io/v2/email-verifier",
        params={"email": email, "api_key": api_key},
    )
    status_error = _common_status_error(response)
    if status_error:
        return status_error
    response.raise_for_status()
    return _map_hunter(response.json())


async def _verify_zerobounce(client: httpx.AsyncClient, email: str, api_key: str) -> EmailVerificationResult:
    response = await client.get(
        "https://api.zerobounce.net/v2/validate",
        params={"api_key": api_key, "email": email},
    )
    status_error = _common_status_error(response)
    if status_error:
        return status_error
    response.raise_for_status()
    return _map_zerobounce(response.json())


async def verify_email(email: str) -> EmailVerificationResult:
    provider = (settings.EMAIL_VERIFICATION_PROVIDER or "smtp").strip().lower()
    api_key = (settings.EMAIL_VERIFICATION_API_KEY or "").strip()

    # The built-in SMTP probe is free and needs no key. It is also the fallback
    # whenever a provider is selected but no key is configured.
    if provider == "smtp" or not api_key:
        return await _verify_smtp(email)

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(settings.EMAIL_VERIFICATION_TIMEOUT_SECONDS)
        ) as client:
            if provider == "abstract":
                return await _verify_abstract(client, email, api_key)
            if provider == "hunter":
                return await _verify_hunter(client, email, api_key)
            if provider == "zerobounce":
                return await _verify_zerobounce(client, email, api_key)
    except (httpx.HTTPError, ValueError):
        return EmailVerificationResult("unknown", "Email verification service is temporarily unavailable.")

    return EmailVerificationResult("unknown", f"Unsupported email verification provider: {provider}.")
