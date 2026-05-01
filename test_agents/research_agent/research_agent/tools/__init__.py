from .search import search
from .extract import extract_text
from .summarize import summarize_text
from .citations import save_citation
from .outline import build_outline
from .save import save_note


def make_tools(memory, llm):
    return {
        "search":         {"fn": lambda query: search(query),
                            "description": "Search a fixed corpus. Args: query."},
        "extract_text":   {"fn": lambda url: extract_text(url),
                            "description": "Extract text from a URL. Args: url."},
        "summarize_text": {"fn": lambda text, max_words=30: summarize_text(llm, text, max_words),
                            "description": "Summarize text. Args: text, max_words."},
        "save_citation":  {"fn": lambda title, url: save_citation(memory, title, url),
                            "description": "Save a citation. Args: title, url."},
        "build_outline":  {"fn": lambda topic, n=3: build_outline(llm, memory, topic, n),
                            "description": "Build an outline. Args: topic, n."},
        "save_note":      {"fn": lambda note: save_note(memory, note),
                            "description": "Save a research note. Args: note."},
    }


__all__ = [
    "search", "extract_text", "summarize_text",
    "save_citation", "build_outline", "save_note", "make_tools",
]
