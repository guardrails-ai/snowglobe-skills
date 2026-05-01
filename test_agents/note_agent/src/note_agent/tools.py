"""Tool implementations bound to a NoteStore instance."""
from __future__ import annotations

from typing import Any, Dict, List

from .store import NoteStore


def make_tools(store: NoteStore) -> Dict[str, Dict[str, Any]]:
    def add_note(title: str, body: str = "") -> Dict[str, Any]:
        if not isinstance(title, str) or not title.strip():
            return {"ok": False, "error": "title required"}
        note = store.add(title.strip(), body or "")
        return {"ok": True, "note": note.to_dict()}

    def search_notes(query: str) -> Dict[str, Any]:
        if not isinstance(query, str):
            return {"ok": False, "error": "query must be a string"}
        results = store.search(query)
        return {"ok": True, "results": [n.to_dict() for n in results]}

    def list_notes() -> Dict[str, Any]:
        return {"ok": True, "results": [n.to_dict() for n in store.all()]}

    return {
        "add_note": {"fn": add_note, "description": "Save a note. Args: title, body."},
        "search_notes": {"fn": search_notes, "description": "Search notes. Args: query."},
        "list_notes": {"fn": list_notes, "description": "List all notes. No args."},
    }
