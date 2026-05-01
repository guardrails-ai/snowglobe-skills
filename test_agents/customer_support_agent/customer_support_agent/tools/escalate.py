from __future__ import annotations

from typing import Any, Dict


def escalate(store, ticket_id: int) -> Dict[str, Any]:
    t = store.tickets.get(ticket_id)
    if not t:
        return {"ok": False, "error": f"no ticket {ticket_id}"}
    t.status = "escalated"
    t.priority = "urgent"
    return {"ok": True, "ticket": t.model_dump()}
