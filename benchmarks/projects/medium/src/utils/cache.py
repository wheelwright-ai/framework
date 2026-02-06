"""
Simple in-memory caching utility.
Used for product listings, user data, and session information.
"""
from typing import Any, Optional, Dict
from datetime import datetime, timedelta


class CacheEntry:
    """A single cache entry with expiration."""

    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = datetime.utcnow()
        self.ttl_seconds = ttl_seconds

    def is_expired(self) -> bool:
        """Check if this cache entry has expired."""
        return (
            datetime.utcnow() - self.created_at
        ) > timedelta(seconds=self.ttl_seconds)


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self):
        self.data: Dict[str, CacheEntry] = {}

    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set a value in the cache."""
        self.data[key] = CacheEntry(value, ttl_seconds)

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if key not in self.data:
            return None

        entry = self.data[key]
        if entry.is_expired():
            del self.data[key]
            return None

        return entry.value

    def delete(self, key: str):
        """Delete a key from the cache."""
        if key in self.data:
            del self.data[key]

    def clear(self):
        """Clear all cache entries."""
        self.data.clear()

    def cleanup_expired(self):
        """Remove all expired entries from cache."""
        expired_keys = [
            key for key, entry in self.data.items() if entry.is_expired()
        ]
        for key in expired_keys:
            del self.data[key]


# Global cache instance
_cache = SimpleCache()


def set_cache(key: str, value: Any, ttl_seconds: int = 300):
    """Set a value in the global cache."""
    _cache.set(key, value, ttl_seconds)


def get_cache(key: str) -> Optional[Any]:
    """Get a value from the global cache."""
    return _cache.get(key)


def clear_cache():
    """Clear the global cache."""
    _cache.clear()
