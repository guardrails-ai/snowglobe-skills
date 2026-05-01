import unittest

from note_agent import NoteAgent, NoteStore, respond


class StoreTests(unittest.TestCase):
    def test_add_and_search(self):
        s = NoteStore()
        s.add("groceries", "milk eggs")
        s.add("books", "kafka")
        self.assertEqual(len(s.search("milk")), 1)
        self.assertEqual(len(s.search("")), 2)
        self.assertEqual(len(s.all()), 2)

    def test_get_missing(self):
        self.assertIsNone(NoteStore().get(999))


class AgentTests(unittest.TestCase):
    def test_add(self):
        agent = NoteAgent()
        out = agent.chat("add groceries: milk and eggs")
        self.assertIn("Saved note", out)
        self.assertEqual(len(agent.store.all()), 1)

    def test_search(self):
        agent = NoteAgent()
        agent.chat("add books: kafka stories")
        out = agent.chat("search kafka")
        self.assertIn("Found 1", out)

    def test_list(self):
        agent = NoteAgent()
        agent.chat("add a: x")
        agent.chat("add b: y")
        out = agent.chat("list notes")
        self.assertIn("2", out)

    def test_noop(self):
        out = respond("hello", NoteStore())
        self.assertEqual(out["tool_calls"], [])

    def test_at_most_one_tool_call_per_turn(self):
        agent = NoteAgent()
        out = respond("add groceries: milk", agent.store)
        self.assertLessEqual(len(out["tool_calls"]), 5)


if __name__ == "__main__":
    unittest.main()
