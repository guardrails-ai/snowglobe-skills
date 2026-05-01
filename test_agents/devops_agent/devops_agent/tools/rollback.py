from __future__ import annotations

from typing import Any, Dict


def rollback(config, service: str) -> Dict[str, Any]:
    if service not in config.services:
        return {"ok": False, "error": f"unknown service '{service}'"}
    history = [h for h in config.deploy_history if h["service"] == service and h["from"] is not None]
    if not history:
        return {"ok": False, "error": "no deploys to roll back"}
    last = history[-1]
    config.services[service]["version"] = last["from"]
    return {"ok": True, "service": service, "rolled_back_to": last["from"]}
