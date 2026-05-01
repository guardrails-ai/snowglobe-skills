from __future__ import annotations

from typing import Any, Dict


_DATA = {
    "san francisco": {"temp_f": 62, "condition": "foggy"},
    "new york":      {"temp_f": 71, "condition": "sunny"},
    "london":        {"temp_f": 55, "condition": "rainy"},
    "tokyo":         {"temp_f": 68, "condition": "clear"},
}


def weather(city: str) -> Dict[str, Any]:
    if not city:
        return {"ok": False, "error": "city required"}
    data = _DATA.get(city.strip().lower())
    if not data:
        return {"ok": False, "error": "unknown city"}
    return {"ok": True, "city": city, **data}
