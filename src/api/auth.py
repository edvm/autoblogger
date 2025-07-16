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

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from configs.logging_config import logger

from .auth_strategies import AuthStrategyManager
from .database import User, get_db

"""Authentication utilities supporting multiple auth methods."""

# Security scheme
security = HTTPBearer()

# Initialize authentication strategy manager
auth_manager = AuthStrategyManager()


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user using any supported authentication method."""

    auth_result = await auth_manager.authenticate(request, db)

    logger.info(
        f"User authenticated via {auth_result.auth_type.value}: {auth_result.user.email}"
    )

    return auth_result.user


# Optional dependency for endpoints that don't require authentication
async def get_current_user_optional(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> User | None:
    """Get current user if authenticated, otherwise return None."""
    # Check if any authentication method is present
    if not credentials and not request.headers.get("X-API-Key"):
        return None

    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None
