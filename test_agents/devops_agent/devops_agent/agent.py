"""DevOps agent. Single-tool dispatch; the deploy intent additionally fetches
status before+after to give a 3-call summary (still under the 5 cap).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._llm import _LLM_AVAILABLE, llm_respond
from .config import Config
from .parser import parse
from .tools import make_tools


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_SYSTEM_PROMPT = (
    "You are a DevOps agent. Use tools to check service status, deploy, "
    "rollback, fetch logs, scale, restart, and run healthchecks."
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


def respond(input_: HistoryOrPrompt, config: Optional[Config] = None) -> Dict[str, Any]:
    history = _normalize(input_)
    text = _last_user(history)
    config = config or Config.default()
    tools = make_tools(config)

    if _LLM_AVAILABLE:
        reply, tool_calls = llm_respond(history, tools, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {"response": reply, "tool_calls": tool_calls, "history": history + [new_turn]}

    intent = parse(text)

    tool_calls: List[Dict[str, Any]] = []
    reply = ""

    if intent.action == "status":
        r = tools["get_status"]["fn"](intent.service)
        tool_calls.append({"name": "get_status", "args": {"service": intent.service}, "result": r})
        reply = f"{intent.service}: v{r.get('version')} x{r.get('instances')}" if r["ok"] else r["error"]
    elif intent.action == "deploy":
        before = tools["get_status"]["fn"](intent.service)
        tool_calls.append({"name": "get_status", "args": {"service": intent.service}, "result": before})
        if before["ok"]:
            d = tools["deploy"]["fn"](intent.service, intent.version)
            tool_calls.append({"name": "deploy", "args": {"service": intent.service, "version": intent.version}, "result": d})
            after = tools["get_status"]["fn"](intent.service)
            tool_calls.append({"name": "get_status", "args": {"service": intent.service}, "result": after})
            reply = f"deployed {intent.service} {d['from']} -> {d['to']}" if d["ok"] else d["error"]
        else:
            reply = before["error"]
    elif intent.action == "rollback":
        r = tools["rollback"]["fn"](intent.service)
        tool_calls.append({"name": "rollback", "args": {"service": intent.service}, "result": r})
        reply = f"rolled back {intent.service} to {r.get('rolled_back_to')}" if r["ok"] else r["error"]
    elif intent.action == "logs":
        r = tools["get_logs"]["fn"](intent.service)
        tool_calls.append({"name": "get_logs", "args": {"service": intent.service}, "result": r})
        reply = f"{len(r.get('lines', []))} lines" if r["ok"] else r["error"]
    elif intent.action == "scale":
        r = tools["scale"]["fn"](intent.service, intent.instances)
        tool_calls.append({"name": "scale", "args": {"service": intent.service, "instances": intent.instances}, "result": r})
        reply = f"scaled {intent.service} {r['from']}->{r['to']}" if r["ok"] else r["error"]
    elif intent.action == "restart":
        r = tools["restart"]["fn"](intent.service)
        tool_calls.append({"name": "restart", "args": {"service": intent.service}, "result": r})
        reply = f"restarted {intent.service}" if r["ok"] else r["error"]
    elif intent.action == "healthcheck":
        r = tools["healthcheck"]["fn"](intent.service)
        tool_calls.append({"name": "healthcheck", "args": {"service": intent.service}, "result": r})
        reply = f"{intent.service} healthy={r.get('healthy')}" if r["ok"] else r["error"]
    elif intent.action == "healthcheck_all":
        r = tools["healthcheck"]["fn"]()
        tool_calls.append({"name": "healthcheck", "args": {}, "result": r})
        unhealthy = [s for s, h in r["results"].items() if not h]
        reply = "all healthy" if not unhealthy else f"unhealthy: {', '.join(unhealthy)}"
    else:
        reply = "Try: 'status api', 'deploy api 1.5', 'rollback api', 'logs api', 'scale api 5', 'restart api', 'healthcheck'."

    assert len(tool_calls) <= 5
    new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
    return {"response": reply, "tool_calls": tool_calls, "history": history + [new_turn]}


class DevOpsAgent:
    def __init__(self, config: Optional[Config] = None) -> None:
        self.config = config or Config.default()
        self.history: List[Message] = []
        self.tools = make_tools(self.config)

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}], self.config)
        self.history = out["history"]
        return out["response"]
