import unittest

from todo_agent import TodoAgent, Database, respond


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = TodoAgent()

    def test_add(self):
        out = self.agent.chat("add buy milk")
        self.assertIn("Added", out)
        self.assertEqual(len(self.agent.db.list()), 1)

    def test_list(self):
        self.agent.chat("add x")
        self.agent.chat("add y")
        out = self.agent.chat("list todos")
        self.assertIn("2", out)

    def test_list_open(self):
        self.agent.chat("add x")
        self.agent.chat("complete 1")
        out = self.agent.chat("list open todos")
        self.assertIn("0", out)

    def test_complete(self):
        self.agent.chat("add x")
        out = self.agent.chat("complete 1")
        self.assertIn("done", out)

    def test_delete(self):
        self.agent.chat("add x")
        out = self.agent.chat("delete 1")
        self.assertIn("Deleted", out)

    def test_unknown(self):
        out = self.agent.chat("hello")
        self.assertIn("Try", out)

    def test_max_tool_calls(self):
        out = respond("add foo", Database())
        self.assertLessEqual(len(out["tool_calls"]), 5)


if __name__ == "__main__":
    unittest.main()
