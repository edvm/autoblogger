"""
Autoblogger - Generate content on demand using online data in real time.
Copyright (C) 2025  Emiliano Dalla Verde Marcozzi <edvm.inbox@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import re

from configs.config import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW
from .exceptions import RateLimitExceeded as AutobloggerRateLimitExceeded


# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        # Content Security Policy for API
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'none'; "
            "style-src 'none'; "
            "img-src 'none'; "
            "font-src 'none'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )

        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """Middleware to sanitize and validate input data."""

    # Potentially dangerous patterns
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # Script tags
        r"javascript:",  # JavaScript URLs
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>.*?</iframe>",  # Iframes
        r"<object[^>]*>.*?</object>",  # Objects
        r"<embed[^>]*>.*?</embed>",  # Embeds
    ]

    def __init__(self, app):
        super().__init__(app)
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.DANGEROUS_PATTERNS
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Request entity too large",
                    "error_code": "REQUEST_TOO_LARGE",
                },
            )

        # For JSON requests, validate the body
        if request.headers.get("content-type") == "application/json":
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8")

                    # Check for dangerous patterns
                    for pattern in self.compiled_patterns:
                        if pattern.search(body_str):
                            return JSONResponse(
                                status_code=400,
                                content={
                                    "error": "Invalid input detected",
                                    "error_code": "INVALID_INPUT",
                                },
                            )

                    # Recreate request with sanitized body
                    # Note: FastAPI will parse the JSON again, this is just validation
                    request._body = body
            except UnicodeDecodeError:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "Invalid encoding",
                        "error_code": "INVALID_ENCODING",
                    },
                )

        return await call_next(request)


def setup_rate_limiting(app):
    """Set up rate limiting for the FastAPI app."""

    # Add rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Custom rate limit exception handler
    @app.exception_handler(RateLimitExceeded)
    async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "error_code": "RATE_LIMIT_EXCEEDED",
                "detail": f"Rate limit exceeded: {exc.detail}",
                "retry_after": exc.retry_after,
            },
            headers={"Retry-After": str(exc.retry_after)},
        )


# Rate limiting decorators for different endpoint types
def standard_rate_limit():
    """Standard rate limit for most endpoints."""
    return limiter.limit(f"{RATE_LIMIT_REQUESTS}/{RATE_LIMIT_WINDOW}second")


def expensive_rate_limit():
    """More restrictive rate limit for expensive operations like blog generation."""
    return limiter.limit(
        f"{max(1, RATE_LIMIT_REQUESTS // 10)}/{RATE_LIMIT_WINDOW}second"
    )


def auth_rate_limit():
    """Rate limit for authentication endpoints."""
    return limiter.limit(
        f"{max(5, RATE_LIMIT_REQUESTS // 20)}/{RATE_LIMIT_WINDOW}second"
    )
