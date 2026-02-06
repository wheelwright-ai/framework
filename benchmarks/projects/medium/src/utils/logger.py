"""
Structured logging utilities.
Provides consistent logging across the application.
"""
import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredLogger:
    """Structured logging with JSON output."""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.name = name

    def _format_message(
        self,
        message: str,
        level: str,
        **context
    ) -> Dict[str, Any]:
        """Format log message with context."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "logger": self.name,
            "message": message,
            "context": context,
        }

    def debug(self, message: str, **context):
        """Log debug message."""
        log_dict = self._format_message(message, "DEBUG", **context)
        self.logger.debug(json.dumps(log_dict))

    def info(self, message: str, **context):
        """Log info message."""
        log_dict = self._format_message(message, "INFO", **context)
        self.logger.info(json.dumps(log_dict))

    def warning(self, message: str, **context):
        """Log warning message."""
        log_dict = self._format_message(message, "WARNING", **context)
        self.logger.warning(json.dumps(log_dict))

    def error(self, message: str, **context):
        """Log error message."""
        log_dict = self._format_message(message, "ERROR", **context)
        self.logger.error(json.dumps(log_dict))

    def critical(self, message: str, **context):
        """Log critical message."""
        log_dict = self._format_message(message, "CRITICAL", **context)
        self.logger.critical(json.dumps(log_dict))


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
