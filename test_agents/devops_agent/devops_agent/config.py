"""YAML-backed mutable service registry."""
from __future__ import annotations

import copy
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import yaml


@dataclass
class Config:
    services: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    deploy_history: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_file(cls, path: str) -> "Config":
        with open(path, "r") as fh:
            data = yaml.safe_load(fh) or {}
        return cls(services=data.get("services", {}))

    @classmethod
    def from_string(cls, yaml_text: str) -> "Config":
        data = yaml.safe_load(yaml_text) or {}
        return cls(services=data.get("services", {}))

    @classmethod
    def default(cls) -> "Config":
        here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(here, "config.yaml")
        if os.path.exists(path):
            return cls.from_file(path)
        return cls()

    def snapshot(self) -> Dict[str, Dict[str, Any]]:
        return copy.deepcopy(self.services)

    def list_services(self) -> List[str]:
        return list(self.services.keys())
