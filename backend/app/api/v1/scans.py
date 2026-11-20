from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.schemas.breach import (
    BreachedAccountRecord,
    EmailBreachRequest,
    EmailBreachResponse,
    ScanHistoryItem,
)
from app.services.xposedornot import check_email_breaches
import httpx

router = APIRouter(prefix="/scans", tags=["Exposure Scans"])


@router.post("/email-breach", response_model=EmailBreachResponse)
async def scan_email_breach(
    request: EmailBreachRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> EmailBreachResponse:
    """
    Scans an email address against XposedOrNot public breach data and records
    the audit result in the database.
    """
    clean_email = request.email.lower()
    try:
        raw_breaches, source = await check_email_breaches(clean_email)
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 429:
            raise HTTPException(status_code=429, detail="XposedOrNot free API rate limit reached. Try again later.") from exc
        raise HTTPException(status_code=502, detail="XposedOrNot breach lookup is currently unavailable; no clean result can be confirmed.") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail="XposedOrNot breach lookup is currently unavailable; no clean result can be confirmed.") from exc

    breach_count = len(raw_breaches)
    is_breached = breach_count > 0

    # Collect unique compromised data classes
    all_classes = set()
    for b in raw_breaches:
        for dc in b.get("data_classes", []):
            all_classes.add(dc)
    data_classes_list = sorted(list(all_classes))

    # Calculate risk level & score impact
    if breach_count == 0:
        risk_level = "clean"
        score_impact = 0
        summary_text = f"Email {clean_email} was not found in any known public breaches."
    elif breach_count == 1:
        risk_level = "low"
        score_impact = 10
        summary_text = f"Email {clean_email} identified in 1 data breach."
    elif breach_count <= 3:
        risk_level = "medium"
        score_impact = breach_count * 10
        summary_text = f"Email {clean_email} identified in {breach_count} data breaches."
    else:
        risk_level = "critical"
        score_impact = min(40, breach_count * 10)
        summary_text = f"CRITICAL: Email {clean_email} identified in {breach_count} data breaches."

    # Record scan in database
    scan_record = Scan(
        user_id=current_user.id,
        scan_type="email_breach",
        target=clean_email,
        status="completed",
        risk_level=risk_level,
        score_impact=score_impact,
        summary=summary_text,
        findings_data={
            "breach_count": breach_count,
            "is_breached": is_breached,
            "source": source,
            "data_classes": data_classes_list,
            "breaches": raw_breaches,
        }
    )
    db.add(scan_record)
    await db.flush()
    await db.refresh(scan_record)

    formatted_breaches = [BreachedAccountRecord(**b) for b in raw_breaches]

    return EmailBreachResponse(
        email=clean_email,
        is_breached=is_breached,
        breach_count=breach_count,
        risk_level=risk_level,
        score_impact=score_impact,
        compromised_data_classes=data_classes_list,
        breaches=formatted_breaches,
        source=source,
    )


@router.get("/history", response_model=List[ScanHistoryItem])
async def get_scan_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[ScanHistoryItem]:
    """Retrieves all past scan records for the authenticated user."""
    stmt = (
        select(Scan)
        .where(Scan.user_id == current_user.id, Scan.scan_type != "password_check")
        .order_by(desc(Scan.created_at))
        .limit(50)
    )
    result = await db.execute(stmt)
    scans = result.scalars().all()
    return [ScanHistoryItem.model_validate(s) for s in scans]


@router.get("/{scan_id}", response_model=ScanHistoryItem)
async def get_scan_detail(
    scan_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> ScanHistoryItem:
    """Retrieves detailed audit findings for a specific scan."""
    stmt = select(Scan).where(Scan.id == scan_id, Scan.user_id == current_user.id, Scan.scan_type != "password_check")
    result = await db.execute(stmt)
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan record not found."
        )

    return ScanHistoryItem.model_validate(scan)
