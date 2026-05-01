import unittest

from research_agent.core.memory import Memory
from research_agent.core.llm import StubLLM
from research_agent.tools import (
    search, extract_text, summarize_text,
    save_citation, build_outline, save_note,
)


class ToolTests(unittest.TestCase):
    def test_search(self):
        out = search("python")
        self.assertTrue(out["ok"])
        self.assertGreaterEqual(len(out["results"]), 1)

    def test_search_empty(self):
        self.assertFalse(search("")["ok"])

    def test_extract(self):
        out = extract_text("https://example.com/python")
        self.assertTrue(out["ok"])

    def test_extract_missing(self):
        self.assertFalse(extract_text("https://nope")["ok"])

    def test_summarize(self):
        out = summarize_text(StubLLM(), "the quick brown fox", 2)
        self.assertTrue(out["ok"])

    def test_save_citation(self):
        m = Memory()
        save_citation(m, "t", "u")
        self.assertEqual(len(m.citations), 1)

    def test_outline(self):
        m = Memory()
        out = build_outline(StubLLM(), m, "ai", 4)
        self.assertEqual(len(out["outline"]), 4)
        self.assertEqual(len(m.outline), 4)

    def test_save_note(self):
        m = Memory()
        save_note(m, "hi")
        self.assertEqual(m.notes, ["hi"])


if __name__ == "__main__":
    unittest.main()
