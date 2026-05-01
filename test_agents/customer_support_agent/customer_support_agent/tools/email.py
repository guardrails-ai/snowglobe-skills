from __future__ import annotations

from typing import Any, Dict


def send_email(store, user_id: int, subject: str, body: str) -> Dict[str, Any]:
    user = store.users.get(user_id)
    if not user:
        return {"ok": False, "error": f"no user with id {user_id}"}
    msg = {"to": user.email, "subject": subject, "body": body}
    store.sent_emails.append(msg)
    return {"ok": True, "email": msg}
