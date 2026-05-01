"""Trivial in-process cache to avoid duplicate calls in a single turn."""
from __future__ import annotations

from typing import Any, Dict, Tuple


class Cache:
    def __init__(self) -> None:
        self._data: Dict[Tuple[str, str], Any] = {}

    def get(self, kind: str, key: str) -> Any:
        return self._data.get((kind, key.lower()))

    def set(self, kind: str, key: str, value: Any) -> None:
        self._data[(kind, key.lower())] = value

    def clear(self) -> None:
        self._data.clear()
