"""
Tests for cache utilities.
"""
import pytest
from src.utils.cache import SimpleCache, set_cache, get_cache, clear_cache


class TestSimpleCache:
    """Test caching functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cache = SimpleCache()

    def test_set_and_get(self):
        """Test setting and getting cache values."""
        self.cache.set("key", "value")
        assert self.cache.get("key") == "value"

    def test_get_nonexistent(self):
        """Test getting non-existent key."""
        assert self.cache.get("nonexistent") is None

    def test_delete(self):
        """Test deleting cache entry."""
        self.cache.set("key", "value")
        self.cache.delete("key")
        assert self.cache.get("key") is None

    def test_clear(self):
        """Test clearing all cache."""
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2")
        self.cache.clear()
        assert self.cache.get("key1") is None
        assert self.cache.get("key2") is None

    def test_cache_with_ttl(self):
        """Test cache with time-to-live."""
        # Set with very short TTL
        self.cache.set("key", "value", ttl_seconds=0)
        # Should expire immediately
        assert self.cache.get("key") is None

    def test_global_cache(self):
        """Test global cache functions."""
        clear_cache()
        set_cache("test_key", "test_value")
        assert get_cache("test_key") == "test_value"
