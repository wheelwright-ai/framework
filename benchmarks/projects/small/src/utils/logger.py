"""
Logging utilities for structured logging.
"""
import json
import sys
from datetime import datetime

class StructuredLogger:
    """Logger that outputs structured JSON logs."""

    def __init__(self, name, output=None):
        self.name = name
        self.output = output or sys.stdout

    def log(self, level, message, **context):
        """Log a structured message."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'logger': self.name,
            'message': message,
            **context
        }
        self.output.write(json.dumps(log_entry) + '\n')
        self.output.flush()

    def info(self, message, **context):
        """Log info level message."""
        self.log('INFO', message, **context)

    def error(self, message, **context):
        """Log error level message."""
        self.log('ERROR', message, **context)

    def debug(self, message, **context):
        """Log debug level message."""
        self.log('DEBUG', message, **context)
