"""LLM-driven tool-call loop helpers (LiteLLM backend, routes to OpenAI)."""
from __future__ import annotations

import inspect
import json as _json
import os
from typing import Any, Dict, List, Tuple


_LLM_AVAILABLE = False
try:
    import litellm  # type: ignore
    _LLM_AVAILABLE = bool(os.environ.get("OPENAI_API_KEY"))
except ImportError:
    litellm = None  # type: ignore


MODEL = "gpt-4o-mini"


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


def llm_respond(history: List[Dict[str, Any]], tools_map: Dict[str, Dict[str, Any]],
                system_prompt: str) -> Tuple[str, List[Dict[str, Any]]]:
    if not history:
        return "", []
    specs = _build_tool_specs(tools_map)
    messages: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]
    for entry in history:
        role = entry.get("role")
        if role not in ("user", "assistant"):
            continue
        messages.append({"role": role, "content": entry.get("content", "")})
    tool_calls_taken: List[Dict[str, Any]] = []
    for _ in range(5):
        resp = litellm.completion(
            model=MODEL, messages=messages, tools=specs,
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
