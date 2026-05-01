"""Stub 'LLM' that produces deterministic outputs from inputs.

This lets the agent be tested without API access, while keeping the same
interface a real LLM would expose.
"""
from __future__ import annotations

from typing import List

from ..utils import tokenize, truncate


class StubLLM:
    def summarize(self, text: str, max_words: int = 30) -> str:
        words = tokenize(text)
        if not words:
            return ""
        return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

    def outline(self, topic: str, n: int = 3) -> List[str]:
        topic = topic.strip() or "topic"
        return [f"section {i+1}: aspect of {truncate(topic, 30)}" for i in range(n)]
