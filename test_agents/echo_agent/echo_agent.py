"""Echo agent: the simplest possible text agent. Repeats input with a hello.

Accepts either a prompt string or a message-history list and returns the next
turn. Has no tools.
"""
from __future__ import annotations

import inspect
import json as _json
import os
from typing import Union, List, Dict, Any, Tuple


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_LLM_AVAILABLE = False
try:
    from openai import OpenAI  # type: ignore
    _LLM_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    OpenAI = None  # type: ignore


def _echo(text: str) -> Dict[str, Any]:
    return {"ok": True, "echo": f"Echo: {text}"}


_TOOLS: Dict[str, Dict[str, Any]] = {
    "echo": {"fn": _echo, "description": "Echo the user's text. Args: text (str)."},
}


_SYSTEM_PROMPT = (
    "You are an echo agent. Use the echo tool to repeat the user's message."
)


def _build_tool_specs(tools_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    specs: List[Dict[str, Any]] = []
    for name, info in tools_map.items():
        sig = inspect.signature(info["fn"])
        properties: Dict[str, Any] = {}
        required: List[str] = []
        for pname, param in sig.parameters.items():
            properties[pname] = {"type": "string", "description": pname}
            if param.default is inspect.Parameter.empty:
                required.append(pname)
        specs.append({
            "type": "function",
            "function": {
                "name": name,
                "description": info.get("description", name),
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        })
    return specs


def _llm_respond(history: List[Dict[str, Any]], tools_map: Dict[str, Dict[str, Any]],
                 system_prompt: str) -> Tuple[str, List[Dict[str, Any]]]:
    if not history:
        return "", []
    client = OpenAI()
    specs = _build_tool_specs(tools_map)
    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    for entry in history:
        role = entry.get("role")
        if role not in ("user", "assistant"):
            continue
        messages.append({"role": role, "content": entry.get("content", "")})
    tool_calls_taken: List[Dict[str, Any]] = []
    for _ in range(5):
        resp = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=specs,
        )
        msg = resp.choices[0].message
        if not msg.tool_calls:
            return (msg.content or ""), tool_calls_taken
        messages.append(msg)
        for tc in msg.tool_calls:
            try:
                args = _json.loads(tc.function.arguments or "{}")
            except _json.JSONDecodeError:
                args = {}
            try:
                result = tools_map[tc.function.name]["fn"](**args)
            except Exception as e:
                result = {"error": str(e)}
            tool_calls_taken.append({
                "name": tc.function.name,
                "args": args,
                "result": result,
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result),
            })
    return "(reached max tool calls)", tool_calls_taken


def _normalize(input_: HistoryOrPrompt) -> List[Message]:
    if isinstance(input_, str):
        return [{"role": "user", "content": input_}]
    if isinstance(input_, list):
        for m in input_:
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise ValueError("history entries must be {role, content} dicts")
        return list(input_)
    raise TypeError("input must be a str prompt or list of message dicts")


def respond(input_: HistoryOrPrompt) -> Dict[str, Any]:
    """Generate the next assistant turn.

    Returns a dict with keys: response, tool_calls, history.
    """
    history = _normalize(input_)
    last_user = next(
        (m["content"] for m in reversed(history) if m["role"] == "user"),
        "",
    )

    if _LLM_AVAILABLE:
        reply, tool_calls = _llm_respond(history, _TOOLS, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {"response": reply, "tool_calls": tool_calls, "history": history + [new_turn]}

    text = f"Echo: {last_user}" if last_user else "Echo: (no input)"
    new_turn = {"role": "assistant", "content": text}
    return {
        "response": text,
        "tool_calls": [],
        "history": history + [new_turn],
    }


class EchoAgent:
    """Class-style wrapper around respond() for callers that want state."""

    def __init__(self) -> None:
        self.history: List[Message] = []

    def chat(self, prompt: str) -> str:
        result = respond(self.history + [{"role": "user", "content": prompt}])
        self.history = result["history"]
        return result["response"]
