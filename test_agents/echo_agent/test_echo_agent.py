import unittest

from echo_agent import EchoAgent, respond


class EchoAgentTests(unittest.TestCase):
    def test_prompt_string(self):
        result = respond("hi there")
        self.assertEqual(result["response"], "Echo: hi there")
        self.assertEqual(result["tool_calls"], [])
        self.assertEqual(len(result["history"]), 2)

    def test_history_list(self):
        history = [
            {"role": "user", "content": "first"},
            {"role": "assistant", "content": "ok"},
            {"role": "user", "content": "second"},
        ]
        result = respond(history)
        self.assertEqual(result["response"], "Echo: second")
        self.assertEqual(result["history"][-1]["role"], "assistant")

    def test_empty_history(self):
        result = respond([])
        self.assertEqual(result["response"], "Echo: (no input)")

    def test_invalid_input_type(self):
        with self.assertRaises(TypeError):
            respond(42)

    def test_invalid_history_entry(self):
        with self.assertRaises(ValueError):
            respond([{"role": "user"}])

    def test_class_chat_keeps_state(self):
        agent = EchoAgent()
        agent.chat("one")
        out = agent.chat("two")
        self.assertEqual(out, "Echo: two")
        self.assertEqual(len(agent.history), 4)


if __name__ == "__main__":
    unittest.main()
