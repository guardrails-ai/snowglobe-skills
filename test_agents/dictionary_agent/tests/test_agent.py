import unittest

from dictionary_agent import DictionaryAgent, respond
from dictionary_agent.tools import define, synonyms, list_tools


class ToolTests(unittest.TestCase):
    def test_define_known(self):
        out = define("happy")
        self.assertTrue(out["ok"])
        self.assertIn("pleasure", out["definition"])

    def test_define_unknown(self):
        self.assertFalse(define("xyzzy")["ok"])

    def test_define_blank(self):
        self.assertFalse(define("")["ok"])

    def test_synonyms_known(self):
        out = synonyms("sad")
        self.assertTrue(out["ok"])
        self.assertIn("blue", out["synonyms"])

    def test_synonyms_unknown(self):
        self.assertFalse(synonyms("xyzzy")["ok"])

    def test_list_tools(self):
        self.assertEqual(set(list_tools()), {"define", "synonyms"})


class AgentTests(unittest.TestCase):
    def test_define_only(self):
        out = respond("define happy")
        names = [c["name"] for c in out["tool_calls"]]
        self.assertEqual(names, ["define"])

    def test_synonyms_only(self):
        out = respond("synonyms for sad")
        names = [c["name"] for c in out["tool_calls"]]
        self.assertEqual(names, ["synonyms"])

    def test_define_and_synonyms(self):
        out = respond("define and synonyms for code")
        names = [c["name"] for c in out["tool_calls"]]
        self.assertEqual(names, ["define", "synonyms"])
        self.assertLessEqual(len(out["tool_calls"]), 5)

    def test_no_word(self):
        out = respond("hello there")
        self.assertEqual(out["tool_calls"], [])

    def test_class_history(self):
        agent = DictionaryAgent()
        agent.chat("define test")
        self.assertEqual(len(agent.history), 2)


if __name__ == "__main__":
    unittest.main()
