from __future__ import annotations

from typing import Any, Dict


def reminder_add(memory, text: str, when: str) -> Dict[str, Any]:
    if not text:
        return {"ok": False, "error": "text required"}
    r = {"id": memory.next_reminder_id, "text": text, "when": when}
    memory.reminders.append(r)
    memory.next_reminder_id += 1
    return {"ok": True, "reminder": r}


def reminder_list(memory) -> Dict[str, Any]:
    return {"ok": True, "reminders": list(memory.reminders)}
