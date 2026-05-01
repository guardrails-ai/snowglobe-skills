from __future__ import annotations

import re
from typing import Any, Dict


_EMAIL_RE = re.compile(r"^[\w\.\+\-]+@[\w\-]+\.[\w\.\-]+$")


def email_send(memory, to: str, subject: str, body: str) -> Dict[str, Any]:
    contact = memory.contacts.get(to)
    address = contact["email"] if contact else to
    if not _EMAIL_RE.match(address):
        return {"ok": False, "error": f"invalid email '{address}'"}
    msg = {"to": address, "subject": subject, "body": body}
    memory.sent_emails.append(msg)
    return {"ok": True, "email": msg}
