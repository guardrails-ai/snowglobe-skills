"""Five tools wired to a WeatherClient: current, forecast, alerts, compare, summarize."""
from __future__ import annotations

from typing import Any, Dict, List

from .api_client import WeatherClient
from .cache import Cache


def make_tools(client: WeatherClient, cache: Cache):
    def get_current(city: str) -> Dict[str, Any]:
        if not city:
            return {"ok": False, "error": "city required"}
        cached = cache.get("current", city)
        if cached:
            return {"ok": True, "data": cached, "cached": True}
        data = client.current(city)
        if data.get("error"):
            return {"ok": False, "error": data["error"]}
        cache.set("current", city, data)
        return {"ok": True, "data": data, "cached": False}

    def get_forecast(city: str) -> Dict[str, Any]:
        if not city:
            return {"ok": False, "error": "city required"}
        data = client.forecast(city)
        if data.get("error"):
            return {"ok": False, "error": data["error"]}
        return {"ok": True, "data": data}

    def get_alerts(city: str) -> Dict[str, Any]:
        if not city:
            return {"ok": False, "error": "city required"}
        data = client.alerts(city)
        if data.get("error"):
            return {"ok": False, "error": data["error"]}
        return {"ok": True, "data": data}

    def compare_cities(city_a: str, city_b: str) -> Dict[str, Any]:
        a = client.current(city_a)
        b = client.current(city_b)
        if a.get("error") or b.get("error"):
            return {"ok": False, "error": "one or both cities unknown"}
        warmer = a["city"] if a["temp_f"] >= b["temp_f"] else b["city"]
        return {"ok": True, "warmer": warmer, "a": a, "b": b}

    def summarize_week(city: str) -> Dict[str, Any]:
        data = client.forecast(city)
        if data.get("error"):
            return {"ok": False, "error": data["error"]}
        highs = [d["high_f"] for d in data["days"]]
        return {
            "ok": True,
            "city": city,
            "avg_high": sum(highs) / len(highs),
            "max_high": max(highs),
            "min_high": min(highs),
        }

    return {
        "get_current": {"fn": get_current, "description": "Current weather. Args: city."},
        "get_forecast": {"fn": get_forecast, "description": "5-day forecast. Args: city."},
        "get_alerts": {"fn": get_alerts, "description": "Active alerts. Args: city."},
        "compare_cities": {"fn": compare_cities, "description": "Compare two cities."},
        "summarize_week": {"fn": summarize_week, "description": "Weekly stats. Args: city."},
    }
