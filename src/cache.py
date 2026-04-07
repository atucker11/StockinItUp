import asyncio
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: float


class AsyncTTLCache:
    def __init__(self) -> None:
        self._data: dict[str, CacheEntry] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    async def get_or_set(self, key: str, ttl: int, factory: Callable[[], Awaitable[T]]) -> T:
        now = time.time()
        entry = self._data.get(key)
        if entry and entry.expires_at > now:
            return entry.value
        lock = self._locks.setdefault(key, asyncio.Lock())
        async with lock:
            now = time.time()
            entry = self._data.get(key)
            if entry and entry.expires_at > now:
                return entry.value
            value = await factory()
            self._data[key] = CacheEntry(value=value, expires_at=now + ttl)
            return value

    def clear(self) -> None:
        self._data.clear()
