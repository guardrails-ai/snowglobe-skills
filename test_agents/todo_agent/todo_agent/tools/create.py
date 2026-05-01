from __future__ import annotations

from typing import Any, Dict


def add_todo(db, text: str) -> Dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return {"ok": False, "error": "text required"}
    todo = db.add(text.strip())
    return {"ok": True, "todo": todo.to_dict()}
