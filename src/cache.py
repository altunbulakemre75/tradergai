from __future__ import annotations

import time
from typing import Any

_store: dict[str, tuple[Any, float]] = {}
TTL = 300  # 5 dakika


def get(key: str) -> Any | None:
    entry = _store.get(key)
    if entry and time.time() - entry[1] < TTL:
        return entry[0]
    return None


def set(key: str, value: Any) -> None:
    _store[key] = (value, time.time())
