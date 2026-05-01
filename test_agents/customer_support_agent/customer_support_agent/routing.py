"""Intent routing for support prompts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Intent:
    action: str
    user_id: Optional[int] = None
    ticket_id: Optional[int] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    text: Optional[str] = None
    amount: Optional[float] = None
    pref_key: Optional[str] = None
    pref_value: Optional[str] = None


_LOOKUP = re.compile(r"^\s*(?:lookup|find|get)\s+user\s+(\d+)\s*$", re.I)
_HISTORY = re.compile(r"^\s*history\s+(?:for\s+)?user\s+(\d+)\s*$", re.I)
_TICKET = re.compile(r"^\s*(?:create|open)\s+ticket\s+for\s+user\s+(\d+)\s*[:\-]\s*(.+?)(?:\s*//\s*(.+))?\s*$", re.I)
_ESC = re.compile(r"^\s*escalate\s+ticket\s+(\d+)\s*$", re.I)
_EMAIL = re.compile(r"^\s*email\s+user\s+(\d+)\s*[:\-]\s*(.+?)\s*//\s*(.+?)\s*$", re.I)
_REFUND = re.compile(r"^\s*refund\s+user\s+(\d+)\s+\$?(\d+(?:\.\d+)?)\s*$", re.I)
_PREF = re.compile(r"^\s*set\s+pref(?:erence)?\s+for\s+user\s+(\d+)\s+(\w+)\s*=\s*(.+?)\s*$", re.I)
_FAQ = re.compile(r"^\s*faq\s+(.+?)\s*$", re.I)


def parse(text: str) -> Intent:
    if (m := _LOOKUP.match(text)):
        return Intent("lookup", user_id=int(m.group(1)))
    if (m := _HISTORY.match(text)):
        return Intent("history", user_id=int(m.group(1)))
    if (m := _TICKET.match(text)):
        return Intent("ticket", user_id=int(m.group(1)),
                       subject=m.group(2).strip(), body=(m.group(3) or "").strip() or m.group(2).strip())
    if (m := _ESC.match(text)):
        return Intent("escalate", ticket_id=int(m.group(1)))
    if (m := _EMAIL.match(text)):
        return Intent("email", user_id=int(m.group(1)), subject=m.group(2).strip(), body=m.group(3).strip())
    if (m := _REFUND.match(text)):
        return Intent("refund", user_id=int(m.group(1)), amount=float(m.group(2)))
    if (m := _PREF.match(text)):
        return Intent("pref", user_id=int(m.group(1)), pref_key=m.group(2), pref_value=m.group(3).strip())
    if (m := _FAQ.match(text)):
        return Intent("faq", text=m.group(1))
    return Intent("noop")
