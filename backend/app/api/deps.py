from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.models.revoked_token import RevokedToken

security_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency that extracts and validates the JWT Bearer token and returns the current user."""
    auth_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials or not credentials.credentials:
        raise auth_exception
    
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise auth_exception
    
    token_type = payload.get("type")
    user_id = payload.get("sub")
    jti = payload.get("jti")
    if not jti:
        raise auth_exception
    revoked = await db.execute(select(RevokedToken).where(RevokedToken.jti == jti))
    if revoked.scalar_one_or_none():
        raise auth_exception
    if token_type != "access" or not user_id:
        raise auth_exception
    
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise auth_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    return user
