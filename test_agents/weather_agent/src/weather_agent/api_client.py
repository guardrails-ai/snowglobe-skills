"""Weather API client. Pluggable backend so tests don't hit the network."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol


class Backend(Protocol):
    def get_json(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]: ...


class MockWeatherBackend:
    """Deterministic, offline backend used in tests."""

    DATA: Dict[str, Dict[str, Any]] = {
        "san francisco": {"temp_f": 62, "condition": "foggy", "humidity": 78, "wind_mph": 12},
        "new york":      {"temp_f": 71, "condition": "sunny", "humidity": 55, "wind_mph": 7},
        "london":        {"temp_f": 55, "condition": "rainy", "humidity": 88, "wind_mph": 14},
        "tokyo":         {"temp_f": 68, "condition": "clear", "humidity": 60, "wind_mph": 5},
    }

    def get_json(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        city = (params.get("city") or "").strip().lower()
        if path == "/current":
            if city not in self.DATA:
                return {"error": "unknown city"}
            return {"city": city, **self.DATA[city]}
        if path == "/forecast":
            if city not in self.DATA:
                return {"error": "unknown city"}
            base = self.DATA[city]["temp_f"]
            return {
                "city": city,
                "days": [{"day": i + 1, "high_f": base + i, "low_f": base - 5 + i} for i in range(5)],
            }
        if path == "/alerts":
            if city == "london":
                return {"city": city, "alerts": [{"severity": "moderate", "title": "wind advisory"}]}
            return {"city": city, "alerts": []}
        return {"error": "unknown path"}


class WeatherClient:
    def __init__(self, backend: Optional[Backend] = None) -> None:
        self.backend: Backend = backend or MockWeatherBackend()

    def current(self, city: str) -> Dict[str, Any]:
        return self.backend.get_json("/current", {"city": city})

    def forecast(self, city: str) -> Dict[str, Any]:
        return self.backend.get_json("/forecast", {"city": city})

    def alerts(self, city: str) -> Dict[str, Any]:
        return self.backend.get_json("/alerts", {"city": city})
