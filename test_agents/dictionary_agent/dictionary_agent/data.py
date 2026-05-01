"""Static dictionary data. Keeps the agent fully offline and deterministic."""
from __future__ import annotations

from typing import Dict, List


DEFINITIONS: Dict[str, str] = {
    "happy": "feeling or showing pleasure or contentment",
    "sad": "feeling or showing sorrow; unhappy",
    "code": "instructions for a computer expressed in a programming language",
    "agent": "an entity that perceives its environment and takes actions",
    "test": "a procedure intended to establish quality or reliability",
    "python": "a high-level, interpreted programming language",
    "tool": "a device or implement used to carry out a function",
    "venv": "a self-contained python environment",
}


SYNONYMS: Dict[str, List[str]] = {
    "happy": ["joyful", "content", "cheerful", "glad"],
    "sad": ["unhappy", "sorrowful", "downcast", "blue"],
    "code": ["program", "source", "script"],
    "agent": ["assistant", "actor", "operative"],
    "test": ["check", "examine", "verify"],
    "python": ["serpent", "snake"],
    "tool": ["instrument", "utility", "implement"],
    "venv": ["virtualenv", "environment"],
}
