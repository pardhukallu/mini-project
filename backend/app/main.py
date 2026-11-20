from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_v1_router
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on application startup
    await init_db()
    yield


if settings.ENVIRONMENT.lower() == "production" and (
    len(settings.SECRET_KEY) < 32
    or settings.SECRET_KEY.startswith("shadowwatch_dev_")
    or "replace-with" in settings.SECRET_KEY.lower()
):
    raise RuntimeError("Set a unique SECRET_KEY of at least 32 characters before running ShadowWatch in production.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI Personal Data Exposure Monitor API - Cybersecurity Monitoring Platform",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"^chrome-extension://[a-p]{32}$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 routes
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["System"])
async def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get("/", tags=["System"])
async def root():
    """Root entry point with documentation links."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "version": settings.VERSION
    }
