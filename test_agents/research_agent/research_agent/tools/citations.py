from __future__ import annotations

from typing import Any, Dict


def save_citation(memory, title: str, url: str) -> Dict[str, Any]:
    if not title or not url:
        return {"ok": False, "error": "title and url required"}
    memory.add_citation(title, url)
    return {"ok": True, "count": len(memory.citations)}
