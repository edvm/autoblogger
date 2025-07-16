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

from abc import ABC, abstractmethod

from clerk_backend_api import AuthenticateRequestOptions, Clerk
from fastapi import HTTPException, Request, status
from sqlalchemy.orm import Session

from configs.config import CLERK_SECRET_KEY
from configs.logging_config import logger

from .database import ApiKey, AuthType, User

"""Authentication strategy pattern for multiple auth methods."""


class AuthResult:
    """Result of authentication attempt."""

    def __init__(self, user: User, auth_type: AuthType, metadata: dict = None):
        self.user = user
        self.auth_type = auth_type
        self.metadata = metadata or {}


class AuthStrategy(ABC):
    """Abstract base class for authentication strategies."""

    @abstractmethod
    async def authenticate(self, request: Request, db: Session) -> AuthResult:
        """Authenticate a request and return user information."""
        pass

    @abstractmethod
    def get_auth_type(self) -> AuthType:
        """Get the authentication type this strategy handles."""
        pass


class ClerkAuthStrategy(AuthStrategy):
    """Clerk-based authentication strategy."""

    def __init__(self):
        self.clerk_client = Clerk(bearer_auth=CLERK_SECRET_KEY)

    def get_auth_type(self) -> AuthType:
        return AuthType.CLERK

    async def authenticate(self, request: Request, db: Session) -> AuthResult:
        """Authenticate using Clerk JWT token."""
        try:
            request_state = self.clerk_client.authenticate_request(
                request,
                AuthenticateRequestOptions(
                    secret_key=CLERK_SECRET_KEY,
                    authorized_parties=["http://localhost:3000"],
                ),
            )
        except Exception as e:
            logger.error(f"Failed to authenticate Clerk request: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Clerk authentication failed",
            ) from e

        if not request_state.is_signed_in:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not signed in"
            )

        if not request_state.payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Payload is not found"
            )

        payload = request_state.payload
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing 'sub' claim, cannot find user id",
            )

        try:
            user_response = self.clerk_client.users.get(user_id=user_id)
        except Exception as e:
            logger.error(f"Failed to get user from Clerk: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to get user information",
            ) from e

        if not user_response:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        # Extract email
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
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User email not found"
            )

        # Get or create user in our database
        db_user = db.query(User).filter(User.clerk_user_id == user_id).first()

        if not db_user:
            # Create new Clerk user
            first_name = (
                None if not user_response.first_name else str(user_response.first_name)
            )
            last_name = (
                None if not user_response.last_name else str(user_response.last_name)
            )

            db_user = User(
                auth_type=AuthType.CLERK,
                clerk_user_id=user_id,
                email=email,
                first_name=first_name,
                last_name=last_name,
                credits=100,  # Starting credits
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"Created new Clerk user: {email}")

        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        return AuthResult(
            user=db_user, auth_type=AuthType.CLERK, metadata={"clerk_user_id": user_id}
        )


class ApiKeyAuthStrategy(AuthStrategy):
    """API key-based authentication strategy."""

    def get_auth_type(self) -> AuthType:
        return AuthType.SYSTEM

    async def authenticate(self, request: Request, db: Session) -> AuthResult:
        """Authenticate using API key."""
        # Get API key from X-API-Key header
        api_key = request.headers.get("X-API-Key")

        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="X-API-Key header is required",
            )

        if not api_key.startswith("abk_live_"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key format",
            )

        # Hash the key for database lookup
        key_hash = ApiKey.hash_key(api_key)

        # Find the API key in database
        api_key_obj = (
            db.query(ApiKey)
            .filter(ApiKey.key_hash == key_hash, ApiKey.is_active == True)
            .first()
        )

        if not api_key_obj:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
            )

        # Check if key is expired
        if api_key_obj.is_expired():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="API key has expired"
            )

        # Get the system user
        system_user = api_key_obj.system_user
        if not system_user or not system_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive",
            )

        # Get or create the User record
        db_user = db.query(User).filter(User.system_user_id == system_user.id).first()

        if not db_user:
            # Create new system user record
            db_user = User(
                auth_type=AuthType.SYSTEM,
                system_user_id=system_user.id,
                email=system_user.email,
                username=system_user.username,
                first_name=system_user.first_name,
                last_name=system_user.last_name,
                credits=100,  # Starting credits
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"Created new system user: {system_user.email}")

        if not db_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is inactive",
            )

        # Update last used timestamp
        api_key_obj.update_last_used()
        db.commit()

        return AuthResult(
            user=db_user,
            auth_type=AuthType.SYSTEM,
            metadata={
                "api_key_id": api_key_obj.id,
                "api_key_name": api_key_obj.name,
                "system_user_id": system_user.id,
            },
        )


class AuthStrategyManager:
    """Manager for handling different authentication strategies."""

    def __init__(self):
        self.strategies = {
            AuthType.CLERK: ClerkAuthStrategy(),
            AuthType.SYSTEM: ApiKeyAuthStrategy(),
        }

    async def authenticate(self, request: Request, db: Session) -> AuthResult:
        """Try to authenticate using available strategies."""
        # Try API key first (check for X-API-Key header)
        if request.headers.get("X-API-Key"):
            return await self.strategies[AuthType.SYSTEM].authenticate(request, db)

        # Try Clerk authentication (check for Authorization header)
        if request.headers.get("Authorization"):
            return await self.strategies[AuthType.CLERK].authenticate(request, db)

        # No authentication method found
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication method provided. Use 'X-API-Key' or 'Authorization' header.",
        )

    def get_strategy(self, auth_type: AuthType) -> AuthStrategy:
        """Get a specific authentication strategy."""
        return self.strategies.get(auth_type)
