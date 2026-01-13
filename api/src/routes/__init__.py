"""
Routes module with health check and router configuration.
T020: Create health check endpoint GET /api/v1/health
Phase 3: Added AI assistant routes
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .tasks import router as tasks_router
from .ai import router as ai_router

# Main API router with v1 prefix (FR-032)
api_router = APIRouter(prefix="/api/v1")

# Health check endpoint
@api_router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0", "phase": 3}

# Include sub-routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])

__all__ = ["api_router"]
