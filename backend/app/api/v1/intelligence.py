from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.models.scan import Scan
from app.models.user import User
from app.schemas.permissions import PermissionReportRequest
from app.services.scoring import calculate_score
from app.services.recommendations import generate_recommendations

router = APIRouter(tags=["Security intelligence"])

@router.post("/permissions/report")
async def save_permission_report(body: PermissionReportRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    high = [x.model_dump() for x in body.extensions if x.risk_level.lower() == "high"]
    medium = [x.model_dump() for x in body.extensions if x.risk_level.lower() == "medium"]
    scan = Scan(user_id=current_user.id, scan_type="permissions", target="Chrome extension inventory", status="completed", risk_level="high" if high else ("medium" if medium else "clean"), score_impact=min(20, len(high)*4), summary=f"Audited {len(body.extensions)} extensions; {len(high)} high-risk finding(s).", findings_data={"source": body.source, "scanned_at": body.scanned_at, "extensions": [x.model_dump() for x in body.extensions], "sites": body.sites, "high_risk": high, "medium_risk": medium})
    db.add(scan)
    await db.flush()
    return {"scan_id": scan.id, "extensions_audited": len(body.extensions), "high_risk": len(high), "medium_risk": len(medium)}

@router.get("/intelligence/score")
async def get_score(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Scan).where(Scan.user_id == current_user.id).order_by(Scan.created_at))
    score = calculate_score(result.scalars().all())
    return score

@router.get("/intelligence/recommendations")
async def recommendations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Scan).where(Scan.user_id == current_user.id).order_by(Scan.created_at))
    score = calculate_score(result.scalars().all())
    return await generate_recommendations(score)

@router.get("/reports/export")
async def export_report(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Scan).where(Scan.user_id == current_user.id).order_by(desc(Scan.created_at)))
    scans = result.scalars().all()
    score = calculate_score(scans)
    return {"product": "ShadowWatch", "generated_for": current_user.email, "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "score": score, "scans": [{"id": s.id, "type": s.scan_type, "target": s.target, "status": s.status, "risk_level": s.risk_level, "summary": s.summary, "findings": s.findings_data, "created_at": s.created_at.isoformat()} for s in scans]}
