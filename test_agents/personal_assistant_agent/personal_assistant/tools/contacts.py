from __future__ import annotations

from typing import Any, Dict


def contact_add(memory, name: str, email: str) -> Dict[str, Any]:
    if not name or not email:
        return {"ok": False, "error": "name and email required"}
    memory.contacts[name] = {"email": email}
    return {"ok": True, "contact": {"name": name, "email": email}}


def contact_lookup(memory, name: str) -> Dict[str, Any]:
    c = memory.contacts.get(name)
    if not c:
        return {"ok": False, "error": f"no contact named '{name}'"}
    return {"ok": True, "contact": {"name": name, **c}}
