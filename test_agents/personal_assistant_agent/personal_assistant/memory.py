"""Persistent in-process state for the assistant."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Memory:
    events: List[Dict[str, Any]] = field(default_factory=list)
    sent_emails: List[Dict[str, str]] = field(default_factory=list)
    reminders: List[Dict[str, Any]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    contacts: Dict[str, Dict[str, str]] = field(default_factory=dict)
    next_event_id: int = 1
    next_reminder_id: int = 1
