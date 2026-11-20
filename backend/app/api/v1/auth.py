from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user, get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.models.revoked_token import RevokedToken
from app.api.deps import security_bearer
from app.schemas.token import RefreshTokenRequest, Token
from datetime import datetime, timezone
from app.schemas.user import UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Register a new user account with Argon2id hashed password."""
    # Check if user already exists
    existing_user = await db.execute(select(User).where(User.email == user_in.email.lower()))
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash password with Argon2id
    hashed_pwd = get_password_hash(user_in.password)

    new_user = User(
        email=user_in.email.lower(),
        hashed_password=hashed_pwd,
        full_name=user_in.full_name or ""
    )
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)

    # Generate tokens
    access_token = create_access_token(new_user.id)
    refresh_token = create_refresh_token(new_user.id)

    return {
        "message": "User registered successfully.",
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "user": UserResponse.model_validate(new_user).model_dump()
    }


@router.post("/login", response_model=dict)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Authenticate user with email and Argon2id password verification, returning JWT tokens."""
    result = await db.execute(select(User).where(User.email == login_data.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive."
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return {
        "tokens": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        },
        "user": UserResponse.model_validate(user).model_dump()
    }


@router.post("/refresh", response_model=Token)
async def refresh_token_endpoint(
    refresh_req: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Exchange a valid refresh token for a new access token and refresh token."""
    payload = decode_token(refresh_req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    if not payload.get("jti"):
        raise HTTPException(status_code=401, detail="Invalid refresh token.")
    revoked = await db.execute(select(RevokedToken).where(RevokedToken.jti == payload["jti"]))
    if revoked.scalar_one_or_none():
        raise HTTPException(status_code=401, detail="Refresh token has been revoked.")
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive."
        )

    # Rotate refresh tokens: the previous token cannot be reused.
    db.add(RevokedToken(jti=payload["jti"], token_type="refresh", expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc)))
    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
) -> UserResponse:
    """Return the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    body: RefreshTokenRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke both the presented access token and refresh token."""
    access_payload = decode_token(credentials.credentials) if credentials else None
    refresh_payload = decode_token(body.refresh_token)
    if access_payload and access_payload.get("jti"):
        db.add(RevokedToken(jti=access_payload["jti"], token_type="access", expires_at=datetime.fromtimestamp(access_payload["exp"], timezone.utc)))
    if refresh_payload and refresh_payload.get("type") == "refresh" and refresh_payload.get("sub") == current_user.id and refresh_payload.get("jti"):
        db.add(RevokedToken(jti=refresh_payload["jti"], token_type="refresh", expires_at=datetime.fromtimestamp(refresh_payload["exp"], timezone.utc)))
    return {"message": "Session tokens revoked successfully."}
