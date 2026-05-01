from __future__ import annotations

from typing import Any, Dict


def deploy(config, service: str, version: str) -> Dict[str, Any]:
    if service not in config.services:
        return {"ok": False, "error": f"unknown service '{service}'"}
    prev = config.services[service].get("version")
    config.deploy_history.append({"service": service, "from": prev, "to": version})
    config.services[service]["version"] = version
    return {"ok": True, "service": service, "from": prev, "to": version}
