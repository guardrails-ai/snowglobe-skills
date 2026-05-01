"""Pattern-based intent recognizer for devops prompts."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Intent:
    action: str
    service: Optional[str] = None
    version: Optional[str] = None
    instances: Optional[int] = None


_STATUS = re.compile(r"^\s*status(?:\s+of)?\s+(\w+)\s*$", re.I)
_DEPLOY = re.compile(r"^\s*deploy\s+(\w+)\s+(?:to\s+)?(?:version\s+)?(\S+)\s*$", re.I)
_ROLLBACK = re.compile(r"^\s*rollback\s+(\w+)\s*$", re.I)
_LOGS = re.compile(r"^\s*logs?\s+(?:for\s+)?(\w+)\s*$", re.I)
_SCALE = re.compile(r"^\s*scale\s+(\w+)\s+(?:to\s+)?(\d+)\s*$", re.I)
_RESTART = re.compile(r"^\s*restart\s+(\w+)\s*$", re.I)
_HEALTH_ALL = re.compile(r"^\s*(?:health(?:check)?|check\s+health)\s*$", re.I)
_HEALTH_ONE = re.compile(r"^\s*(?:health(?:check)?|check\s+health)\s+(\w+)\s*$", re.I)


def parse(text: str) -> Intent:
    if (m := _STATUS.match(text)):
        return Intent("status", service=m.group(1))
    if (m := _DEPLOY.match(text)):
        return Intent("deploy", service=m.group(1), version=m.group(2))
    if (m := _ROLLBACK.match(text)):
        return Intent("rollback", service=m.group(1))
    if (m := _LOGS.match(text)):
        return Intent("logs", service=m.group(1))
    if (m := _SCALE.match(text)):
        return Intent("scale", service=m.group(1), instances=int(m.group(2)))
    if (m := _RESTART.match(text)):
        return Intent("restart", service=m.group(1))
    if (m := _HEALTH_ONE.match(text)):
        return Intent("healthcheck", service=m.group(1))
    if _HEALTH_ALL.match(text):
        return Intent("healthcheck_all")
    return Intent("noop")
