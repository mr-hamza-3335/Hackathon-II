"""
Routes module with health check and router configuration.
T020: Create health check endpoint GET /api/v1/health
Phase III: Cohere AI chat endpoint with MCP-style tools
"""
from fastapi import APIRouter

from .auth import router as auth_router
from .tasks import router as tasks_router
from .chat import router as chat_router

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

# Phase III: Chat router (without v1 prefix per spec - POST /api/{user_id}/chat)
# This is included separately for direct access at /api/{user_id}/chat
chat_api_router = chat_router

__all__ = ["api_router", "chat_api_router"]
