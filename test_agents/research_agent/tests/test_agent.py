import unittest

from research_agent import ResearchAgent, respond


class AgentTests(unittest.TestCase):
    def test_research_runs_pipeline(self):
        a = ResearchAgent()
        out = respond("research python", a.memory, a.llm)
        names = [c["name"] for c in out["tool_calls"]]
        self.assertIn("search", names)
        self.assertLessEqual(len(out["tool_calls"]), 5)

    def test_search_alone(self):
        out = respond("search python", None, None)
        self.assertEqual([c["name"] for c in out["tool_calls"]], ["search"])

    def test_outline(self):
        out = respond("outline ai agents", None, None)
        self.assertEqual(out["tool_calls"][0]["name"], "build_outline")

    def test_summarize(self):
        out = respond("summarize: the quick brown fox jumps", None, None)
        self.assertEqual(out["tool_calls"][0]["name"], "summarize_text")

    def test_unknown(self):
        out = respond("hello", None, None)
        self.assertEqual(out["tool_calls"], [])

    def test_chat_history(self):
        a = ResearchAgent()
        a.chat("search python")
        a.chat("search agents")
        self.assertEqual(len(a.history), 4)


if __name__ == "__main__":
    unittest.main()
