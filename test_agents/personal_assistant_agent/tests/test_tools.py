import unittest

from personal_assistant import Memory
from personal_assistant.tools import (
    calendar_add, calendar_list, email_send, weather, reminder_add, reminder_list,
    web_search, calculate, note_add, note_list, contact_add, contact_lookup, news_top, translate,
)


class ToolTests(unittest.TestCase):
    def test_calendar(self):
        m = Memory()
        out = calendar_add(m, "lunch", "tomorrow noon")
        self.assertTrue(out["ok"])
        self.assertEqual(len(calendar_list(m)["events"]), 1)

    def test_email_invalid(self):
        m = Memory()
        out = email_send(m, "not-an-email", "s", "b")
        self.assertFalse(out["ok"])

    def test_email_valid(self):
        m = Memory()
        out = email_send(m, "x@y.com", "s", "b")
        self.assertTrue(out["ok"])

    def test_weather(self):
        self.assertTrue(weather("tokyo")["ok"])
        self.assertFalse(weather("atlantis")["ok"])

    def test_reminders(self):
        m = Memory()
        out = reminder_add(m, "call mom", "5pm")
        self.assertTrue(out["ok"])
        self.assertEqual(len(reminder_list(m)["reminders"]), 1)

    def test_search(self):
        self.assertTrue(web_search("python")["ok"])
        self.assertFalse(web_search("")["ok"])

    def test_calculator(self):
        self.assertEqual(calculate("2 + 2")["result"], 4.0)
        self.assertFalse(calculate("foo()")["ok"])

    def test_notes(self):
        m = Memory()
        note_add(m, "buy bread")
        self.assertEqual(len(note_list(m)["notes"]), 1)

    def test_contacts(self):
        m = Memory()
        contact_add(m, "alice", "alice@example.com")
        out = contact_lookup(m, "alice")
        self.assertTrue(out["ok"])
        self.assertEqual(out["contact"]["email"], "alice@example.com")

    def test_news(self):
        self.assertTrue(news_top("ai")["ok"])

    def test_translate(self):
        out = translate("hello", "spanish")
        self.assertEqual(out["translation"], "hola")


if __name__ == "__main__":
    unittest.main()
