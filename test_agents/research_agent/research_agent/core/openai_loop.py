"""LLM-driven tool-call loop helpers (Anthropic backend).

Module name kept as ``openai_loop`` for import-stability; backend is Anthropic.
"""
from __future__ import annotations

import inspect
import os
from typing import Any, Dict, List, Tuple


_LLM_AVAILABLE = False
try:
    import anthropic  # type: ignore
    _LLM_AVAILABLE = bool(os.environ.get("ANTHROPIC_API_KEY"))
except ImportError:
    anthropic = None  # type: ignore


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
            "name": name,
            "description": info.get("description", name),
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        })
    return specs


def _build_messages_from_history(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Build Anthropic messages list with strict user/assistant alternation."""
    messages: List[Dict[str, Any]] = []
    for entry in history:
        role = entry.get("role")
        if role not in ("user", "assistant"):
            continue
        content = entry.get("content", "")
        if messages and messages[-1]["role"] == role:
            messages[-1]["content"] = f"{messages[-1]['content']}\n\n{content}"
        else:
            messages.append({"role": role, "content": content})
    return messages


def llm_respond(history: List[Dict[str, Any]], tools_map: Dict[str, Dict[str, Any]],
                system_prompt: str) -> Tuple[str, List[Dict[str, Any]]]:
    if not history:
        return "", []
    client = anthropic.Anthropic()
    specs = _build_tool_specs(tools_map)
    messages: List[Dict[str, Any]] = _build_messages_from_history(history)
    if not messages:
        return "", []
    tool_calls_taken: List[Dict[str, Any]] = []
    for _ in range(5):
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            tools=specs,
            messages=messages,
        )
        if resp.stop_reason != "tool_use":
            text = "".join(
                getattr(b, "text", "") for b in resp.content
                if getattr(b, "type", None) == "text"
            )
            return text, tool_calls_taken
        messages.append({"role": "assistant", "content": resp.content})
        tool_results: List[Dict[str, Any]] = []
        for block in resp.content:
            if getattr(block, "type", None) != "tool_use":
                continue
            args = block.input or {}
            try:
                result = tools_map[block.name]["fn"](**args)
            except Exception as e:
                result = {"error": str(e)}
            tool_calls_taken.append({
                "name": block.name,
                "args": args,
                "result": result,
            })
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": str(result),
            })
        messages.append({"role": "user", "content": tool_results})
    return "(reached max tool calls)", tool_calls_taken
