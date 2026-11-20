"""
Footprint Pydantic schemas — Phase 3
"""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, field_validator
import re


# ---------------------------------------------------------------------------
# Username OSINT
# ---------------------------------------------------------------------------

class UsernameCheckRequest(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) < 1 or len(v) > 64:
            raise ValueError("Username must be 1–64 characters")
        # Allow alphanumeric, dashes, underscores, dots
        if not re.match(r"^[A-Za-z0-9._-]+$", v):
            raise ValueError("Username may only contain letters, digits, ., _, -")
        return v


class PlatformPresence(BaseModel):
    platform: str
    url: str
    present: bool
    verified: bool = True
    status_code: Optional[int] = None
    note: Optional[str] = None


class UsernameCheckResponse(BaseModel):
    username: str
    platforms_checked: int
    platforms_found: int
    results: list[PlatformPresence]
    scan_id: str


# ---------------------------------------------------------------------------
# Domain / DNS Audit
# ---------------------------------------------------------------------------

class DomainAuditRequest(BaseModel):
    domain: str

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        v = v.strip().lower()
        # Strip protocol if pasted
        v = re.sub(r"^https?://", "", v)
        v = v.split("/")[0]  # strip path
        # Basic domain pattern: label.label (at least one dot)
        if not re.match(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)+$", v):
            raise ValueError("Invalid domain name")
        return v


class DnsRecordCheck(BaseModel):
    record_type: str          # SPF, DMARC, DKIM, MX
    present: bool
    value: Optional[str] = None   # First matching record value (truncated to 300 chars)
    policy: Optional[str] = None  # Parsed enforcement level where applicable
    tls_supported: Optional[bool] = None
    risk_level: str           # none | low | medium | high
    note: str


class DomainAuditResponse(BaseModel):
    domain: str
    mx_records: list[str]
    checks: list[DnsRecordCheck]
    overall_risk: str         # none | low | medium | high
    scan_id: str


# ---------------------------------------------------------------------------
# Combined footprint response (for future full-scan aggregation)
# ---------------------------------------------------------------------------

class FootprintScanSummary(BaseModel):
    username_scans: int
    domain_audits: int
    total_findings: int
