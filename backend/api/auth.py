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

"""Authentication utilities for Clerk integration."""

from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from configs.logging_config import logger
from .database import get_db, User
from configs.config import CLERK_SECRET_KEY
from clerk_backend_api import Clerk, AuthenticateRequestOptions

# Security scheme
security = HTTPBearer()


class ClerkUser:
    """Represents a Clerk user from JWT token."""

    def __init__(
        self,
        user_id: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> None:
        self.user_id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name


# Initialize Clerk client
clerk_client = Clerk(bearer_auth=CLERK_SECRET_KEY)


def is_signed_in(request) -> bool:
    request_state = clerk_client.authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=CLERK_SECRET_KEY, authorized_parties=["http://localhost:3000"]
        ),
    )
    print(request_state)
    return request_state.is_signed_in


async def get_clerk_user(request: Request) -> ClerkUser:
    """
    Authenticate a user via Clerk and return user information.

    This function validates the incoming request using the Clerk SDK,
    extracts user information from the authenticated session, and returns
    a ClerkUser object with the user's details.

    Args:
        request: The FastAPI Request object containing authentication headers

    Returns:
        ClerkUser: A ClerkUser object containing user_id, email, first_name, and last_name

    Raises:
        HTTPException: 401 if authentication fails for any reason:
            - Failed to authenticate request
            - User is not signed in
            - Missing payload in authenticated request
            - Missing 'sub' claim in token
            - User not found in Clerk
            - User email not found
    """
    try:
        request_state = clerk_client.authenticate_request(
            request,
            AuthenticateRequestOptions(
                secret_key=CLERK_SECRET_KEY,
                authorized_parties=["http://localhost:3000"],
            ),
        )
    except Exception as e:
        logger.error(f"Failed to authenticate request: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed"
        )

    if not request_state.is_signed_in:
        logger.error("User is not signed in")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not signed in"
        )

    if not request_state.payload:
        logger.error("Payload is not found in authenticated request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Payload is not found"
        )

    payload = request_state.payload
    user_id = payload.get("sub")
    if not user_id:
        logger.error("Token missing 'sub' claim, cannot find user id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' claim, cannot find user id",
        )

    try:
        user_response = clerk_client.users.get(user_id=user_id)
    except Exception as e:
        logger.error(f"Failed to get user from Clerk: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Failed to get user information",
        )

    if not user_response:
        logger.error(f"User not found for user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    email = None
    if user_response.email_addresses:
        primary_email = next(
            (
                email
                for email in user_response.email_addresses
                if email.id == user_response.primary_email_address_id
            ),
            user_response.email_addresses[0],
        )
        email = primary_email.email_address

    if not email:
        logger.error(f"User email not found for user_id: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User email not found"
        )

    # Handle OptionalNullable types from Clerk SDK
    first_name = None if not user_response.first_name else str(user_response.first_name)
    last_name = None if not user_response.last_name else str(user_response.last_name)

    return ClerkUser(
        user_id=user_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
    )


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""

    clerk_user = await get_clerk_user(request)

    # Get or create user in our database
    db_user = db.query(User).filter(User.clerk_user_id == clerk_user.user_id).first()

    if not db_user:
        # Create new user
        db_user = User(
            clerk_user_id=clerk_user.user_id,
            email=clerk_user.email,
            first_name=clerk_user.first_name,
            last_name=clerk_user.last_name,
            credits=100,  # Starting credits
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Created new user: {clerk_user.email}")

    if db_user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    return db_user


# Optional dependency for endpoints that don't require authentication
# TODO: Remove this dependency
async def get_current_user_optional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None."""
    if not credentials:
        return None

    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None
