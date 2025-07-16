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

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from configs.logging_config import logger

from ..auth import get_current_user
from ..database import ApiKey, AuthType, SystemUser, User, get_db

"""System authentication and API key management endpoints."""

router = APIRouter()


# Pydantic models
class SystemUserCreate(BaseModel):
    """System user creation model."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str | None = Field(None, max_length=50)
    last_name: str | None = Field(None, max_length=50)


class SystemUserLogin(BaseModel):
    """System user login model."""

    username: str
    password: str


class SystemUserResponse(BaseModel):
    """System user response model."""

    id: int
    username: str
    email: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreate(BaseModel):
    """API key creation model."""

    name: str = Field(..., min_length=1, max_length=100)
    expires_at: datetime | None = None


class ApiKeyResponse(BaseModel):
    """API key response model."""

    id: int
    name: str
    key_prefix: str
    is_active: bool
    last_used_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApiKeyCreatedResponse(BaseModel):
    """API key created response model with full key."""

    id: int
    name: str
    key_prefix: str
    full_key: str  # Only returned on creation
    is_active: bool
    expires_at: datetime | None
    created_at: datetime

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response model."""

    user: SystemUserResponse
    api_key: ApiKeyCreatedResponse


@router.post("/register", response_model=SystemUserResponse)
async def register_system_user(
    user_data: SystemUserCreate,
    db: Session = Depends(get_db),
):
    """Register a new system user."""
    # Check if username already exists
    existing_user = (
        db.query(SystemUser).filter(SystemUser.username == user_data.username).first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Check if email already exists
    existing_email = (
        db.query(SystemUser).filter(SystemUser.email == user_data.email).first()
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    # Create new system user
    system_user = SystemUser(
        username=user_data.username,
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )

    system_user.set_password(user_data.password)

    db.add(system_user)
    db.commit()
    db.refresh(system_user)

    logger.info(f"Created new system user: {user_data.username}")

    return system_user


@router.post("/login", response_model=LoginResponse)
async def login_system_user(
    login_data: SystemUserLogin,
    db: Session = Depends(get_db),
):
    """Login system user and return an API key."""
    # Find user by username
    system_user = (
        db.query(SystemUser).filter(SystemUser.username == login_data.username).first()
    )

    if not system_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    # Verify password
    if not system_user.verify_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not system_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User account is inactive"
        )

    # Create a new API key for this login
    full_key, key_hash = ApiKey.generate_key()

    api_key = ApiKey(
        system_user_id=system_user.id,
        name=f"Login key - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        key_hash=key_hash,
        key_prefix=full_key[:12],  # Store first 12 characters for display
        expires_at=datetime.utcnow() + timedelta(days=365),  # 1 year expiration
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    logger.info(f"System user logged in: {system_user.username}")

    return LoginResponse(
        user=SystemUserResponse(
            id=system_user.id,
            username=system_user.username,
            email=system_user.email,
            first_name=system_user.first_name,
            last_name=system_user.last_name,
            is_active=system_user.is_active,
            created_at=system_user.created_at,
            updated_at=system_user.updated_at,
        ),
        api_key=ApiKeyCreatedResponse(
            id=api_key.id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            full_key=full_key,
            is_active=api_key.is_active,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
        ),
    )


@router.get("/keys", response_model=list[ApiKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all API keys for the current system user."""
    if current_user.auth_type != AuthType.SYSTEM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system users can manage API keys",
        )

    api_keys = (
        db.query(ApiKey)
        .filter(ApiKey.system_user_id == current_user.system_user_id)
        .order_by(ApiKey.created_at.desc())
        .all()
    )

    return api_keys


@router.post("/keys", response_model=ApiKeyCreatedResponse)
async def create_api_key(
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new API key for the current system user."""
    if current_user.auth_type != AuthType.SYSTEM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system users can create API keys",
        )

    # Check if name already exists for this user
    existing_key = (
        db.query(ApiKey)
        .filter(
            ApiKey.system_user_id == current_user.system_user_id,
            ApiKey.name == key_data.name,
        )
        .first()
    )

    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key with this name already exists",
        )

    # Generate new API key
    full_key, key_hash = ApiKey.generate_key()

    api_key = ApiKey(
        system_user_id=current_user.system_user_id,
        name=key_data.name,
        key_hash=key_hash,
        key_prefix=full_key[:12],  # Store first 12 characters for display
        expires_at=key_data.expires_at,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    logger.info(f"Created new API key '{key_data.name}' for user {current_user.email}")

    return ApiKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key_prefix=api_key.key_prefix,
        full_key=full_key,
        is_active=api_key.is_active,
        expires_at=api_key.expires_at,
        created_at=api_key.created_at,
    )


@router.put("/keys/{key_id}", response_model=ApiKeyResponse)
async def update_api_key(
    key_id: int,
    key_data: ApiKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update an API key (name and expiration only)."""
    if current_user.auth_type != AuthType.SYSTEM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system users can update API keys",
        )

    # Find the API key
    api_key = (
        db.query(ApiKey)
        .filter(
            ApiKey.id == key_id, ApiKey.system_user_id == current_user.system_user_id
        )
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    # Check if new name conflicts with existing keys
    if key_data.name != api_key.name:
        existing_key = (
            db.query(ApiKey)
            .filter(
                ApiKey.system_user_id == current_user.system_user_id,
                ApiKey.name == key_data.name,
                ApiKey.id != key_id,
            )
            .first()
        )

        if existing_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key with this name already exists",
            )

    # Update the key
    api_key.name = key_data.name
    api_key.expires_at = key_data.expires_at
    api_key.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(api_key)

    logger.info(f"Updated API key '{api_key.name}' for user {current_user.email}")

    return api_key


@router.delete("/keys/{key_id}")
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Revoke (deactivate) an API key."""
    if current_user.auth_type != AuthType.SYSTEM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system users can revoke API keys",
        )

    # Find the API key
    api_key = (
        db.query(ApiKey)
        .filter(
            ApiKey.id == key_id, ApiKey.system_user_id == current_user.system_user_id
        )
        .first()
    )

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="API key not found"
        )

    # Deactivate the key
    api_key.is_active = False
    api_key.updated_at = datetime.utcnow()

    db.commit()

    logger.info(f"Revoked API key '{api_key.name}' for user {current_user.email}")

    return {"message": "API key revoked successfully"}


@router.get("/me", response_model=SystemUserResponse)
async def get_current_system_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current system user information."""
    if current_user.auth_type != AuthType.SYSTEM:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only system users can access this endpoint",
        )

    system_user = (
        db.query(SystemUser)
        .filter(SystemUser.id == current_user.system_user_id)
        .first()
    )

    if not system_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="System user not found"
        )

    return system_user
