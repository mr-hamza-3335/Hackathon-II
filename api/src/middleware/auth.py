"""
JWT verification middleware.
T016: Create JWT verification middleware in api/src/middleware/auth.py with 24-hour expiration check
Requirements: FR-006, FR-028, FR-029

SECURITY:
- JWT errors logged server-side only
- Generic error messages returned to client
- No internal details exposed
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import Request, HTTPException, Depends
from fastapi.security import APIKeyCookie
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config import get_settings
from ..db import get_db
from ..models import User

logger = logging.getLogger(__name__)
settings = get_settings()

# Cookie-based auth scheme (NFR-007)
cookie_scheme = APIKeyCookie(name=settings.cookie_name, auto_error=False)


class JWTAuth:
    """JWT authentication handler."""

    @staticmethod
    def create_token(user_id: UUID, email: str) -> str:
        """
        Create JWT token with 24-hour expiration (FR-028).

        Payload: {user_id, email, exp, iat}
        Algorithm: HS256 (NFR-002)
        """
        now = datetime.now(timezone.utc)
        expire = now.timestamp() + (settings.jwt_expiration_hours * 3600)

        payload = {
            "sub": str(user_id),
            "email": email,
            "iat": now.timestamp(),
            "exp": expire,
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """
        Decode and validate JWT token.

        Returns None if token is invalid or expired (FR-029).
        SECURITY: Errors logged server-side only.
        """
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm],
            )
            return payload
        except JWTError as e:
            # Log error server-side only - never expose to client
            logger.warning(f"JWT decode failed: {type(e).__name__}")
            return None


async def get_current_user(
    token: Optional[str] = Depends(cookie_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that validates JWT and returns current user.

    FR-006: Validate authentication tokens on every protected request.
    FR-029: Reject expired tokens and redirect users to login.
    """
    if not token:
        raise HTTPException(
            status_code=401,
            detail={"error": {
                "code": "AUTHENTICATION_ERROR",
                "message": "Not authenticated",
                "details": [],
            }},
        )

    payload = JWTAuth.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail={"error": {
                "code": "AUTHENTICATION_ERROR",
                "message": "Invalid or expired token",
                "details": [],
            }},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail={"error": {
                "code": "AUTHENTICATION_ERROR",
                "message": "Invalid token payload",
                "details": [],
            }},
        )

    # Fetch user from database
    result = await db.execute(select(User).where(User.id == UUID(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=401,
            detail={"error": {
                "code": "AUTHENTICATION_ERROR",
                "message": "User not found",
                "details": [],
            }},
        )

    return user
