from __future__ import annotations

from typing import Any, Dict


def get_status(config, service: str) -> Dict[str, Any]:
    if service not in config.services:
        return {"ok": False, "error": f"unknown service '{service}'"}
    return {"ok": True, "service": service, **config.services[service]}
