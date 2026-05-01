"""Lightweight intent parser for the note agent."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Intent:
    action: str  # "add" | "search" | "list" | "noop"
    title: Optional[str] = None
    body: Optional[str] = None
    query: Optional[str] = None


_ADD_RE = re.compile(
    r"^\s*(?:add|create|save|note)\s+(?:a\s+note\s+)?(?:titled\s+)?[\"']?([^\"':]+?)[\"']?(?:\s*[:\-]\s*(.+))?\s*$",
    re.I,
)
_SEARCH_RE = re.compile(r"^\s*(?:search|find)(?:\s+for)?\s+(.+?)\s*$", re.I)
_LIST_RE = re.compile(r"^\s*(?:list|show|all)\s*(?:notes?)?\s*$", re.I)


def parse(text: str) -> Intent:
    if not text:
        return Intent(action="noop")
    if _LIST_RE.match(text):
        return Intent(action="list")
    m = _SEARCH_RE.match(text)
    if m:
        return Intent(action="search", query=m.group(1).strip())
    m = _ADD_RE.match(text)
    if m:
        title = m.group(1).strip()
        body = (m.group(2) or "").strip()
        return Intent(action="add", title=title, body=body)
    return Intent(action="noop")
