"""Note agent: parses intent, dispatches to one of three tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._llm import _LLM_AVAILABLE, llm_respond
from .parser import parse
from .store import NoteStore
from .tools import make_tools


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_SYSTEM_PROMPT = (
    "You are a note-taking agent. Use tools to add notes, search notes by "
    "query, or list all saved notes."
)


def _normalize(input_: HistoryOrPrompt) -> List[Message]:
    if isinstance(input_, str):
        return [{"role": "user", "content": input_}]
    if not isinstance(input_, list):
        raise TypeError("input must be a str or list of messages")
    return list(input_)


def _last_user(history: List[Message]) -> str:
    for m in reversed(history):
        if m.get("role") == "user":
            return str(m.get("content", ""))
    return ""


def respond(input_: HistoryOrPrompt, store: Optional[NoteStore] = None) -> Dict[str, Any]:
    history = _normalize(input_)
    user_text = _last_user(history)
    store = store or NoteStore()
    tools = make_tools(store)

    if _LLM_AVAILABLE:
        reply, tool_calls = llm_respond(history, tools, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {
            "response": reply,
            "tool_calls": tool_calls,
            "history": history + [new_turn],
        }

    intent = parse(user_text)

    tool_calls: List[Dict[str, Any]] = []
    if intent.action == "add":
        result = tools["add_note"]["fn"](intent.title or "", intent.body or "")
        tool_calls.append({"name": "add_note", "args": {"title": intent.title, "body": intent.body}, "result": result})
        text = (
            f"Saved note #{result['note']['id']}: {result['note']['title']}"
            if result["ok"]
            else f"Failed to save note: {result['error']}"
        )
    elif intent.action == "search":
        result = tools["search_notes"]["fn"](intent.query or "")
        tool_calls.append({"name": "search_notes", "args": {"query": intent.query}, "result": result})
        if not result["ok"]:
            text = f"Search failed: {result['error']}"
        else:
            text = (
                f"Found {len(result['results'])} note(s)."
                if result["results"]
                else "No notes match."
            )
    elif intent.action == "list":
        result = tools["list_notes"]["fn"]()
        tool_calls.append({"name": "list_notes", "args": {}, "result": result})
        text = f"You have {len(result['results'])} note(s)."
    else:
        text = "I can add, search, or list notes. e.g. 'add groceries: milk' or 'search milk'."

    new_turn: Message = {"role": "assistant", "content": text, "tool_calls": tool_calls}
    return {
        "response": text,
        "tool_calls": tool_calls,
        "history": history + [new_turn],
    }


class NoteAgent:
    def __init__(self, store: Union[NoteStore, None] = None) -> None:
        self.store = store or NoteStore()
        self.history: List[Message] = []
        self.tools = make_tools(self.store)

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}], self.store)
        self.history = out["history"]
        return out["response"]
