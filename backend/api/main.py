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

"""Main FastAPI application for AutoBlogger API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import routers
from .routers import users, apps, credits

# Initialize FastAPI app
app = FastAPI(
    title="AutoBlogger API",
    description="REST API for AutoBlogger - AI-powered blog generation with multi-agent workflow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(apps.router, prefix="/api/v1/apps", tags=["apps"])
app.include_router(credits.router, prefix="/api/v1/credits", tags=["credits"])


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
