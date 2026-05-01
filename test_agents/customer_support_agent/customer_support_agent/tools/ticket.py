from __future__ import annotations

from typing import Any, Dict


def create_ticket(store, user_id: int, subject: str, body: str, priority: str = "normal") -> Dict[str, Any]:
    if user_id not in store.users:
        return {"ok": False, "error": f"no user with id {user_id}"}
    if not subject:
        return {"ok": False, "error": "subject required"}
    if priority not in {"low", "normal", "high", "urgent"}:
        return {"ok": False, "error": "invalid priority"}
    t = store.create_ticket(user_id, subject, body or subject, priority)
    return {"ok": True, "ticket": t.model_dump()}
