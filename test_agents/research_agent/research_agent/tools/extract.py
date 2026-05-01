from __future__ import annotations

from typing import Any, Dict

from .search import CORPUS


def extract_text(url: str) -> Dict[str, Any]:
    for doc in CORPUS:
        if doc["url"] == url:
            return {"ok": True, "text": doc["text"], "title": doc["title"]}
    return {"ok": False, "error": "url not in corpus"}
