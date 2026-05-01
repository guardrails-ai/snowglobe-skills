from __future__ import annotations

from typing import Any, Dict, List

from ..utils import tokenize


CORPUS: List[Dict[str, str]] = [
    {"title": "intro to python", "url": "https://example.com/python", "text": "python is a high-level programming language used for many things."},
    {"title": "ai agents 101", "url": "https://example.com/agents", "text": "ai agents perceive their environment and take actions to achieve goals."},
    {"title": "test driven development", "url": "https://example.com/tdd", "text": "tdd is a discipline where tests are written before the implementation."},
    {"title": "venv guide", "url": "https://example.com/venv", "text": "a venv isolates python dependencies for one project from the system."},
]


def search(query: str) -> Dict[str, Any]:
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "query required"}
    q_tokens = set(tokenize(query))
    hits = []
    for doc in CORPUS:
        score = sum(1 for w in tokenize(doc["text"]) if w in q_tokens) + \
                sum(1 for w in tokenize(doc["title"]) if w in q_tokens)
        if score > 0:
            hits.append({"title": doc["title"], "url": doc["url"], "score": score})
    hits.sort(key=lambda h: -h["score"])
    return {"ok": True, "results": hits[:5]}
