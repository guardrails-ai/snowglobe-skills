from __future__ import annotations

from typing import Any, Dict


def refund(store, user_id: int, amount: float) -> Dict[str, Any]:
    if user_id not in store.users:
        return {"ok": False, "error": f"no user with id {user_id}"}
    if not isinstance(amount, (int, float)) or amount <= 0:
        return {"ok": False, "error": "amount must be positive"}
    record = {"user_id": user_id, "amount": float(amount)}
    store.refunds.append(record)
    return {"ok": True, "refund": record}
