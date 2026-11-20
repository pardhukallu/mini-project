"""
Footprint API router — Phase 3
Endpoints:
  POST /footprint/username-scan   — OSINT username presence check
  POST /footprint/domain-audit    — DNS security audit
"""
from __future__ import annotations
import uuid
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.scan import Scan
from app.schemas.footprint import (
    UsernameCheckRequest,
    UsernameCheckResponse,
    DomainAuditRequest,
    DomainAuditResponse,
)
from app.services.osint import scan_username
from app.services.domain_audit import audit_domain

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/footprint", tags=["footprint"])


# ---------------------------------------------------------------------------
# POST /footprint/username-scan
# ---------------------------------------------------------------------------

@router.post("/username-scan", response_model=UsernameCheckResponse)
async def username_scan(
    body: UsernameCheckRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UsernameCheckResponse:
    """
    Check public username presence across major platforms using HTTP HEAD requests.
    No third-party API key required.
    """
    results = await scan_username(body.username)
    found = [r for r in results if r.present]

    scan_id = str(uuid.uuid4())

    # Persist scan record
    scan = Scan(
        id=scan_id,
        user_id=current_user.id,
        scan_type="username_osint",
        target=body.username,
        risk_level="medium" if found else "low",
        score_impact=len(found) * 2,          # each exposed platform costs 2 pts
        findings_data={
            "username": body.username,
            "platforms_found": len(found),
            "platforms_checked": len(results),
            "results": [r.model_dump() for r in results],
        },
    )
    db.add(scan)
    await db.commit()

    return UsernameCheckResponse(
        username=body.username,
        platforms_checked=len(results),
        platforms_found=len(found),
        results=results,
        scan_id=scan_id,
    )


# ---------------------------------------------------------------------------
# POST /footprint/domain-audit
# ---------------------------------------------------------------------------

@router.post("/domain-audit", response_model=DomainAuditResponse)
async def domain_audit(
    body: DomainAuditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DomainAuditResponse:
    """
    Audit DNS security records for a domain: SPF, DMARC, DKIM, MX.
    Uses dnspython — no external API key required.
    """
    try:
        mx, checks, overall_risk = await run_in_threadpool(audit_domain, body.domain)
    except Exception as exc:
        logger.error("Domain audit failed for %s: %s", body.domain, exc)
        raise HTTPException(status_code=502, detail="DNS resolution failed") from exc

    scan_id = str(uuid.uuid4())
    risk_score = {"none": 0, "low": 5, "medium": 10, "high": 20}.get(overall_risk, 0)

    scan = Scan(
        id=scan_id,
        user_id=current_user.id,
        scan_type="domain_audit",
        target=body.domain,
        risk_level=overall_risk,
        score_impact=risk_score,
        findings_data={
            "domain": body.domain,
            "mx_records": mx,
            "overall_risk": overall_risk,
            "checks": [c.model_dump() for c in checks],
        },
    )
    db.add(scan)
    await db.commit()

    return DomainAuditResponse(
        domain=body.domain,
        mx_records=mx,
        checks=checks,
        overall_risk=overall_risk,
        scan_id=scan_id,
    )
