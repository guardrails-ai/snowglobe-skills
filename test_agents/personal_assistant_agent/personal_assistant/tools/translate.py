from __future__ import annotations

from typing import Any, Dict


_PHRASES = {
    ("hello", "spanish"): "hola",
    ("hello", "french"):  "bonjour",
    ("hello", "german"):  "hallo",
    ("thank you", "spanish"): "gracias",
    ("thank you", "french"):  "merci",
    ("yes", "spanish"): "si",
    ("no",  "spanish"): "no",
}


def translate(text: str, target_lang: str) -> Dict[str, Any]:
    if not text or not target_lang:
        return {"ok": False, "error": "text and target_lang required"}
    key = (text.strip().lower(), target_lang.strip().lower())
    return {"ok": True, "text": text, "target_lang": target_lang,
            "translation": _PHRASES.get(key, f"[{target_lang}] {text}")}
