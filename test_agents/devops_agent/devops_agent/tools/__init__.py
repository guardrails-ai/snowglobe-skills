from .status import get_status
from .deploy import deploy
from .rollback import rollback
from .logs import get_logs
from .scale import scale
from .restart import restart
from .healthcheck import healthcheck


def make_tools(config):
    return {
        "get_status":  {"fn": lambda service: get_status(config, service),
                         "description": "Get service status. Args: service."},
        "deploy":      {"fn": lambda service, version: deploy(config, service, version),
                         "description": "Deploy a version. Args: service, version."},
        "rollback":    {"fn": lambda service: rollback(config, service),
                         "description": "Rollback to previous. Args: service."},
        "get_logs":    {"fn": lambda service: get_logs(config, service),
                         "description": "Fetch recent logs. Args: service."},
        "scale":       {"fn": lambda service, instances: scale(config, service, instances),
                         "description": "Set instance count. Args: service, instances."},
        "restart":     {"fn": lambda service: restart(config, service),
                         "description": "Restart a service. Args: service."},
        "healthcheck": {"fn": lambda service=None: healthcheck(config, service),
                         "description": "Health check one or all. Args: service (optional)."},
    }


__all__ = [
    "get_status", "deploy", "rollback", "get_logs", "scale",
    "restart", "healthcheck", "make_tools",
]
