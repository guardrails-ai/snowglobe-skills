from __future__ import annotations

from typing import Any, Dict


def build_outline(llm, memory, topic: str, n: int = 3) -> Dict[str, Any]:
    if not isinstance(topic, str) or not topic.strip():
        return {"ok": False, "error": "topic required"}
    items = llm.outline(topic, n)
    memory.set_outline(items)
    return {"ok": True, "outline": items}
