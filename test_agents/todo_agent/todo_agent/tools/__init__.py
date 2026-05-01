from .create import add_todo
from .list import list_todos
from .complete import complete_todo
from .delete import delete_todo


def make_tools(db):
    return {
        "add_todo": {
            "fn": lambda text: add_todo(db, text),
            "description": "Add a todo. Args: text (str).",
        },
        "list_todos": {
            "fn": lambda include_done=True: list_todos(db, include_done),
            "description": "List todos. Args: include_done (bool).",
        },
        "complete_todo": {
            "fn": lambda todo_id: complete_todo(db, todo_id),
            "description": "Mark todo done. Args: todo_id (int).",
        },
        "delete_todo": {
            "fn": lambda todo_id: delete_todo(db, todo_id),
            "description": "Delete a todo. Args: todo_id (int).",
        },
    }


__all__ = ["add_todo", "list_todos", "complete_todo", "delete_todo", "make_tools"]
