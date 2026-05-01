"""Pretty-printers for tool outputs."""
from __future__ import annotations

from typing import Any, Dict


def format_current(payload: Dict[str, Any]) -> str:
    if payload.get("error"):
        return f"weather error: {payload['error']}"
    return (
        f"{payload['city'].title()}: {payload['temp_f']}F, "
        f"{payload['condition']}, humidity {payload['humidity']}%, wind {payload['wind_mph']}mph"
    )


def format_forecast(payload: Dict[str, Any]) -> str:
    if payload.get("error"):
        return f"forecast error: {payload['error']}"
    parts = [f"day {d['day']}: {d['low_f']}-{d['high_f']}F" for d in payload["days"]]
    return f"{payload['city'].title()} forecast: " + "; ".join(parts)


def format_alerts(payload: Dict[str, Any]) -> str:
    if payload.get("error"):
        return f"alerts error: {payload['error']}"
    if not payload["alerts"]:
        return f"No alerts for {payload['city'].title()}."
    return f"{payload['city'].title()}: " + ", ".join(
        f"[{a['severity']}] {a['title']}" for a in payload["alerts"]
    )
