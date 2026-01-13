"""
Auth request/response schemas.
T032: Create auth request/response schemas in api/src/schemas/auth.py per data-model.md
"""
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """Registration request schema (FR-001, FR-002)."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLoginRequest(BaseModel):
    """Login request schema (FR-004)."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")


class UserResponse(BaseModel):
    """User response schema (excludes password_hash)."""
    id: UUID
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
