"""
Date/time utility functions.
"""
from datetime import datetime, timedelta
from typing import Optional


def get_current_timestamp() -> str:
    """Get current ISO format timestamp."""
    return datetime.utcnow().isoformat()


def add_hours(hours: int = 1) -> datetime:
    """Get datetime X hours from now."""
    return datetime.utcnow() + timedelta(hours=hours)


def add_days(days: int = 1) -> datetime:
    """Get datetime X days from now."""
    return datetime.utcnow() + timedelta(days=days)


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object to string."""
    return dt.strftime(format_str)


def parse_iso_timestamp(iso_string: str) -> Optional[datetime]:
    """Parse ISO format timestamp string."""
    try:
        return datetime.fromisoformat(iso_string)
    except (ValueError, TypeError):
        return None


def is_past(dt: datetime) -> bool:
    """Check if a datetime is in the past."""
    return dt < datetime.utcnow()


def is_future(dt: datetime) -> bool:
    """Check if a datetime is in the future."""
    return dt > datetime.utcnow()


def days_until(dt: datetime) -> int:
    """Calculate days until a datetime."""
    delta = dt - datetime.utcnow()
    return delta.days


def seconds_until(dt: datetime) -> int:
    """Calculate seconds until a datetime."""
    delta = dt - datetime.utcnow()
    return int(delta.total_seconds())
