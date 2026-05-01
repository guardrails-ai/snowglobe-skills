import unittest

from personal_assistant import PersonalAssistant, Memory, respond


class AgentTests(unittest.TestCase):
    def test_weather(self):
        a = PersonalAssistant()
        out = a.chat("weather in tokyo")
        self.assertIn("Tokyo", out)

    def test_calendar(self):
        a = PersonalAssistant()
        out = a.chat("schedule lunch")
        self.assertIn("event", out)

    def test_email_with_contact(self):
        a = PersonalAssistant()
        a.chat("add contact alice alice@example.com")
        out = a.chat("email alice: hi // there")
        self.assertIn("sent", out)

    def test_calculate(self):
        a = PersonalAssistant()
        out = a.chat("calculate 7 * 6")
        self.assertIn("42", out)

    def test_note(self):
        a = PersonalAssistant()
        out = a.chat("note: buy milk")
        self.assertIn("saved", out)

    def test_contact_lookup(self):
        a = PersonalAssistant()
        a.chat("add contact bob bob@example.com")
        out = a.chat("contact bob")
        self.assertIn("bob@example.com", out)

    def test_news(self):
        a = PersonalAssistant()
        out = a.chat("news about ai")
        self.assertIn("headline", out)

    def test_translate(self):
        a = PersonalAssistant()
        out = a.chat("translate hello to spanish")
        self.assertIn("hola", out)

    def test_reminder(self):
        a = PersonalAssistant()
        out = a.chat("remind me to call mom at 5pm")
        self.assertIn("reminder", out)

    def test_search(self):
        a = PersonalAssistant()
        out = a.chat("search python")
        self.assertIn("hit", out)

    def test_plan_morning_caps_at_5(self):
        out = respond("plan my morning in tokyo", Memory())
        self.assertEqual(len(out["tool_calls"]), 5)

    def test_unknown(self):
        a = PersonalAssistant()
        out = a.chat("hi how are you")
        self.assertIn("translate", out)


if __name__ == "__main__":
    unittest.main()
