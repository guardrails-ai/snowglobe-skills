"""Intent classifier for the personal assistant.

Returns a list of (action, args) tuples so a single prompt can fire multiple
tool calls (capped at 5).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple


_PATTERNS = [
    ("calendar_add",   re.compile(r"^\s*(?:schedule|add\s+event)\s+(.+?)(?:\s+on\s+(.+?))?\s*$", re.I)),
    ("calendar_list",  re.compile(r"^\s*(?:list|show)\s+(?:my\s+)?(?:calendar|events)\s*$", re.I)),
    ("email_send",     re.compile(r"^\s*email\s+(\S+)\s*[:\-]\s*(.+?)\s*//\s*(.+?)\s*$", re.I)),
    ("weather",        re.compile(r"^\s*weather\s+(?:in\s+)?(.+?)\s*$", re.I)),
    ("reminder_add",   re.compile(r"^\s*remind\s+me\s+to\s+(.+?)(?:\s+at\s+(.+?))?\s*$", re.I)),
    ("reminder_list",  re.compile(r"^\s*(?:list|show)\s+reminders\s*$", re.I)),
    ("search",         re.compile(r"^\s*(?:search|google|web)\s+(.+?)\s*$", re.I)),
    ("calculate",      re.compile(r"^\s*(?:calculate|compute|=)\s*(.+?)\s*$", re.I)),
    ("note_add",       re.compile(r"^\s*note\s*[:\-]?\s*(.+?)\s*$", re.I)),
    ("note_list",      re.compile(r"^\s*(?:list|show)\s+notes\s*$", re.I)),
    ("contact_add",    re.compile(r"^\s*add\s+contact\s+(\w+)\s+([\w@\.\+\-]+)\s*$", re.I)),
    ("contact_lookup", re.compile(r"^\s*(?:contact|find)\s+(\w+)\s*$", re.I)),
    ("news",           re.compile(r"^\s*news\s+(?:about\s+)?(.+?)\s*$", re.I)),
    ("translate",      re.compile(r"^\s*translate\s+['\"]?(.+?)['\"]?\s+to\s+(\w+)\s*$", re.I)),
]


def parse(text: str) -> List[Tuple[str, Dict[str, Any]]]:
    out: List[Tuple[str, Dict[str, Any]]] = []
    for action, pat in _PATTERNS:
        m = pat.match(text)
        if not m:
            continue
        if action == "calendar_add":
            out.append((action, {"title": m.group(1).strip(), "when": (m.group(2) or "tomorrow").strip()}))
        elif action == "calendar_list":
            out.append((action, {}))
        elif action == "email_send":
            out.append((action, {"to": m.group(1).strip(), "subject": m.group(2).strip(), "body": m.group(3).strip()}))
        elif action == "weather":
            out.append((action, {"city": m.group(1).strip()}))
        elif action == "reminder_add":
            out.append((action, {"text": m.group(1).strip(), "when": (m.group(2) or "later").strip()}))
        elif action == "reminder_list":
            out.append((action, {}))
        elif action == "search":
            out.append((action, {"query": m.group(1).strip()}))
        elif action == "calculate":
            out.append((action, {"expression": m.group(1).strip()}))
        elif action == "note_add":
            out.append((action, {"text": m.group(1).strip()}))
        elif action == "note_list":
            out.append((action, {}))
        elif action == "contact_add":
            out.append((action, {"name": m.group(1).strip(), "email": m.group(2).strip()}))
        elif action == "contact_lookup":
            out.append((action, {"name": m.group(1).strip()}))
        elif action == "news":
            out.append((action, {"topic": m.group(1).strip()}))
        elif action == "translate":
            out.append((action, {"text": m.group(1).strip(), "target_lang": m.group(2).strip()}))
        break
    return out
