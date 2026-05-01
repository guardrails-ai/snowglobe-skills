"""Research agent. Routes prompts to up to 5 of its 6 tools per turn.

Behaviour by intent:
  - "research <topic>": search -> extract top -> summarize -> save_citation -> save_note (5 calls)
  - "outline <topic>": build_outline only
  - "search <query>": search only
  - "summarize <text>": summarize_text only
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Union

from .core.llm import StubLLM
from .core.memory import Memory
from .core.openai_loop import _LLM_AVAILABLE, llm_respond
from .tools import make_tools


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_SYSTEM_PROMPT = (
    "You are a research agent. Use tools to search a corpus, extract text "
    "from URLs, summarize text, save citations, build outlines, and save notes."
)


_RESEARCH_RE = re.compile(r"^\s*(?:research|investigate|study)\s+(.+?)\s*$", re.I)
_OUTLINE_RE  = re.compile(r"^\s*(?:outline|structure)\s+(.+?)\s*$", re.I)
_SEARCH_RE   = re.compile(r"^\s*(?:search|find|lookup)\s+(.+?)\s*$", re.I)
_SUMMARIZE_RE = re.compile(r"^\s*summari[sz]e\s*[:\-]?\s*(.+?)\s*$", re.I | re.S)


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


def _do_research(tools, topic: str) -> List[Dict[str, Any]]:
    calls: List[Dict[str, Any]] = []
    s = tools["search"]["fn"](topic)
    calls.append({"name": "search", "args": {"query": topic}, "result": s})
    if not s["ok"] or not s["results"]:
        return calls
    top = s["results"][0]
    e = tools["extract_text"]["fn"](top["url"])
    calls.append({"name": "extract_text", "args": {"url": top["url"]}, "result": e})
    if not e["ok"]:
        return calls
    sm = tools["summarize_text"]["fn"](e["text"], 20)
    calls.append({"name": "summarize_text", "args": {"text": e["text"], "max_words": 20}, "result": sm})
    cit = tools["save_citation"]["fn"](top["title"], top["url"])
    calls.append({"name": "save_citation", "args": {"title": top["title"], "url": top["url"]}, "result": cit})
    if sm["ok"]:
        n = tools["save_note"]["fn"](sm["summary"])
        calls.append({"name": "save_note", "args": {"note": sm["summary"]}, "result": n})
    return calls


def respond(input_: HistoryOrPrompt, memory: Optional[Memory] = None,
            llm: Optional[StubLLM] = None) -> Dict[str, Any]:
    history = _normalize(input_)
    text = _last_user(history)
    memory = memory or Memory()
    llm = llm or StubLLM()
    tools = make_tools(memory, llm)

    if _LLM_AVAILABLE:
        reply, tool_calls = llm_respond(history, tools, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5, "research agent must not exceed 5 tool calls per turn"
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {
            "response": reply,
            "tool_calls": tool_calls,
            "history": history + [new_turn],
        }

    tool_calls: List[Dict[str, Any]] = []
    reply = ""

    if (m := _RESEARCH_RE.match(text)):
        tool_calls = _do_research(tools, m.group(1))
        reply = f"Researched '{m.group(1)}' using {len(tool_calls)} tool calls."
    elif (m := _OUTLINE_RE.match(text)):
        result = tools["build_outline"]["fn"](m.group(1))
        tool_calls.append({"name": "build_outline", "args": {"topic": m.group(1)}, "result": result})
        reply = f"Outline: {result.get('outline')}"
    elif (m := _SEARCH_RE.match(text)):
        result = tools["search"]["fn"](m.group(1))
        tool_calls.append({"name": "search", "args": {"query": m.group(1)}, "result": result})
        reply = f"Found {len(result.get('results', []))} hits."
    elif (m := _SUMMARIZE_RE.match(text)):
        result = tools["summarize_text"]["fn"](m.group(1), 30)
        tool_calls.append({"name": "summarize_text", "args": {"text": m.group(1)}, "result": result})
        reply = result.get("summary", "")
    else:
        reply = "Try 'research X', 'search X', 'outline X', 'summarize: ...'."

    assert len(tool_calls) <= 5, "research agent must not exceed 5 tool calls per turn"
    new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
    return {
        "response": reply,
        "tool_calls": tool_calls,
        "history": history + [new_turn],
    }


class ResearchAgent:
    def __init__(self) -> None:
        self.memory = Memory()
        self.llm = StubLLM()
        self.history: List[Message] = []
        self.tools = make_tools(self.memory, self.llm)

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}], self.memory, self.llm)
        self.history = out["history"]
        return out["response"]
