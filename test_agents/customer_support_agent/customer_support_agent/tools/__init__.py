from .lookup import lookup_user
from .history import view_history
from .ticket import create_ticket
from .escalate import escalate
from .email import send_email
from .refund import refund
from .preferences import update_preferences
from .faq import faq_search


def make_tools(store):
    return {
        "lookup_user":         {"fn": lambda user_id: lookup_user(store, user_id),
                                  "description": "Look up a user. Args: user_id."},
        "view_history":        {"fn": lambda user_id: view_history(store, user_id),
                                  "description": "Recent interactions. Args: user_id."},
        "create_ticket":       {"fn": lambda user_id, subject, body, priority="normal": create_ticket(store, user_id, subject, body, priority),
                                  "description": "Create support ticket."},
        "escalate":            {"fn": lambda ticket_id: escalate(store, ticket_id),
                                  "description": "Escalate ticket. Args: ticket_id."},
        "send_email":          {"fn": lambda user_id, subject, body: send_email(store, user_id, subject, body),
                                  "description": "Send email. Args: user_id, subject, body."},
        "refund":              {"fn": lambda user_id, amount: refund(store, user_id, amount),
                                  "description": "Issue a refund. Args: user_id, amount."},
        "update_preferences":  {"fn": lambda user_id, key, value: update_preferences(store, user_id, key, value),
                                  "description": "Update one preference."},
        "faq_search":          {"fn": lambda query: faq_search(query),
                                  "description": "Search the FAQ. Args: query."},
    }


__all__ = [
    "lookup_user", "view_history", "create_ticket", "escalate",
    "send_email", "refund", "update_preferences", "faq_search", "make_tools",
]
