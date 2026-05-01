"""Weather agent with five tools.

Decides which tool(s) to call based on keyword routing. Caps tool calls at 5
per turn (the agent itself is configured to dispatch at most 3 in any one
prompt — well under the limit).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union

from ._llm import _LLM_AVAILABLE, llm_respond
from .api_client import WeatherClient
from .cache import Cache
from .formatter import format_alerts, format_current, format_forecast
from .tools import make_tools


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_SYSTEM_PROMPT = (
    "You are a weather agent. Use tools to fetch current conditions, "
    "forecasts, alerts, weekly summaries, and to compare cities."
)


_KNOWN_CITIES = ["san francisco", "new york", "london", "tokyo"]
_COMPARE_RE = re.compile(r"compare\s+(.+?)\s+(?:and|vs|to)\s+(.+?)\s*[\?\.]?$", re.I)


def _normalize(input_: HistoryOrPrompt) -> List[Message]:
    if isinstance(input_, str):
        return [{"role": "user", "content": input_}]
    if not isinstance(input_, list):
        raise TypeError("input must be str or list")
    return list(input_)


def _last_user(history: List[Message]) -> str:
    for m in reversed(history):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""


def _find_cities(text: str) -> List[str]:
    text_l = text.lower()
    return [c for c in _KNOWN_CITIES if c in text_l]


def respond(input_: HistoryOrPrompt, client: Optional[WeatherClient] = None,
            cache: Optional[Cache] = None) -> Dict[str, Any]:
    history = _normalize(input_)
    text = _last_user(history)
    client = client or WeatherClient()
    cache = cache or Cache()
    tools = make_tools(client, cache)

    if _LLM_AVAILABLE:
        reply, tool_calls = llm_respond(history, tools, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {
            "response": reply,
            "tool_calls": tool_calls,
            "history": history + [new_turn],
        }

    tool_calls: List[Dict[str, Any]] = []
    parts: List[str] = []

    cmp_m = _COMPARE_RE.search(text)
    cities = _find_cities(text)
    text_l = text.lower()

    if cmp_m and len(cities) >= 2:
        result = tools["compare_cities"]["fn"](cities[0], cities[1])
        tool_calls.append({"name": "compare_cities", "args": {"city_a": cities[0], "city_b": cities[1]}, "result": result})
        if result["ok"]:
            parts.append(f"{result['warmer'].title()} is warmer.")
    elif cities:
        city = cities[0]
        wants_alerts = "alert" in text_l or "warning" in text_l
        wants_forecast = "forecast" in text_l or "week" in text_l
        wants_summary = "summary" in text_l or "summarize" in text_l
        if wants_alerts:
            r = tools["get_alerts"]["fn"](city)
            tool_calls.append({"name": "get_alerts", "args": {"city": city}, "result": r})
            if r["ok"]:
                parts.append(format_alerts(r["data"]))
        if wants_forecast:
            r = tools["get_forecast"]["fn"](city)
            tool_calls.append({"name": "get_forecast", "args": {"city": city}, "result": r})
            if r["ok"]:
                parts.append(format_forecast(r["data"]))
        if wants_summary:
            r = tools["summarize_week"]["fn"](city)
            tool_calls.append({"name": "summarize_week", "args": {"city": city}, "result": r})
            if r["ok"]:
                parts.append(f"avg high {r['avg_high']:.1f}F (max {r['max_high']}, min {r['min_high']})")
        if not (wants_alerts or wants_forecast or wants_summary):
            r = tools["get_current"]["fn"](city)
            tool_calls.append({"name": "get_current", "args": {"city": city}, "result": r})
            if r["ok"]:
                parts.append(format_current(r["data"]))
    if not tool_calls:
        parts.append(f"Tell me a city ({', '.join(c.title() for c in _KNOWN_CITIES)}).")

    assert len(tool_calls) <= 5
    text_out = " ".join(parts) if parts else "ok"
    new_turn: Message = {"role": "assistant", "content": text_out, "tool_calls": tool_calls}
    return {
        "response": text_out,
        "tool_calls": tool_calls,
        "history": history + [new_turn],
    }


class WeatherAgent:
    def __init__(self, client: Optional[WeatherClient] = None) -> None:
        self.client = client or WeatherClient()
        self.cache = Cache()
        self.history: List[Message] = []
        self.tools = make_tools(self.client, self.cache)

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}], self.client, self.cache)
        self.history = out["history"]
        return out["response"]
