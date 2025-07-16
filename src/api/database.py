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

import enum
import hashlib
import os
import secrets
from collections.abc import Generator
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

"""Database configuration and models for AutoBlogger API."""


class AuthType(enum.Enum):
    """Authentication type enumeration."""

    CLERK = "clerk"
    SYSTEM = "system"


# Database URL - SQLite for development
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./autoblogger.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class User(Base):
    """User model for storing user information."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth_type = Column(Enum(AuthType), default=AuthType.CLERK, nullable=False)
    clerk_user_id = Column(
        String, unique=True, index=True, nullable=True
    )  # Only for Clerk users
    system_user_id = Column(
        Integer, ForeignKey("system_users.id"), nullable=True
    )  # Only for system users
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    credits = Column(Integer, default=100)  # Starting credits
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    credit_transactions = relationship("CreditTransaction", back_populates="user")
    app_usages = relationship("AppUsage", back_populates="user")
    system_user = relationship("SystemUser", back_populates="user")


class CreditTransaction(Base):
    """Credit transaction model for tracking credit purchases and usage."""

    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(
        Integer, nullable=False
    )  # Positive for purchases, negative for usage
    transaction_type = Column(String, nullable=False)  # "purchase", "usage", "refund"
    description = Column(Text, nullable=True)
    reference_id = Column(
        String, nullable=True
    )  # For payment references or app usage IDs
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="credit_transactions")


class AppUsage(Base):
    """App usage model for tracking when users consume apps."""

    __tablename__ = "app_usages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    app_name = Column(String, nullable=False)  # e.g., "blogger"
    credits_consumed = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # "pending", "completed", "failed"
    input_data = Column(Text, nullable=True)  # JSON string of input parameters
    output_data = Column(Text, nullable=True)  # JSON string of output/results
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="app_usages")


class SystemUser(Base):
    """System user model for native authentication."""

    __tablename__ = "system_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    api_keys = relationship("ApiKey", back_populates="system_user")
    user = relationship("User", back_populates="system_user", uselist=False)

    def set_password(self, password: str):
        """Set password with hashing."""
        import bcrypt

        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """Verify password against hash."""
        import bcrypt

        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )


class ApiKey(Base):
    """API key model for system authentication."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    system_user_id = Column(Integer, ForeignKey("system_users.id"), nullable=False)
    name = Column(String, nullable=False)  # User-defined name for the key
    key_hash = Column(String, unique=True, index=True, nullable=False)  # Hashed API key
    key_prefix = Column(String, nullable=False)  # First 8 chars for identification
    is_active = Column(Boolean, default=True)
    last_used_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    system_user = relationship("SystemUser", back_populates="api_keys")

    @staticmethod
    def generate_key() -> tuple[str, str]:
        """Generate a new API key and return (full_key, key_hash)."""
        # Generate secure random key
        key = secrets.token_urlsafe(32)
        full_key = f"abk_live_{key}"

        # Create hash for storage
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()

        return full_key, key_hash

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key for storage/comparison."""
        return hashlib.sha256(key.encode()).hexdigest()

    def get_prefix(self) -> str:
        """Get the key prefix for display."""
        return self.key_prefix

    def is_expired(self) -> bool:
        """Check if the API key is expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def update_last_used(self):
        """Update the last used timestamp."""
        self.last_used_at = datetime.utcnow()


# Create tables
def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


# Dependency to get database session
def get_db() -> Generator[Any, Any, Session] | None:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
