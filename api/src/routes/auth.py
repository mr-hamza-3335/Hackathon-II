"""
Authentication routes.
T034, T041, T042, T043: Auth endpoints per api-auth.yaml contract
Requirements: FR-001-007, FR-028-031, NFR-007
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..config import get_settings
from ..schemas import UserRegisterRequest, UserLoginRequest, UserResponse
from ..schemas.common import MessageResponse
from ..services import AuthService
from ..middleware.auth import get_current_user
from ..models import User

router = APIRouter()
settings = get_settings()


def set_auth_cookie(response: Response, token: str) -> None:
    """
    Set HTTP-only authentication cookie.

    NFR-007: HTTP-only cookies with Secure and SameSite=Lax attributes
    FR-028: 24-hour token expiration (via max_age)
    """
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=settings.cookie_httponly,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.cookie_max_age,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """
    Clear authentication cookie on logout.

    FR-031: Clear authentication cookies on logout with immediate effect
    """
    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
    )


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(
    request: UserRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    FR-001: Allow new users to register with email and password
    FR-002: Require passwords to be at least 8 characters
    FR-003: Prevent duplicate email registrations (case-insensitive)
    FR-005: Issue secure authentication tokens upon successful login
    """
    try:
        user, token = await AuthService.register(db, request.email, request.password)
        set_auth_cookie(response, token)
        return user
    except ValueError as e:
        if "already registered" in str(e):
            raise HTTPException(
                status_code=409,
                detail={"error": {
                    "code": "CONFLICT",
                    "message": "Email already registered",
                    "details": [],
                }},
            )
        raise HTTPException(
            status_code=400,
            detail={"error": {
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "details": [],
            }},
        )


@router.post("/login", response_model=UserResponse)
async def login(
    request: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and set session cookie.

    FR-004: Allow registered users to log in with email and password
    FR-005: Issue secure authentication tokens upon successful login
    User Story 2, Scenario 2: Generic error (don't reveal which field is wrong)
    """
    try:
        user, token = await AuthService.login(db, request.email, request.password)
        set_auth_cookie(response, token)
        return user
    except ValueError:
        # Generic error message - don't reveal which field is wrong
        raise HTTPException(
            status_code=401,
            detail={"error": {
                "code": "AUTHENTICATION_ERROR",
                "message": "Invalid email or password",
                "details": [],
            }},
        )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
):
    """
    Log out the current user.

    FR-007: Allow users to log out, invalidating their session
    FR-031: Clear authentication cookies on logout with immediate effect
    """
    clear_auth_cookie(response)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user information.

    Used to check authentication status.
    """
    return current_user
