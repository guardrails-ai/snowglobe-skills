"""Mutable in-memory store seeded with demo data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .models import Ticket, User


@dataclass
class Store:
    users: Dict[int, User] = field(default_factory=dict)
    tickets: Dict[int, Ticket] = field(default_factory=dict)
    sent_emails: List[Dict[str, str]] = field(default_factory=list)
    refunds: List[Dict[str, object]] = field(default_factory=list)
    next_ticket_id: int = 1

    def create_ticket(self, user_id: int, subject: str, body: str, priority: str = "normal") -> Ticket:
        t = Ticket(id=self.next_ticket_id, user_id=user_id, subject=subject, body=body, priority=priority)
        self.tickets[t.id] = t
        self.next_ticket_id += 1
        return t


FAQ: Dict[str, str] = {
    "reset password": "Click 'forgot password' on the login page; we will email you a reset link.",
    "cancel subscription": "Open Settings -> Billing -> Cancel. Cancellation takes effect at the next billing cycle.",
    "refund": "Refunds are processed within 5-7 business days to the original payment method.",
    "invoice": "Invoices live under Settings -> Billing -> Invoices.",
    "contact": "You can reach us 24/7 at support@example.com.",
}


def seed_store() -> Store:
    store = Store()
    store.users[1] = User(id=1, name="Ada", email="ada@example.com", plan="pro",
                          preferences={"newsletter": "weekly"},
                          interactions=["asked about billing", "downgraded plan"])
    store.users[2] = User(id=2, name="Bob", email="bob@example.com", plan="free",
                          preferences={}, interactions=["created account"])
    store.create_ticket(1, "billing question", "I was charged twice", priority="high")
    return store
