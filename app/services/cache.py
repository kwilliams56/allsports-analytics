"""Small cache contract and a thread-safe in-memory TTL implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any, Callable


class Cache(ABC):
    """Minimal cache interface that can later be backed by Redis."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Return a cached value, or ``None`` when it is absent or expired."""

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        """Store a value for a positive number of seconds."""


@dataclass(frozen=True)
class _CacheEntry:
    value: Any
    expires_at: float


class MemoryTTLCache(Cache):
    """Process-local cache suitable for development and a single worker."""

    def __init__(self, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._entries: dict[str, _CacheEntry] = {}
        self._lock = RLock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None
            if entry.expires_at <= self._clock():
                self._entries.pop(key, None)
                return None
            return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        with self._lock:
            self._entries[key] = _CacheEntry(
                value=value,
                expires_at=self._clock() + ttl_seconds,
            )
