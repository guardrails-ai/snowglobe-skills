from __future__ import annotations

from typing import Any, Dict


def restart(config, service: str) -> Dict[str, Any]:
    if service not in config.services:
        return {"ok": False, "error": f"unknown service '{service}'"}
    config.services[service]["healthy"] = True
    return {"ok": True, "service": service, "restarted": True}
