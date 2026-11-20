from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=Dict[str, Any])
async def get_dashboard_overview(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    Returns verified dashboard metrics for the authenticated user,
    aggregating actual scans from the database.
    """
    from app.services.scoring import calculate_score, build_score_history
    stmt = select(Scan).where(Scan.user_id == current_user.id).order_by(desc(Scan.created_at))
    result = await db.execute(stmt)
    all_scans: List[Scan] = [scan for scan in result.scalars().all() if scan.scan_type != "password_check"]
    scans = all_scans
    score = calculate_score(all_scans)
    scan_history = [{
        "id": s.id, "scan_type": s.scan_type, "target": s.target,
        "status": s.status, "risk_level": s.risk_level,
        "score_impact": s.score_impact, "summary": s.summary,
        "created_at": s.created_at.isoformat(),
    } for s in scans]

    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
        },
        "metrics": {
            "privacy_score": score["privacy_score"],
            **score["metrics"],
            "total_scans_performed": len(all_scans),
        },
        "score_breakdown": {
            "base_score": 100,
            "deductions": score["deductions"],
            "category_penalties": score["category_penalties"],
            "evidence": score["evidence"],
            "verification_warnings": score["verification_warnings"]
        },
        "recent_scans": scan_history,
        "score_history": build_score_history(all_scans)
    }
