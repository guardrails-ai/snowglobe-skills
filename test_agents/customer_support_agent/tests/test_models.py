import unittest

from customer_support_agent.models import Ticket, User, Message
from pydantic import ValidationError


class ModelTests(unittest.TestCase):
    def test_user(self):
        u = User(id=1, name="x", email="x@y.com")
        self.assertEqual(u.plan, "free")

    def test_ticket_priority(self):
        t = Ticket(id=1, user_id=1, subject="s", body="b")
        self.assertEqual(t.priority, "normal")

    def test_invalid_priority(self):
        with self.assertRaises(ValidationError):
            Ticket(id=1, user_id=1, subject="s", body="b", priority="banana")

    def test_message_roles(self):
        m = Message(role="user", content="hi")
        self.assertEqual(m.role, "user")
        with self.assertRaises(ValidationError):
            Message(role="server", content="x")


if __name__ == "__main__":
    unittest.main()
