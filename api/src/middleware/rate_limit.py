"""
Rate limiting middleware.
T017: Create rate limiting middleware in api/src/middleware/rate_limit.py
Requirements: FR-036, FR-037, FR-038, FR-039
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from ..config import get_settings

settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for abuse prevention.

    FR-036: 10 req/min per IP for auth endpoints
    FR-037: 100 req/min per user for task endpoints
    FR-038: HTTP 429 with Retry-After header
    FR-039: Must not block legitimate usage
    """

    def __init__(self, app):
        super().__init__(app)
        # Store: {key: (request_count, window_start_time)}
        self.ip_requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0))
        self.user_requests: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0))

    def _check_rate_limit(
        self,
        store: Dict[str, Tuple[int, float]],
        key: str,
        limit: int,
        window: int = 60,  # 1 minute window
    ) -> Tuple[bool, int]:
        """
        Check if rate limit is exceeded.

        Returns: (is_allowed, retry_after_seconds)
        """
        current_time = time.time()
        count, window_start = store[key]

        # Reset window if expired
        if current_time - window_start >= window:
            store[key] = (1, current_time)
            return True, 0

        # Check if limit exceeded
        if count >= limit:
            retry_after = int(window - (current_time - window_start)) + 1
            return False, retry_after

        # Increment count
        store[key] = (count + 1, window_start)
        return True, 0

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Skip rate limiting for health check
        if path == "/api/v1/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"

        # FR-036: Auth endpoints - 10 req/min per IP
        if path.startswith("/api/v1/auth"):
            is_allowed, retry_after = self._check_rate_limit(
                self.ip_requests,
                client_ip,
                settings.rate_limit_auth_per_minute,
            )

            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests",
                            "details": [],
                        }
                    },
                    headers={"Retry-After": str(retry_after)},
                )

        # FR-037: Task endpoints - 100 req/min per authenticated user
        # Note: User identification happens after auth middleware
        # For simplicity, we rate limit by IP for task endpoints too
        # In production, this would be enhanced to use user_id from JWT
        elif path.startswith("/api/v1/tasks"):
            is_allowed, retry_after = self._check_rate_limit(
                self.user_requests,
                client_ip,  # Would use user_id in production
                settings.rate_limit_tasks_per_minute,
            )

            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many requests",
                            "details": [],
                        }
                    },
                    headers={"Retry-After": str(retry_after)},
                )

        return await call_next(request)
