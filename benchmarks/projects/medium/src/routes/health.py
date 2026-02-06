"""
Health check and status endpoints.
Public endpoints - no authentication required.
"""
from datetime import datetime


class HealthCheckRouter:
    """Health check endpoints."""

    @staticmethod
    def health_check() -> dict:
        """GET /health - Basic health check."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }

    @staticmethod
    def status() -> dict:
        """GET /status - Detailed status information."""
        return {
            "status": "operational",
            "services": {
                "api": "healthy",
                "database": "healthy",
                "cache": "healthy",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def metrics() -> dict:
        """GET /metrics - System metrics."""
        return {
            "requests_total": 0,
            "requests_per_minute": 0,
            "error_rate": 0.0,
            "average_response_time_ms": 0.0,
            "timestamp": datetime.utcnow().isoformat(),
        }
