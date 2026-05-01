"""Stub LLM used by tools that need text 'generation'."""
from __future__ import annotations


class StubLLM:
    def respond(self, prompt: str) -> str:
        return f"[stub] {prompt[:60]}"
