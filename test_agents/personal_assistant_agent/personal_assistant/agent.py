"""Personal assistant agent with 10 tools.

Most prompts trigger one tool call. Special compound intents (e.g.
"plan my morning in city X") chain up to 5 calls.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union

from .intent import parse
from .llm.openai_loop import _LLM_AVAILABLE, llm_respond
from .memory import Memory
from .tools import calendar_list, make_tools, note_list, reminder_list


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_PLAN_RE = re.compile(r"^\s*plan\s+my\s+(?:day|morning)\s+in\s+(.+?)\s*$", re.I)


_SYSTEM_PROMPT = (
    "You are a personal assistant. Use tools to manage calendar events, send "
    "email, get weather, set reminders, search the web, do calculations, save "
    "notes, manage contacts, fetch news, and translate text."
)


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


def _plan_morning(tools, memory, city: str) -> List[Dict[str, Any]]:
    calls: List[Dict[str, Any]] = []
    w = tools["weather"]["fn"](city)
    calls.append({"name": "weather", "args": {"city": city}, "result": w})
    n = tools["news"]["fn"](city)
    calls.append({"name": "news", "args": {"topic": city}, "result": n})
    c = tools["calendar"]["fn"]("morning standup", "today 9am")
    calls.append({"name": "calendar", "args": {"title": "morning standup", "when": "today 9am"},
                    "result": c})
    r = tools["reminders"]["fn"]("review inbox", "9:30am")
    calls.append({"name": "reminders", "args": {"text": "review inbox", "when": "9:30am"},
                    "result": r})
    note = tools["notes"]["fn"](f"morning plan for {city}")
    calls.append({"name": "notes", "args": {"text": f"morning plan for {city}"}, "result": note})
    return calls


def respond(input_: HistoryOrPrompt, memory: Optional[Memory] = None) -> Dict[str, Any]:
    history = _normalize(input_)
    text = _last_user(history)
    memory = memory or Memory()
    tools = make_tools(memory)

    if _LLM_AVAILABLE:
        reply, tool_calls = llm_respond(history, tools, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5, "personal assistant must not exceed 5 tool calls per turn"
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {"response": reply, "tool_calls": tool_calls, "history": history + [new_turn]}

    tool_calls: List[Dict[str, Any]] = []
    reply = ""

    pm = _PLAN_RE.match(text)
    if pm:
        city = pm.group(1)
        tool_calls = _plan_morning(tools, memory, city)
        reply = f"morning plan ready for {city} ({len(tool_calls)} actions)"
    else:
        intents = parse(text)
        for action, args in intents:
            if action == "calendar_list":
                r = calendar_list(memory)
                tool_calls.append({"name": "calendar_list", "args": {}, "result": r})
                reply = f"{len(r['events'])} event(s)"
            elif action == "calendar_add":
                r = tools["calendar"]["fn"](**args)
                tool_calls.append({"name": "calendar", "args": args, "result": r})
                reply = f"event #{r['event']['id']} added" if r["ok"] else r["error"]
            elif action == "email_send":
                r = tools["email"]["fn"](**args)
                tool_calls.append({"name": "email", "args": args, "result": r})
                reply = "email sent" if r["ok"] else r["error"]
            elif action == "weather":
                r = tools["weather"]["fn"](**args)
                tool_calls.append({"name": "weather", "args": args, "result": r})
                reply = (f"{r['city'].title()}: {r['temp_f']}F {r['condition']}" if r["ok"] else r["error"])
            elif action == "reminder_add":
                r = tools["reminders"]["fn"](**args)
                tool_calls.append({"name": "reminders", "args": args, "result": r})
                reply = f"reminder #{r['reminder']['id']} set" if r["ok"] else r["error"]
            elif action == "reminder_list":
                r = reminder_list(memory)
                tool_calls.append({"name": "reminder_list", "args": {}, "result": r})
                reply = f"{len(r['reminders'])} reminder(s)"
            elif action == "search":
                r = tools["search"]["fn"](**args)
                tool_calls.append({"name": "search", "args": args, "result": r})
                reply = f"{len(r['results'])} hit(s)"
            elif action == "calculate":
                r = tools["calculator"]["fn"](**args)
                tool_calls.append({"name": "calculator", "args": args, "result": r})
                reply = str(r.get("result")) if r["ok"] else r["error"]
            elif action == "note_add":
                r = tools["notes"]["fn"](**args)
                tool_calls.append({"name": "notes", "args": args, "result": r})
                reply = f"note saved (#{r['count']})" if r["ok"] else r["error"]
            elif action == "note_list":
                r = note_list(memory)
                tool_calls.append({"name": "note_list", "args": {}, "result": r})
                reply = f"{len(r['notes'])} note(s)"
            elif action == "contact_add":
                r = tools["contacts"]["fn"](**args)
                tool_calls.append({"name": "contacts", "args": args, "result": r})
                reply = "contact saved" if r["ok"] else r["error"]
            elif action == "contact_lookup":
                r = tools["contacts"]["fn"](**args)
                tool_calls.append({"name": "contacts", "args": args, "result": r})
                reply = (f"{r['contact']['name']} -> {r['contact']['email']}"
                         if r["ok"] else r["error"])
            elif action == "news":
                r = tools["news"]["fn"](**args)
                tool_calls.append({"name": "news", "args": args, "result": r})
                reply = f"{len(r['headlines'])} headline(s)" if r["ok"] else r["error"]
            elif action == "translate":
                r = tools["translate"]["fn"](**args)
                tool_calls.append({"name": "translate", "args": args, "result": r})
                reply = r["translation"] if r["ok"] else r["error"]

    if not tool_calls and not reply:
        reply = ("I can: schedule, email, weather, remind, search, calculate, note, "
                 "contacts, news, translate, or 'plan my morning in <city>'.")

    assert len(tool_calls) <= 5, "personal assistant must not exceed 5 tool calls per turn"
    new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
    return {"response": reply, "tool_calls": tool_calls, "history": history + [new_turn]}


class PersonalAssistant:
    def __init__(self, memory: Optional[Memory] = None) -> None:
        self.memory = memory or Memory()
        self.history: List[Message] = []
        self.tools = make_tools(self.memory)

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}], self.memory)
        self.history = out["history"]
        return out["response"]
