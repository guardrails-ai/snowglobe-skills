import unittest

from customer_support_agent import seed_store
from customer_support_agent.tools import (
    lookup_user, view_history, create_ticket, escalate,
    send_email, refund, update_preferences, faq_search,
)


class ToolTests(unittest.TestCase):
    def setUp(self):
        self.store = seed_store()

    def test_lookup(self):
        self.assertTrue(lookup_user(self.store, 1)["ok"])
        self.assertFalse(lookup_user(self.store, 99)["ok"])

    def test_history(self):
        out = view_history(self.store, 1)
        self.assertGreater(len(out["interactions"]), 0)

    def test_create_ticket(self):
        out = create_ticket(self.store, 1, "subj", "body")
        self.assertTrue(out["ok"])

    def test_create_ticket_bad_priority(self):
        out = create_ticket(self.store, 1, "subj", "body", "weird")
        self.assertFalse(out["ok"])

    def test_escalate(self):
        out = escalate(self.store, 1)
        self.assertTrue(out["ok"])
        self.assertEqual(self.store.tickets[1].status, "escalated")

    def test_email(self):
        out = send_email(self.store, 1, "s", "b")
        self.assertTrue(out["ok"])
        self.assertEqual(len(self.store.sent_emails), 1)

    def test_refund(self):
        self.assertTrue(refund(self.store, 1, 10.0)["ok"])
        self.assertFalse(refund(self.store, 1, -1)["ok"])

    def test_prefs(self):
        out = update_preferences(self.store, 2, "theme", "dark")
        self.assertTrue(out["ok"])
        self.assertEqual(self.store.users[2].preferences["theme"], "dark")

    def test_faq(self):
        out = faq_search("password")
        self.assertTrue(out["ok"])
        self.assertGreater(len(out["results"]), 0)


if __name__ == "__main__":
    unittest.main()
