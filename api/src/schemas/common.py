"""
Common error response schemas per FR-026 format.
T015: Create common error response schemas in api/src/schemas/common.py per FR-026 format
"""
from pydantic import BaseModel
from typing import Optional


class ErrorDetail(BaseModel):
    """Field-level error detail."""
    field: str
    message: str


class ErrorContent(BaseModel):
    """Error content structure per FR-026."""
    code: str
    message: str
    details: list[ErrorDetail] = []


class ErrorResponse(BaseModel):
    """
    Structured error response format per FR-026.

    Format: {error: {code, message, details[]}}

    Error Codes:
    - VALIDATION_ERROR: Input validation failures (400)
    - AUTHENTICATION_ERROR: Invalid/missing credentials (401)
    - AUTHORIZATION_ERROR: Access to another user's resource (403)
    - NOT_FOUND: Resource doesn't exist (404)
    - CONFLICT: Email already registered (409)
    - RATE_LIMITED: Too many requests (429)
    - INTERNAL_ERROR: Unexpected server error (500)
    - SERVICE_UNAVAILABLE: Database/service unavailable (503)
    """
    error: ErrorContent


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
