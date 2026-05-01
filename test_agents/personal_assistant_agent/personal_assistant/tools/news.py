from __future__ import annotations

from typing import Any, Dict


def news_top(topic: str) -> Dict[str, Any]:
    if not topic:
        return {"ok": False, "error": "topic required"}
    return {"ok": True, "topic": topic,
            "headlines": [f"breaking: {topic} update", f"analysis: deep dive into {topic}"]}
