from __future__ import annotations

from typing import Any, Dict

from dateutil import parser as dtparser


def calendar_add(memory, title: str, when: str) -> Dict[str, Any]:
    if not title:
        return {"ok": False, "error": "title required"}
    try:
        when_dt = dtparser.parse(when, fuzzy=True) if when else None
    except (ValueError, TypeError):
        when_dt = None
    event = {
        "id": memory.next_event_id,
        "title": title,
        "when": when_dt.isoformat() if when_dt else when,
    }
    memory.events.append(event)
    memory.next_event_id += 1
    return {"ok": True, "event": event}


def calendar_list(memory) -> Dict[str, Any]:
    return {"ok": True, "events": list(memory.events)}
