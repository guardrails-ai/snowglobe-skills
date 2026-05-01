from __future__ import annotations

from typing import Any, Dict


def list_todos(db, include_done: bool = True) -> Dict[str, Any]:
    todos = db.list(include_done=include_done)
    return {"ok": True, "todos": [t.to_dict() for t in todos]}
