"""Shared text utilities."""
from __future__ import annotations

import re
from typing import List


_WORD_RE = re.compile(r"\b[a-zA-Z][a-zA-Z\-']+\b")


def tokenize(text: str) -> List[str]:
    return [w.lower() for w in _WORD_RE.findall(text or "")]


def truncate(text: str, n: int = 80) -> str:
    text = (text or "").strip()
    return text if len(text) <= n else text[: n - 3] + "..."
