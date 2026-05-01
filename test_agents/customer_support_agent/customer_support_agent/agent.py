"""Customer support agent. Most actions trigger one tool call; ticket creation
chains lookup_user -> create_ticket -> send_email (3 calls).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._llm import _LLM_AVAILABLE, llm_respond
from .data import Store, seed_store
from .routing import parse
from .tools import make_tools


Message = Dict[str, Any]
HistoryOrPrompt = Union[str, List[Message]]


_SYSTEM_PROMPT = (
    "You are a customer support agent. Use tools to look up users, view "
    "history, create tickets, escalate, send emails, issue refunds, update "
    "preferences, and search the FAQ."
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


def respond(input_: HistoryOrPrompt, store: Optional[Store] = None) -> Dict[str, Any]:
    history = _normalize(input_)
    text = _last_user(history)
    store = store or seed_store()
    tools = make_tools(store)

    if _LLM_AVAILABLE:
        reply, tool_calls = llm_respond(history, tools, _SYSTEM_PROMPT)
        assert len(tool_calls) <= 5
        new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
        return {"response": reply, "tool_calls": tool_calls, "history": history + [new_turn]}

    intent = parse(text)

    tool_calls: List[Dict[str, Any]] = []
    reply = ""

    if intent.action == "lookup":
        r = tools["lookup_user"]["fn"](intent.user_id)
        tool_calls.append({"name": "lookup_user", "args": {"user_id": intent.user_id}, "result": r})
        reply = f"{r['user']['name']} ({r['user']['email']}, {r['user']['plan']})" if r["ok"] else r["error"]
    elif intent.action == "history":
        r = tools["view_history"]["fn"](intent.user_id)
        tool_calls.append({"name": "view_history", "args": {"user_id": intent.user_id}, "result": r})
        reply = f"{len(r['interactions'])} interactions" if r["ok"] else r["error"]
    elif intent.action == "ticket":
        u = tools["lookup_user"]["fn"](intent.user_id)
        tool_calls.append({"name": "lookup_user", "args": {"user_id": intent.user_id}, "result": u})
        if not u["ok"]:
            reply = u["error"]
        else:
            t = tools["create_ticket"]["fn"](intent.user_id, intent.subject, intent.body)
            tool_calls.append({"name": "create_ticket",
                                 "args": {"user_id": intent.user_id, "subject": intent.subject, "body": intent.body},
                                 "result": t})
            if t["ok"]:
                e = tools["send_email"]["fn"](intent.user_id,
                                                f"ticket #{t['ticket']['id']} created",
                                                f"We received: {intent.subject}")
                tool_calls.append({"name": "send_email",
                                     "args": {"user_id": intent.user_id,
                                              "subject": f"ticket #{t['ticket']['id']} created",
                                              "body": f"We received: {intent.subject}"},
                                     "result": e})
                reply = f"created ticket #{t['ticket']['id']} and emailed user"
            else:
                reply = t["error"]
    elif intent.action == "escalate":
        r = tools["escalate"]["fn"](intent.ticket_id)
        tool_calls.append({"name": "escalate", "args": {"ticket_id": intent.ticket_id}, "result": r})
        reply = f"escalated ticket #{intent.ticket_id}" if r["ok"] else r["error"]
    elif intent.action == "email":
        r = tools["send_email"]["fn"](intent.user_id, intent.subject, intent.body)
        tool_calls.append({"name": "send_email",
                            "args": {"user_id": intent.user_id, "subject": intent.subject, "body": intent.body},
                            "result": r})
        reply = "email sent" if r["ok"] else r["error"]
    elif intent.action == "refund":
        r = tools["refund"]["fn"](intent.user_id, intent.amount)
        tool_calls.append({"name": "refund", "args": {"user_id": intent.user_id, "amount": intent.amount}, "result": r})
        reply = f"refunded ${intent.amount} to user {intent.user_id}" if r["ok"] else r["error"]
    elif intent.action == "pref":
        r = tools["update_preferences"]["fn"](intent.user_id, intent.pref_key, intent.pref_value)
        tool_calls.append({"name": "update_preferences",
                            "args": {"user_id": intent.user_id, "key": intent.pref_key, "value": intent.pref_value},
                            "result": r})
        reply = "preferences updated" if r["ok"] else r["error"]
    elif intent.action == "faq":
        r = tools["faq_search"]["fn"](intent.text)
        tool_calls.append({"name": "faq_search", "args": {"query": intent.text}, "result": r})
        reply = f"{len(r['results'])} faq result(s)" if r["ok"] else r["error"]
    else:
        reply = ("I can: lookup user, history, create ticket, escalate, email, refund, "
                 "set preferences, or search the FAQ.")

    assert len(tool_calls) <= 5
    new_turn: Message = {"role": "assistant", "content": reply, "tool_calls": tool_calls}
    return {"response": reply, "tool_calls": tool_calls, "history": history + [new_turn]}


class CustomerSupportAgent:
    def __init__(self, store: Optional[Store] = None) -> None:
        self.store = store or seed_store()
        self.history: List[Message] = []
        self.tools = make_tools(self.store)

    def chat(self, prompt: str) -> str:
        out = respond(self.history + [{"role": "user", "content": prompt}], self.store)
        self.history = out["history"]
        return out["response"]
