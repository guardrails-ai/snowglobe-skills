from __future__ import annotations

from typing import Any, Dict, Optional


def healthcheck(config, service: Optional[str] = None) -> Dict[str, Any]:
    if service is None:
        return {"ok": True, "results": {s: cfg.get("healthy", False) for s, cfg in config.services.items()}}
    if service not in config.services:
        return {"ok": False, "error": f"unknown service '{service}'"}
    return {"ok": True, "service": service, "healthy": config.services[service].get("healthy", False)}
