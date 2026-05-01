from __future__ import annotations

from typing import Any, Dict


def update_preferences(store, user_id: int, key: str, value: str) -> Dict[str, Any]:
    user = store.users.get(user_id)
    if not user:
        return {"ok": False, "error": f"no user with id {user_id}"}
    if not key:
        return {"ok": False, "error": "key required"}
    user.preferences[key] = value
    return {"ok": True, "user_id": user_id, "preferences": dict(user.preferences)}
