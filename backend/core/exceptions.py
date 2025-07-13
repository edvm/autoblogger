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

from typing import Any

from fastapi import HTTPException, status


class AutobloggerException(Exception):
    """Base exception for all Autoblogger-specific errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(AutobloggerException):
    """Raised when input validation fails."""

    pass


class AuthenticationError(AutobloggerException):
    """Raised when authentication fails."""

    pass


class AuthorizationError(AutobloggerException):
    """Raised when user lacks required permissions."""

    pass


class RateLimitExceeded(AutobloggerException):
    """Raised when rate limit is exceeded."""

    pass


class InsufficientCreditsError(AutobloggerException):
    """Raised when user has insufficient credits."""

    pass


class LLMServiceError(AutobloggerException):
    """Raised when LLM service encounters an error."""

    pass


class SearchServiceError(AutobloggerException):
    """Raised when search service encounters an error."""

    pass


class WorkflowError(AutobloggerException):
    """Raised when workflow processing fails."""

    pass


class ConfigurationError(AutobloggerException):
    """Raised when configuration is invalid or missing."""

    pass


# HTTP Exception mappings
class AutobloggerHTTPException(HTTPException):
    """Custom HTTP exception for API responses."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, str] | None = None,
        error_code: str | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


def map_exception_to_http(exc: AutobloggerException) -> AutobloggerHTTPException:
    """Map internal exceptions to HTTP exceptions with appropriate status codes."""

    error_mappings = {
        ValidationError: (status.HTTP_400_BAD_REQUEST, "VALIDATION_ERROR"),
        AuthenticationError: (status.HTTP_401_UNAUTHORIZED, "AUTHENTICATION_ERROR"),
        AuthorizationError: (status.HTTP_403_FORBIDDEN, "AUTHORIZATION_ERROR"),
        RateLimitExceeded: (status.HTTP_429_TOO_MANY_REQUESTS, "RATE_LIMIT_EXCEEDED"),
        InsufficientCreditsError: (
            status.HTTP_402_PAYMENT_REQUIRED,
            "INSUFFICIENT_CREDITS",
        ),
        LLMServiceError: (status.HTTP_502_BAD_GATEWAY, "LLM_SERVICE_ERROR"),
        SearchServiceError: (status.HTTP_502_BAD_GATEWAY, "SEARCH_SERVICE_ERROR"),
        WorkflowError: (status.HTTP_500_INTERNAL_SERVER_ERROR, "WORKFLOW_ERROR"),
        ConfigurationError: (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "CONFIGURATION_ERROR",
        ),
    }

    status_code, error_code = error_mappings.get(
        type(exc), (status.HTTP_500_INTERNAL_SERVER_ERROR, "INTERNAL_ERROR")
    )

    return AutobloggerHTTPException(
        status_code=status_code, detail=exc.message, error_code=error_code
    )


# Error response constants
class ErrorConstants:
    """Professional error constants and messages."""

    LLM_NO_RESPONSE = "LLM_NO_RESPONSE"
    LLM_EMPTY_RESPONSE = "LLM_EMPTY_RESPONSE"
    LLM_SERVICE_UNAVAILABLE = "LLM_SERVICE_UNAVAILABLE"
    SEARCH_SERVICE_UNAVAILABLE = "SEARCH_SERVICE_UNAVAILABLE"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"
    INVALID_INPUT = "INVALID_INPUT"
    RATE_LIMITED = "RATE_LIMITED"
    INSUFFICIENT_CREDITS = "INSUFFICIENT_CREDITS"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    CONFIGURATION_MISSING = "CONFIGURATION_MISSING"
