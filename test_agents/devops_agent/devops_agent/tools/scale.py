from __future__ import annotations

from typing import Any, Dict


def scale(config, service: str, instances: int) -> Dict[str, Any]:
    if service not in config.services:
        return {"ok": False, "error": f"unknown service '{service}'"}
    if not isinstance(instances, int) or instances < 0:
        return {"ok": False, "error": "instances must be a non-negative int"}
    prev = config.services[service].get("instances")
    config.services[service]["instances"] = instances
    return {"ok": True, "service": service, "from": prev, "to": instances}
