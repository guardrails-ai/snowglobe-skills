from __future__ import annotations

from typing import Any, Dict


_RESULTS = {
    "python": [{"title": "Python.org", "url": "https://python.org"}],
    "ai":     [{"title": "AI overview", "url": "https://example.com/ai"}],
    "weather": [{"title": "Weather forecast", "url": "https://example.com/weather"}],
}


def web_search(query: str) -> Dict[str, Any]:
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "query required"}
    key = query.strip().lower().split()[0] if query.strip() else ""
    return {"ok": True, "results": _RESULTS.get(key, [{"title": "no results", "url": ""}])}
