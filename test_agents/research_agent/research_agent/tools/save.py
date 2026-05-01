from __future__ import annotations

from typing import Any, Dict


def save_note(memory, note: str) -> Dict[str, Any]:
    if not isinstance(note, str) or not note.strip():
        return {"ok": False, "error": "note required"}
    memory.add_note(note.strip())
    return {"ok": True, "count": len(memory.notes)}
