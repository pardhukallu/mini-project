from app.schemas.token import Token, TokenPayload, RefreshTokenRequest
from app.schemas.user import UserBase, UserCreate, UserLogin, UserResponse
from app.schemas.breach import (
    BreachedAccountRecord,
    EmailBreachRequest,
    EmailBreachResponse,
    ScanHistoryItem,
)
from app.schemas.footprint import (
    UsernameCheckRequest,
    UsernameCheckResponse,
    PlatformPresence,
    DomainAuditRequest,
    DomainAuditResponse,
    DnsRecordCheck,
    FootprintScanSummary,
)

__all__ = [
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "BreachedAccountRecord",
    "EmailBreachRequest",
    "EmailBreachResponse",
    "ScanHistoryItem",
    "UsernameCheckRequest",
    "UsernameCheckResponse",
    "PlatformPresence",
    "DomainAuditRequest",
    "DomainAuditResponse",
    "DnsRecordCheck",
    "FootprintScanSummary",
    "PermissionFinding",
    "PermissionReportRequest",
    "RecommendationItem",
    "RecommendationResponse",
]

from app.schemas.permissions import PermissionFinding, PermissionReportRequest
from app.schemas.intelligence import RecommendationItem, RecommendationResponse
