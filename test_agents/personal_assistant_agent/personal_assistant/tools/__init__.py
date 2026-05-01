from .calendar import calendar_add, calendar_list
from .email import email_send
from .weather import weather
from .reminders import reminder_add, reminder_list
from .search import web_search
from .calculator import calculate
from .notes import note_add, note_list
from .contacts import contact_add, contact_lookup
from .news import news_top
from .translate import translate


def make_tools(memory):
    return {
        "calendar":   {"fn": lambda title, when: calendar_add(memory, title, when),
                         "description": "Add calendar event."},
        "email":      {"fn": lambda to, subject, body: email_send(memory, to, subject, body),
                         "description": "Send email."},
        "weather":    {"fn": lambda city: weather(city),
                         "description": "Get weather (mocked)."},
        "reminders":  {"fn": lambda text, when: reminder_add(memory, text, when),
                         "description": "Add a reminder."},
        "search":     {"fn": lambda query: web_search(query),
                         "description": "Web search (mocked)."},
        "calculator": {"fn": lambda expression: calculate(expression),
                         "description": "Math expression."},
        "notes":      {"fn": lambda text: note_add(memory, text),
                         "description": "Add a note."},
        "contacts":   {"fn": lambda name, email=None: (contact_add(memory, name, email) if email else contact_lookup(memory, name)),
                         "description": "Lookup or add contact."},
        "news":       {"fn": lambda topic: news_top(topic),
                         "description": "Top news (mocked)."},
        "translate":  {"fn": lambda text, target_lang: translate(text, target_lang),
                         "description": "Translate text (mocked)."},
    }


__all__ = [
    "calendar_add", "calendar_list", "email_send", "weather", "reminder_add",
    "reminder_list", "web_search", "calculate", "note_add", "note_list",
    "contact_add", "contact_lookup", "news_top", "translate", "make_tools",
]
