"""
Response formatting utilities.
Standardizes API responses across all endpoints.
"""
from typing import Any, Dict, Optional, List
from datetime import datetime


class ResponseBuilder:
    """Builder for consistent API responses."""

    @staticmethod
    def success(
        message: str = "Success",
        data: Optional[Dict[str, Any]] = None,
        status_code: int = 200,
    ) -> Dict[str, Any]:
        """Build a successful response."""
        return {
            "success": True,
            "status_code": status_code,
            "message": message,
            "data": data or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def error(
        message: str = "Error",
        errors: Optional[List[str]] = None,
        status_code: int = 400,
    ) -> Dict[str, Any]:
        """Build an error response."""
        return {
            "success": False,
            "status_code": status_code,
            "message": message,
            "errors": errors or [],
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def paginated(
        items: List[Dict[str, Any]],
        total: int,
        page: int = 1,
        limit: int = 50,
        message: str = "Items retrieved",
    ) -> Dict[str, Any]:
        """Build a paginated response."""
        return {
            "success": True,
            "message": message,
            "data": items,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }


def success_response(
    message: str = "Success", data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Quick success response."""
    return ResponseBuilder.success(message, data)


def error_response(
    message: str = "Error", errors: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Quick error response."""
    return ResponseBuilder.error(message, errors)


def paginated_response(
    items: List[Dict[str, Any]], total: int, page: int = 1, limit: int = 50
) -> Dict[str, Any]:
    """Quick paginated response."""
    return ResponseBuilder.paginated(items, total, page, limit)
