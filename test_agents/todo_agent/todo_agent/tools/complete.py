from __future__ import annotations

from typing import Any, Dict


def complete_todo(db, todo_id: int) -> Dict[str, Any]:
    if not isinstance(todo_id, int):
        return {"ok": False, "error": "todo_id must be int"}
    if not db.complete(todo_id):
        return {"ok": False, "error": f"no todo with id {todo_id}"}
    return {"ok": True, "id": todo_id}
