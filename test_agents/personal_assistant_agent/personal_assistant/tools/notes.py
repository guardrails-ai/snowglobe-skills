from __future__ import annotations

from typing import Any, Dict


def note_add(memory, text: str) -> Dict[str, Any]:
    if not text:
        return {"ok": False, "error": "text required"}
    memory.notes.append(text)
    return {"ok": True, "count": len(memory.notes)}


def note_list(memory) -> Dict[str, Any]:
    return {"ok": True, "notes": list(memory.notes)}
