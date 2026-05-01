import unittest

from customer_support_agent import CustomerSupportAgent, seed_store, respond


class AgentTests(unittest.TestCase):
    def test_lookup(self):
        a = CustomerSupportAgent()
        out = a.chat("lookup user 1")
        self.assertIn("Ada", out)

    def test_history(self):
        a = CustomerSupportAgent()
        out = a.chat("history for user 1")
        self.assertIn("interactions", out)

    def test_create_ticket_chain(self):
        a = CustomerSupportAgent()
        out = a.chat("create ticket for user 1: charged twice // I was billed twice")
        self.assertIn("created ticket", out)
        self.assertEqual(len(a.store.sent_emails), 1)

    def test_escalate(self):
        a = CustomerSupportAgent()
        out = a.chat("escalate ticket 1")
        self.assertIn("escalated", out)

    def test_email(self):
        a = CustomerSupportAgent()
        out = a.chat("email user 1: hello // there")
        self.assertIn("sent", out)

    def test_refund(self):
        a = CustomerSupportAgent()
        out = a.chat("refund user 1 25.50")
        self.assertIn("refunded", out)

    def test_pref(self):
        a = CustomerSupportAgent()
        out = a.chat("set preference for user 1 theme = dark")
        self.assertIn("updated", out)

    def test_faq(self):
        a = CustomerSupportAgent()
        out = a.chat("faq password")
        self.assertIn("faq", out)

    def test_unknown(self):
        a = CustomerSupportAgent()
        out = a.chat("hello")
        self.assertIn("FAQ", out)

    def test_max_5_calls(self):
        out = respond("create ticket for user 1: x // y", seed_store())
        self.assertLessEqual(len(out["tool_calls"]), 5)


if __name__ == "__main__":
    unittest.main()
