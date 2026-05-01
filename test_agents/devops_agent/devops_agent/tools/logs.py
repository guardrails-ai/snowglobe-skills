from __future__ import annotations

from typing import Any, Dict


def get_logs(config, service: str) -> Dict[str, Any]:
    if service not in config.services:
        return {"ok": False, "error": f"unknown service '{service}'"}
    fake = [
        f"[INFO] {service} started",
        f"[INFO] {service} processed request",
        f"[WARN] {service} retry triggered",
    ]
    return {"ok": True, "service": service, "lines": fake}
