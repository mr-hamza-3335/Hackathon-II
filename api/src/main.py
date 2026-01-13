"""
FastAPI application entry point.
T018, T019, T082: Main application with CORS, rate limiting, and error handling
Requirements: FR-032-035, Partial Failure Scenarios
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from .config import get_settings
from .routes import api_router
from .middleware.rate_limit import RateLimitMiddleware

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Todo API",
    description="Phase II Full-Stack Todo Application API",
    version="1.0.0",
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
)

# T018: CORS configuration (FR-034, FR-035)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],  # Only allow configured frontend
    allow_credentials=True,  # Required for cookies
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
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


@app.get("/")
async def root():
    """Root endpoint redirects to API docs."""
    return {"message": "Todo API - See /api/docs for documentation"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
