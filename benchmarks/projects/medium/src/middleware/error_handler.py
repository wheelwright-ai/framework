"""
Global error handling middleware.
Catches exceptions and returns appropriate error responses.
"""
import logging
from typing import Dict, Any
from datetime import datetime


logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int = 500, details: Dict[str, Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to response dictionary."""
        return {
            "error": self.message,
            "status_code": self.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "details": self.details,
        }


class ValidationError(APIException):
    """Raised when request validation fails."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, 400, details)


class NotFoundError(APIException):
    """Raised when resource is not found."""

    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, 404, details)


class UnauthorizedError(APIException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized", details: Dict[str, Any] = None):
        super().__init__(message, 401, details)


class PermissionDeniedError(APIException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Permission denied", details: Dict[str, Any] = None):
        super().__init__(message, 403, details)


def handle_exception(exc: Exception) -> Dict[str, Any]:
    """
    Convert exception to response dictionary.
    Logs unexpected exceptions.
    """
    if isinstance(exc, APIException):
        return exc.to_dict()

    # Log unexpected exceptions
    logger.exception(f"Unexpected error: {exc}")
    return {
        "error": "Internal server error",
        "status_code": 500,
        "timestamp": datetime.utcnow().isoformat(),
        "details": {},
    }
