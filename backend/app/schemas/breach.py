from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class BreachedAccountRecord(BaseModel):
    name: str
    title: str
    domain: str
    breach_date: str
    added_date: Optional[str] = None
    pwn_count: int
    description: str
    logo_path: Optional[str] = None
    data_classes: List[str]
    is_verified: bool = True
    is_sensitive: bool = False

    model_config = ConfigDict(from_attributes=True)


class EmailBreachRequest(BaseModel):
    email: EmailStr


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
