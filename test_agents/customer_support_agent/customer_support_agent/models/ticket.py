from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


Priority = Literal["low", "normal", "high", "urgent"]
Status = Literal["open", "escalated", "resolved", "closed"]


class Ticket(BaseModel):
    id: int
    user_id: int
    subject: str
    body: str
    priority: Priority = "normal"
    status: Status = "open"
