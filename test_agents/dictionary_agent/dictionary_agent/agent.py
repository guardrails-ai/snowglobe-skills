"""Dictionary agent. Routes prompts to either `define` or `synonyms` tools.

May fire up to 2 tool calls in one turn (define + synonyms for the same word).
"""
from __future__ import annotations

import re
from typing import Union, List, Dict, Any

from ._llm import _LLM_AVAILABLE, llm_respond
from .tools import TOOLS, define, synonyms


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_SYSTEM_PROMPT = (
    "You are a dictionary agent. Use the define and synonyms tools to look "
    "up word definitions and synonyms."
)


_DEFINE_RE = re.compile(r"\b(define|definition of|what does .* mean|meaning of)\b", re.I)
_SYN_RE = re.compile(r"\b(synonym|synonyms|other words for)\b", re.I)
_WORD_RE = re.compile(r"['\"]?([a-zA-Z]+)['\"]?\s*[\?\.]?\s*$")


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


def _extract_word(text: str) -> str:
    text = text.strip()
    match = _WORD_RE.search(text)
    if not match:
        return ""
    return match.group(1).lower()


def respond(input_: HistoryOrPrompt) -> Dict[str, Any]:
    history = _normalize(input_)
    user_text = _last_user(history)

    if _LLM_AVAILABLE:
        reply, tool_calls = llm_respond(history, TOOLS, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {
            "response": reply,
            "tool_calls": tool_calls,
            "history": history + [new_turn],
        }

    word = _extract_word(user_text)

    wants_define = bool(_DEFINE_RE.search(user_text))
    wants_syn = bool(_SYN_RE.search(user_text))
    if not wants_define and not wants_syn:
        if word and len(user_text.strip().split()) == 1:
            wants_define = True

    tool_calls: List[Dict[str, Any]] = []
    parts: List[str] = []

    if not word or (not wants_define and not wants_syn):
        text = "Tell me a single word to look up, e.g. 'define happy' or 'synonyms for sad'."
    else:
        if wants_define:
            res = define(word)
            tool_calls.append({"name": "define", "args": {"word": word}, "result": res})
            parts.append(
                f"{word}: {res['definition']}" if res["ok"] else f"No definition for '{word}'."
            )
        if wants_syn:
            res = synonyms(word)
            tool_calls.append({"name": "synonyms", "args": {"word": word}, "result": res})
            if res["ok"]:
                parts.append(f"synonyms: {', '.join(res['synonyms'])}")
            else:
                parts.append(f"No synonyms for '{word}'.")
        text = "\n".join(parts)

    new_turn: Message = {"role": "assistant", "content": text, "tool_calls": tool_calls}
    return {
        "response": text,
        "tool_calls": tool_calls,
        "history": history + [new_turn],
    }


class DictionaryAgent:
    def __init__(self) -> None:
        self.history: List[Message] = []
        self.tools = TOOLS

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}])
        self.history = out["history"]
        return out["response"]
