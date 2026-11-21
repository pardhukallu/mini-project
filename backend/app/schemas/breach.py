from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class EmailBreachResponse(BaseModel):
    email: str
    is_breached: bool
    breach_count: int
    risk_level: str  # "clean", "low", "medium", "high", "critical"
    score_impact: int
    compromised_data_classes: List[str]
    breaches: List[BreachedAccountRecord]
    source: str  # "xposedornot_api"


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
