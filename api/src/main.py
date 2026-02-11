"""
FastAPI application entry point.
T018, T019, T082: Main application with CORS, rate limiting, and error handling
Requirements: FR-032-035, Partial Failure Scenarios
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError

from .config import get_settings
from .routes import api_router, chat_api_router
from .middleware.rate_limit import RateLimitMiddleware

logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="PakAura API",
    description="AI-Powered Task Management API with Cohere Integration",
    version="2.0.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
)

# T018: CORS configuration (FR-034, FR-035)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],  # Only allow configured frontend
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# T017: Rate limiting middleware
app.add_middleware(RateLimitMiddleware)


# T082: Global exception handler for database errors
@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle database errors per Partial Failure Scenarios.

    HTTP 500: Internal server error for write failures
    HTTP 503: Service unavailable for connection failures
    """
    error_message = str(exc).lower()

    # Connection/availability errors
    if any(keyword in error_message for keyword in ["connection", "timeout", "unavailable"]):
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "SERVICE_UNAVAILABLE",
                    "message": "Database temporarily unavailable. Please try again.",
                    "details": [],
                }
            },
        )

    # Other database errors
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again.",
                "details": [],
            }
        },
    )


# Global JWT exception handler - ensures consistent 401 responses
@app.exception_handler(JWTError)
async def jwt_exception_handler(request: Request, exc: JWTError):
    """
    Handle JWT errors globally.

    Returns consistent 401 response for all JWT-related errors.
    Logs error server-side only - never expose JWT details to client.
    """
    logger.warning(f"JWT error on {request.url.path}: {type(exc).__name__}")
    return JSONResponse(
        status_code=401,
        content={
            "error": {
                "code": "AUTHENTICATION_ERROR",
                "message": "Invalid or expired token",
                "details": [],
            }
        },
    )


# Handle HTTPException to ensure consistent error format
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions with consistent format.
    """
    # If detail is already our error format, use it
    if isinstance(exc.detail, dict) and "error" in exc.detail:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    # Otherwise, wrap in our standard format
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": str(exc.detail) if exc.detail else "An error occurred",
                "details": [],
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors without exposing internals."""
    # Don't expose system internals (Assumptions section)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": [],
            }
        },
    )


# Include API router with v1 prefix (FR-032)
app.include_router(api_router)

# Phase III: Include chat router at root level (POST /api/{user_id}/chat)
app.include_router(chat_api_router)


@app.get("/")
async def root():
    """Root endpoint redirects to API docs."""
    return {"message": "Todo API - See /api/docs for documentation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
