"""In-memory note storage with monotonically increasing ids."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Note:
    id: int
    title: str
    body: str

    def to_dict(self) -> Dict[str, object]:
        return {"id": self.id, "title": self.title, "body": self.body}


@dataclass
class NoteStore:
    _notes: Dict[int, Note] = field(default_factory=dict)
    _next_id: int = 1

    def add(self, title: str, body: str) -> Note:
        note = Note(id=self._next_id, title=title, body=body)
        self._notes[note.id] = note
        self._next_id += 1
        return note

    def get(self, note_id: int) -> Optional[Note]:
        return self._notes.get(note_id)

    def search(self, query: str) -> List[Note]:
        q = query.strip().lower()
        if not q:
            return list(self._notes.values())
        return [
            n for n in self._notes.values()
            if q in n.title.lower() or q in n.body.lower()
        ]

    def all(self) -> List[Note]:
        return list(self._notes.values())
