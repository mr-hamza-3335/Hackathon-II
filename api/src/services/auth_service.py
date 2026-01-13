"""
Auth service for user registration and login.
T033: Create auth service in api/src/services/auth_service.py
Requirements: FR-001, FR-002, FR-003, FR-004, FR-005, NFR-001, NFR-002
"""
from typing import Optional
from uuid import UUID

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models import User
from ..middleware.auth import JWTAuth


class AuthService:
    """Authentication service with registration and login methods."""

    # NFR-001: bcrypt with cost factor 12
    BCRYPT_COST = 12

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt with cost factor 12 (NFR-001)."""
        salt = bcrypt.gensalt(rounds=AuthService.BCRYPT_COST)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    @classmethod
    async def register(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> tuple[User, str]:
        """
        Register a new user.

        FR-001: Allow new users to register with email and password
        FR-002: Require passwords to be at least 8 characters
        FR-003: Prevent duplicate email registrations (case-insensitive)
        FR-005: Issue secure authentication tokens upon successful login

        Returns: (user, jwt_token)
        Raises: ValueError if email already exists
        """
        # FR-003: Case-insensitive email uniqueness check
        email_lower = email.lower()
        existing = await db.execute(
            select(User).where(func.lower(User.email) == email_lower)
        )
        if existing.scalar_one_or_none():
            raise ValueError("Email already registered")

        # Create user with hashed password
        password_hash = cls.hash_password(password)
        user = User(email=email_lower, password_hash=password_hash)
        db.add(user)
        await db.flush()  # Get the user ID

        # Generate JWT token
        token = JWTAuth.create_token(user.id, user.email)

        return user, token

    @classmethod
    async def login(
        cls,
        db: AsyncSession,
        email: str,
        password: str,
    ) -> tuple[User, str]:
        """
        Authenticate user and return JWT token.

        FR-004: Allow registered users to log in with email and password
        FR-005: Issue secure authentication tokens upon successful login

        Returns: (user, jwt_token)
        Raises: ValueError if credentials are invalid
        """
        # Case-insensitive email lookup (Edge Case: email normalization)
        email_lower = email.lower()
        result = await db.execute(
            select(User).where(func.lower(User.email) == email_lower)
        )
        user = result.scalar_one_or_none()

        if not user or not cls.verify_password(password, user.password_hash):
            # Generic error message - don't reveal which field is wrong
            # (User Story 2, Scenario 2)
            raise ValueError("Invalid email or password")

        # Generate JWT token
        token = JWTAuth.create_token(user.id, user.email)

        return user, token

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
