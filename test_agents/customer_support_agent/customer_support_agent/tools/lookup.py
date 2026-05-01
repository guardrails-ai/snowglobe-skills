from __future__ import annotations

from typing import Any, Dict


def lookup_user(store, user_id: int) -> Dict[str, Any]:
    user = store.users.get(user_id)
    if not user:
        return {"ok": False, "error": f"no user with id {user_id}"}
    return {"ok": True, "user": user.model_dump()}
