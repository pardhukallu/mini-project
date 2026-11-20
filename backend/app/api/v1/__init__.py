from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.scans import router as scans_router
from app.api.v1.footprint import router as footprint_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(scans_router)
api_v1_router.include_router(footprint_router)

from app.api.v1.intelligence import router as intelligence_router
api_v1_router.include_router(intelligence_router)
