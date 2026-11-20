"""
DNS domain security auditor — Phase 3
Checks SPF, DMARC, DKIM, and MX records using dnspython.
No external API key required — uses system DNS resolver.
"""
from __future__ import annotations
import logging
from typing import Optional
import smtplib
import ssl

import dns.resolver
import dns.exception

from app.schemas.footprint import DnsRecordCheck

logger = logging.getLogger(__name__)

# DKIM selectors to probe (common ones used by major providers)
_DKIM_SELECTORS = [
    "default", "google", "mail", "dkim", "k1",
    "selector1", "selector2", "s1", "s2",
]

# Risk rating weights for final overall_risk calculation
_RISK_WEIGHTS = {"none": 0, "low": 1, "medium": 2, "high": 3}


def _resolve_txt(name: str) -> list[str]:
    """Return all TXT record strings for the given DNS name, or [] on error."""
    try:
        answers = dns.resolver.resolve(name, "TXT", lifetime=5)
        records: list[str] = []
        for rdata in answers:
            # TXT records can be multi-string; join them
            joined = "".join(s.decode() if isinstance(s, bytes) else s for s in rdata.strings)
            records.append(joined)
        return records
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
        return []


def _resolve_mx(domain: str) -> list[str]:
    """Return MX record exchange names sorted by preference, or []."""
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=5)
        return [str(r.exchange).rstrip(".") for r in sorted(answers, key=lambda x: x.preference)]
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.exception.DNSException):
        return []


# ---------------------------------------------------------------------------
# Individual check helpers
# ---------------------------------------------------------------------------

def _check_spf(domain: str) -> DnsRecordCheck:
    records = [r for r in _resolve_txt(domain) if r.startswith("v=spf1")]
    if not records:
        return DnsRecordCheck(
            record_type="SPF",
            present=False,
            risk_level="high",
            note="No SPF record — anyone can spoof email from this domain",
        )
    value = records[0][:300]
    # Assess policy strength
    if "-all" in value:
        policy, risk, note = "fail", "none", "Hard fail (-all) — strict SPF enforcement"
    elif "~all" in value:
        policy, risk, note = "softfail", "low", "Soft fail (~all) — SPF configured but not strictly enforced"
    elif "?all" in value:
        policy, risk, note = "neutral", "medium", "Neutral (?all) — SPF present but offers little protection"
    elif "+all" in value:
        policy, risk, note = "pass-all", "high", "+all allows any server to send — SPF is effectively disabled"
    else:
        policy, risk, note = "unknown", "low", "SPF present — policy mechanism not fully parsed"

    return DnsRecordCheck(
        record_type="SPF", present=True,
        value=value, policy=policy, risk_level=risk, note=note,
    )


def _check_dmarc(domain: str) -> DnsRecordCheck:
    records = _resolve_txt(f"_dmarc.{domain}")
    dmarc_records = [r for r in records if r.startswith("v=DMARC1")]
    if not dmarc_records:
        return DnsRecordCheck(
            record_type="DMARC",
            present=False,
            risk_level="high",
            note="No DMARC record — phishing emails from this domain reach inboxes undetected",
        )
    value = dmarc_records[0][:300]
    # Parse p= tag
    policy = "none"
    for part in value.split(";"):
        part = part.strip()
        if part.lower().startswith("p="):
            policy = part[2:].strip().lower()
            break

    if policy == "reject":
        risk, note = "none", "DMARC policy=reject — strongest protection, failing messages rejected"
    elif policy == "quarantine":
        risk, note = "low", "DMARC policy=quarantine — failing messages sent to spam"
    elif policy == "none":
        risk, note = "medium", "DMARC policy=none — monitoring only, no enforcement"
    else:
        risk, note = "low", f"DMARC present with policy={policy}"

    return DnsRecordCheck(
        record_type="DMARC", present=True,
        value=value, policy=policy, risk_level=risk, note=note,
    )


def _check_dkim(domain: str) -> DnsRecordCheck:
    """Probe common DKIM selectors; report presence if any found."""
    found_selector: Optional[str] = None
    found_value: Optional[str] = None

    for selector in _DKIM_SELECTORS:
        name = f"{selector}._domainkey.{domain}"
        records = _resolve_txt(name)
        dkim = [r for r in records if "v=DKIM1" in r or "k=rsa" in r or "p=" in r]
        if dkim:
            found_selector = selector
            found_value = dkim[0][:300]
            break

    if found_selector:
        return DnsRecordCheck(
            record_type="DKIM", present=True,
            value=found_value,
            policy=found_selector,
            risk_level="none",
            note=f"DKIM record found (selector: {found_selector}) — email signing configured",
        )
    return DnsRecordCheck(
        record_type="DKIM", present=False,
        risk_level="medium",
        note="No DKIM record found across common selectors — email authentication may be incomplete",
    )


def _probe_starttls(host: str) -> Optional[bool]:
    """Return True/False when SMTP STARTTLS is observed; None when unreachable."""
    try:
        with smtplib.SMTP(host, 25, timeout=3.0) as smtp:
            smtp.ehlo_or_helo_if_needed()
            if not smtp.has_extn("starttls"):
                return False
            smtp.starttls(context=ssl.create_default_context())
            return True
    except (OSError, smtplib.SMTPException, ssl.SSLError) as exc:
        logger.info("Could not verify STARTTLS for %s: %s", host, exc)
        return None


def _check_mx(domain: str, mx_records: list[str]) -> DnsRecordCheck:
    if not mx_records:
        return DnsRecordCheck(
            record_type="MX", present=False,
            risk_level="low",
            note="No MX records — domain does not appear to receive email",
        )
    # Probe a small number of advertised MX hosts to keep the audit bounded.
    probes = [_probe_starttls(host) for host in mx_records[:2]]
    if any(value is False for value in probes):
        risk = "high"
        tls_supported = False
        note = "At least one probed MX host did not advertise STARTTLS; transport encryption could not be assured"
    elif all(value is True for value in probes):
        risk = "none"
        tls_supported = True
        note = "STARTTLS negotiated successfully with all probed MX hosts"
    else:
        risk = "medium"
        tls_supported = None
        note = "MX records exist, but one or more SMTP hosts could not be reached to verify STARTTLS"
    return DnsRecordCheck(
        record_type="MX", present=True, value=", ".join(mx_records[:3]),
        tls_supported=tls_supported, risk_level=risk,
        note=f"{len(mx_records)} MX record(s) found. {note}",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def audit_domain(domain: str) -> tuple[list[str], list[DnsRecordCheck], str]:
    """
    Audit DNS security records for a domain.
    Returns: (mx_records, checks, overall_risk)
    """
    mx = _resolve_mx(domain)
    checks = [
        _check_spf(domain),
        _check_dmarc(domain),
        _check_dkim(domain),
        _check_mx(domain, mx),
    ]

    max_weight = max(_RISK_WEIGHTS.get(c.risk_level, 0) for c in checks)
    overall = {v: k for k, v in _RISK_WEIGHTS.items()}[max_weight]

    return mx, checks, overall
