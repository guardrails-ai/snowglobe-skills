"""Notes the research agent collects across a session."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Memory:
    notes: List[str] = field(default_factory=list)
    citations: List[Dict[str, str]] = field(default_factory=list)
    outline: List[str] = field(default_factory=list)

    def add_note(self, note: str) -> None:
        self.notes.append(note)

    def add_citation(self, title: str, url: str) -> None:
        self.citations.append({"title": title, "url": url})

    def set_outline(self, items: List[str]) -> None:
        self.outline = list(items)
