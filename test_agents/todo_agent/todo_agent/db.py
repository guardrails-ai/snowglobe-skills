"""SQLite-backed todo database."""
from __future__ import annotations

import sqlite3
from typing import List, Optional

from .models import Todo


SCHEMA = """
CREATE TABLE IF NOT EXISTS todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);
"""


class Database:
    def __init__(self, path: str = ":memory:") -> None:
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute(SCHEMA)

    def add(self, text: str) -> Todo:
        cur = self.conn.execute("INSERT INTO todos (text) VALUES (?)", (text,))
        self.conn.commit()
        return Todo(id=cur.lastrowid, text=text, done=False)

    def list(self, include_done: bool = True) -> List[Todo]:
        if include_done:
            rows = self.conn.execute("SELECT id, text, done FROM todos ORDER BY id").fetchall()
        else:
            rows = self.conn.execute("SELECT id, text, done FROM todos WHERE done = 0 ORDER BY id").fetchall()
        return [Todo(id=r["id"], text=r["text"], done=bool(r["done"])) for r in rows]

    def get(self, todo_id: int) -> Optional[Todo]:
        row = self.conn.execute("SELECT id, text, done FROM todos WHERE id = ?", (todo_id,)).fetchone()
        if not row:
            return None
        return Todo(id=row["id"], text=row["text"], done=bool(row["done"]))

    def complete(self, todo_id: int) -> bool:
        cur = self.conn.execute("UPDATE todos SET done = 1 WHERE id = ?", (todo_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def delete(self, todo_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        self.conn.commit()
        return cur.rowcount > 0

    def close(self) -> None:
        self.conn.close()
