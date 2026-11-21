import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# A real domain extension is alphabetic (com, org, io, рф, ...) or punycode.
_PUNYCODE_TLD_RE = re.compile(r"^xn--[A-Za-z0-9-]{2,}$")


def _is_real_tld(tld: str) -> bool:
    if _PUNYCODE_TLD_RE.match(tld):
        return True
    return len(tld) >= 2 and tld.isalpha()


class BreachedAccountRecord(BaseModel):
    # The XposedOrNot email-check endpoint supplies breach names only.
    # Do not manufacture metadata that the endpoint did not return.
    name: str
    title: Optional[str] = None
    domain: Optional[str] = None
    breach_date: Optional[str] = None
    added_date: Optional[str] = None
    pwn_count: Optional[int] = None
    description: Optional[str] = None
    logo_path: Optional[str] = None
    data_classes: List[str] = Field(default_factory=list)
    is_verified: Optional[bool] = None
    is_sensitive: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class EmailBreachRequest(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("email")
    @classmethod
    def require_real_tld(cls, value: str) -> str:
        """Reject addresses such as `a@b.c` that EmailStr accepts syntactically."""
        domain = str(value).rpartition("@")[2]
        tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
        if not _is_real_tld(tld):
            raise ValueError("Enter a valid email address, for example name@example.com.")
        return str(value)


class EmailBreachResponse(BaseModel):
    email: str
    is_breached: bool
    breach_count: int
    risk_level: str  # "clean", "low", "medium", "high", "critical"
    score_impact: int
    compromised_data_classes: List[str]
    breaches: List[BreachedAccountRecord]
    source: str  # "xposedornot_api"
    # Whether a third-party provider could confirm the mailbox exists.
    email_verification: str = "not_configured"  # "valid", "unknown", "not_configured"
    email_verification_reason: Optional[str] = None


class ScanHistoryItem(BaseModel):
    id: str
    scan_type: str
    target: str
    status: str
    risk_level: str
    score_impact: int
    summary: str
    findings_data: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
