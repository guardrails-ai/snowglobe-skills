from __future__ import annotations

from typing import Any, Dict


def summarize_text(llm, text: str, max_words: int = 30) -> Dict[str, Any]:
    if not isinstance(text, str) or not text.strip():
        return {"ok": False, "error": "text required"}
    return {"ok": True, "summary": llm.summarize(text, max_words)}
