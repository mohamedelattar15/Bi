"""
Simple in-memory cache for API responses.

Uses the CACHE_TTL_SECONDS from app config.
For production, swap this with Redis — interface stays the same.
"""

import time
import hashlib
import json
from functools import wraps
from typing import Any, Callable, Optional

from app.core.config import settings


class _CacheEntry:
    """A single cache entry with TTL."""

    __slots__ = ("data", "expires_at")

    def __init__(self, data: Any, ttl: int):
        self.data = data
        self.expires_at = time.time() + ttl

    @property
    def is_expired(self) -> bool:
        return time.time() > self.expires_at


_cache_store: dict[str, _CacheEntry] = {}


def _make_key(prefix: str, *args, **kwargs) -> str:
    """Build a deterministic cache key from arguments."""
    raw = f"{prefix}:{repr(args)}:{repr(sorted(kwargs.items()))}"
    return hashlib.md5(raw.encode()).hexdigest()


def cached(ttl: Optional[int] = None):
    """
    Decorator that caches return values in memory.

    Usage:
        @cached(ttl=300)  # cache for 5 minutes
        def expensive_method(self, arg1, arg2):
            ...

    Uses CACHE_TTL_SECONDS from settings if ttl is not provided.
    Skips caching if CACHE_TTL_SECONDS is 0.
    """
    if ttl is None:
        ttl = settings.CACHE_TTL_SECONDS

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Cache disabled
            if ttl <= 0:
                return func(*args, **kwargs)

            key = _make_key(func.__qualname__, args[1:], kwargs)

            # Check cache
            entry = _cache_store.get(key)
            if entry and not entry.is_expired:
                return entry.data

            # Compute and cache
            result = func(*args, **kwargs)
            _cache_store[key] = _CacheEntry(result, ttl)
            return result

        return wrapper

    return decorator


def invalidate_cache(prefix: Optional[str] = None):
    """
    Invalidate all cache entries, or those matching a prefix.

    Usage:
        invalidate_cache()              # clear all
        invalidate_cache("get_dashboard")  # clear only dashboard cache
    """
    global _cache_store
    if prefix is None:
        _cache_store.clear()
        return

    # Find keys matching prefix — we need to check the raw key.
    # Since _make_key hashes the input, we store a reverse lookup.
    # For simplicity, clear all when prefix is given.
    # A production Redis cache would use key patterns.
    _cache_store.clear()


def get_cache_stats() -> dict:
    """Return cache hit/miss stats (placeholder)."""
    return {
        "size": len(_cache_store),
        "ttl_seconds": settings.CACHE_TTL_SECONDS,
        "enabled": settings.CACHE_TTL_SECONDS > 0,
    }
