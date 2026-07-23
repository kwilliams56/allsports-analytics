"""Tests for the replaceable in-memory cache implementation."""

from app.services.cache import MemoryTTLCache


def test_cache_returns_value_before_expiry_and_evicts_after_expiry():
    now = [100.0]
    cache = MemoryTTLCache(clock=lambda: now[0])
    cache.set("key", {"value": 1}, ttl_seconds=10)

    assert cache.get("key") == {"value": 1}
    now[0] = 110.0
    assert cache.get("key") is None


def test_cache_ignores_non_positive_ttl():
    cache = MemoryTTLCache()
    cache.set("key", "value", ttl_seconds=0)
    assert cache.get("key") is None
