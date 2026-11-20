from pydantic import BaseModel, Field
from typing import Literal

class PermissionFinding(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    permissions: list[str] = Field(default_factory=list)
    risk_level: Literal["high", "medium", "low"]
    reason: str = ""

class PermissionReportRequest(BaseModel):
    source: str = "chrome_extension"
    scanned_at: str | None = None
    extensions: list[PermissionFinding] = Field(default_factory=list, max_length=500)
    sites: list[dict] = Field(default_factory=list, max_length=500)
