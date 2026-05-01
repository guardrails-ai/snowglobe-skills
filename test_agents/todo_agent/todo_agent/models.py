"""Plain dataclasses for todo entries."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Todo:
    id: int
    text: str
    done: bool

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "text": self.text, "done": self.done}
