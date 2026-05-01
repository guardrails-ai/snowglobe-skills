"""Two tools: define and synonyms."""
from __future__ import annotations

from typing import Dict, Any, List

from .data import DEFINITIONS, SYNONYMS


def define(word: str) -> Dict[str, Any]:
    if not isinstance(word, str) or not word.strip():
        return {"ok": False, "word": word, "definition": None, "error": "word required"}
    key = word.strip().lower()
    if key not in DEFINITIONS:
        return {"ok": False, "word": key, "definition": None, "error": "not in dictionary"}
    return {"ok": True, "word": key, "definition": DEFINITIONS[key], "error": None}


def synonyms(word: str) -> Dict[str, Any]:
    if not isinstance(word, str) or not word.strip():
        return {"ok": False, "word": word, "synonyms": [], "error": "word required"}
    key = word.strip().lower()
    if key not in SYNONYMS:
        return {"ok": False, "word": key, "synonyms": [], "error": "no synonyms known"}
    return {"ok": True, "word": key, "synonyms": list(SYNONYMS[key]), "error": None}


TOOLS: Dict[str, Dict[str, Any]] = {
    "define": {"fn": define, "description": "Define a word. Args: word (str)."},
    "synonyms": {"fn": synonyms, "description": "List synonyms. Args: word (str)."},
}


def list_tools() -> List[str]:
    return list(TOOLS.keys())
