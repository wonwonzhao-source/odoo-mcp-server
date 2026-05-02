"""Configuration management for Odoo MCP server."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class OdooConfig:
    url: str
    db: str
    username: str
    api_key: str
    timeout: int = 30
    debug: bool = False


@dataclass
class MCPConfig:
    name: str = "odoo"
    description: str = "Interact with Odoo ERP"
    enabled_tools: list[str] = field(default_factory=lambda: [
        "search_read", "create", "write", "unlink",
        "call_method", "list_models", "get_model_fields"
    ])


@dataclass
class ServerConfig:
    odoo: OdooConfig
    mcp: MCPConfig = field(default_factory=MCPConfig)


def load_config(config_path: Optional[str] = None) -> ServerConfig:
    """Load configuration from YAML file and environment variables.

    Environment variables take precedence over config file values.
    Supports ${ENV_VAR} syntax in config file for secret injection.
    """
    config_data = {}

    if config_path and Path(config_path).exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}

    odoo_data = config_data.get("odoo", {})
    mcp_data = config_data.get("mcp", {})

    # Helper to resolve ${ENV_VAR} syntax
    def resolve(val):
        if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
            env_var = val[2:-1]
            return os.environ.get(env_var, "")
        return val

    # Resolve environment variables in odoo config
    odoo_config = OdooConfig(
        url=os.environ.get("ODOO_URL", resolve(odoo_data.get("url", ""))),
        db=os.environ.get("ODOO_DB", resolve(odoo_data.get("db", ""))),
        username=os.environ.get("ODOO_USERNAME", resolve(odoo_data.get("username", ""))),
        api_key=os.environ.get("ODOO_API_KEY", resolve(odoo_data.get("api_key", ""))),
        timeout=int(os.environ.get("ODOO_TIMEOUT", odoo_data.get("timeout", 30))),
        debug=bool(os.environ.get("ODOO_DEBUG", odoo_data.get("debug", False))),
    )

    # Validate required fields
    for field_name in ["url", "db", "username", "api_key"]:
        if not getattr(odoo_config, field_name):
            raise ValueError(f"Odoo config field '{field_name}' is required. "
                           f"Set via environment variable or config file.")

    mcp_config = MCPConfig(
        name=mcp_data.get("name", "odoo"),
        description=mcp_data.get("description", "Interact with Odoo ERP"),
        enabled_tools=mcp_data.get("enabled_tools", [
            "search_read", "create", "write", "unlink",
            "call_method", "list_models", "get_model_fields"
        ]),
    )

    return ServerConfig(odoo=odoo_config, mcp=mcp_config)
