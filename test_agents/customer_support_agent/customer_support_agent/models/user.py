from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


class User(BaseModel):
    id: int
    name: str
    email: str
    plan: str = "free"
    preferences: Dict[str, str] = Field(default_factory=dict)
    interactions: List[str] = Field(default_factory=list)
