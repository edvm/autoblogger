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

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import configuration and middleware
from configs.config import ALLOWED_ORIGINS
from core.exceptions import AutobloggerException, map_exception_to_http
from core.middleware import (
    InputSanitizationMiddleware,
    SecurityHeadersMiddleware,
    setup_rate_limiting,
)

# Import routers
from .routers import apps, credits, system_auth, users

"""Main FastAPI application for AutoBlogger API."""

# Initialize FastAPI app
app = FastAPI(
    title="AutoBlogger API",
    description="REST API for AutoBlogger - AI-powered blog generation with multi-agent workflow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizationMiddleware)

# Configure CORS with environment-specific settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
)

# Set up rate limiting
setup_rate_limiting(app)


# Global exception handler for custom exceptions
@app.exception_handler(AutobloggerException)
async def autoblogger_exception_handler(request: Request, exc: AutobloggerException):
    """Handle custom Autoblogger exceptions."""
    http_exc = map_exception_to_http(exc)
    return JSONResponse(
        status_code=http_exc.status_code,
        content={
            "error": http_exc.detail,
            "error_code": http_exc.error_code,
            "details": exc.details,
        },
    )


# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(apps.router, prefix="/api/v1/apps", tags=["apps"])
app.include_router(credits.router, prefix="/api/v1/credits", tags=["credits"])
app.include_router(system_auth.router, prefix="/api/v1/auth", tags=["authentication"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "AutoBlogger API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {"status": "healthy", "service": "AutoBlogger API", "version": "1.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        "api.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
