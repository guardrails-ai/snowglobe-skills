from __future__ import annotations

from typing import Any, Dict, List

from ..data import FAQ


def faq_search(query: str) -> Dict[str, Any]:
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "query required"}
    q = query.strip().lower()
    hits: List[Dict[str, str]] = []
    for k, v in FAQ.items():
        if any(w in k for w in q.split()) or q in k:
            hits.append({"topic": k, "answer": v})
    return {"ok": True, "results": hits[:5]}
