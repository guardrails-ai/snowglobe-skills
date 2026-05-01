"""Todo agent: parses prompts, dispatches up to 5 tool calls per turn."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union

from ._llm import _LLM_AVAILABLE, llm_respond
from .db import Database
from .tools import make_tools


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_SYSTEM_PROMPT = (
    "You are a todo agent. Use tools to add todos, list them, mark them "
    "complete, or delete them by id."
)


_ADD_RE = re.compile(r"^\s*(?:add|new)\s+(?:todo\s+)?[\"']?(.+?)[\"']?\s*$", re.I)
_LIST_RE = re.compile(r"^\s*(list|show|all)(?:\s+todos?)?(?:\s+(?:open|pending|active))?\s*$", re.I)
_LIST_OPEN_RE = re.compile(r"^\s*(?:list|show)\s+(?:open|pending|active)\s*(?:todos?)?\s*$", re.I)
_COMPLETE_RE = re.compile(r"^\s*(?:complete|done|finish|mark)\s+(?:todo\s+)?#?(\d+)\s*$", re.I)
_DELETE_RE = re.compile(r"^\s*(?:delete|remove|drop)\s+(?:todo\s+)?#?(\d+)\s*$", re.I)


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


def respond(input_: HistoryOrPrompt, db: Optional[Database] = None) -> Dict[str, Any]:
    history = _normalize(input_)
    text = _last_user(history)
    db = db or Database()
    tools = make_tools(db)

    if _LLM_AVAILABLE:
        reply_str, tool_calls = llm_respond(history, tools, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5
        new_turn: Message = {"role": "assistant", "content": reply_str, "tool_calls": tool_calls}
        return {
            "response": reply_str,
            "tool_calls": tool_calls,
            "history": history + [new_turn],
        }

    tool_calls: List[Dict[str, Any]] = []
    reply: Optional[str] = None

    if (m := _COMPLETE_RE.match(text)):
        tid = int(m.group(1))
        result = tools["complete_todo"]["fn"](tid)
        tool_calls.append({"name": "complete_todo", "args": {"todo_id": tid}, "result": result})
        reply = f"Marked #{tid} done." if result["ok"] else result["error"]
    elif (m := _DELETE_RE.match(text)):
        tid = int(m.group(1))
        result = tools["delete_todo"]["fn"](tid)
        tool_calls.append({"name": "delete_todo", "args": {"todo_id": tid}, "result": result})
        reply = f"Deleted #{tid}." if result["ok"] else result["error"]
    elif _LIST_OPEN_RE.match(text):
        result = tools["list_todos"]["fn"](include_done=False)
        tool_calls.append({"name": "list_todos", "args": {"include_done": False}, "result": result})
        reply = f"{len(result['todos'])} open todo(s)."
    elif _LIST_RE.match(text):
        result = tools["list_todos"]["fn"](include_done=True)
        tool_calls.append({"name": "list_todos", "args": {"include_done": True}, "result": result})
        reply = f"You have {len(result['todos'])} todo(s)."
    elif (m := _ADD_RE.match(text)):
        body = m.group(1).strip()
        result = tools["add_todo"]["fn"](body)
        tool_calls.append({"name": "add_todo", "args": {"text": body}, "result": result})
        reply = f"Added todo #{result['todo']['id']}." if result["ok"] else result["error"]
    else:
        reply = "Try: 'add buy milk', 'list todos', 'complete 3', 'delete 2'."

    new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
    return {
        "response": reply,
        "tool_calls": tool_calls,
        "history": history + [new_turn],
    }


class TodoAgent:
    def __init__(self, db: Optional[Database] = None) -> None:
        self.db = db or Database()
        self.history: List[Message] = []
        self.tools = make_tools(self.db)

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}], self.db)
        self.history = out["history"]
        return out["response"]
