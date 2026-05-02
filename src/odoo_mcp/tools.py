"""MCP tool definitions for Odoo ERP operations."""

import json
from typing import Any, Optional

from mcp.types import Tool

from .client import OdooClient, OdooAuthenticationError, OdooAPIError


def create_mcp_tools(client: OdooClient) -> list[Tool]:
    """Create all MCP tools for Odoo operations."""

    return [
        Tool(
            name="odoo_search_read",
            description="Search for records in Odoo and return selected fields. "
                       "Use this for querying data - equivalent to Odoo's search_read method. "
                       "Supports filtering, sorting, pagination, and selecting specific fields.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name (e.g., 'sale.order', 'stock.picking', "
                                     "'mrp.production', 'product.product'). "
                                     "Use list_models to discover available models."
                    },
                    "domain": {
                        "type": "array",
                        "description": "Search domain/filter as array of tuples. "
                                     "Example: [['state', '=', 'done'], ['date', '>=', '2024-01-01']] "
                                     "Common operators: =, !=, <, >, <=, >=, ilike, like, in, not in, "
                                     "child_of, parent_left, parent_right"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of field names to return. "
                                     "Example: ['id', 'name', 'state', 'date_order', 'amount_total']"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of records to skip (for pagination). Default: 0"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum records to return. Default: 100, Max: 2000"
                    },
                    "order": {
                        "type": "string",
                        "description": "Sort order. Example: 'date_order desc', 'name asc'"
                    }
                },
                "required": ["model"]
            }
        ),

        Tool(
            name="odoo_create",
            description="Create a new record in Odoo. "
                       "Use this to create new sales orders, purchase orders, manufacturing orders, "
                       "products, partners, or any other Odoo record. "
                       "Returns the ID of the newly created record.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name to create record in"
                    },
                    "values": {
                        "type": "object",
                        "description": "Field values for the new record as a dictionary. "
                                     "Example: {'name': 'SO001', 'partner_id': 5, 'date_order': '2024-01-15'}"
                    }
                },
                "required": ["model", "values"]
            }
        ),

        Tool(
            name="odoo_write",
            description="Update existing records in Odoo. "
                       "Use this to modify fields on existing records like updating order states, "
                       "changing quantities, assigning users, etc. "
                       "Returns true if successful.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of record IDs to update"
                    },
                    "values": {
                        "type": "object",
                        "description": "Field values to update. "
                                     "Example: {'state': 'done', 'date_done': '2024-01-15'}"
                    }
                },
                "required": ["model", "ids", "values"]
            }
        ),

        Tool(
            name="odoo_unlink",
            description="Delete records from Odoo. "
                       "WARNING: This permanently removes records. Use with caution. "
                       "Typically only used for cleaning up test data or drafts.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of record IDs to delete"
                    }
                },
                "required": ["model", "ids"]
            }
        ),

        Tool(
            name="odoo_call_method",
            description="Call an arbitrary method on an Odoo model. "
                       "Use this for model-specific operations like confirming orders, "
                       "validating invoices, transferring stock, etc. "
                       "Requires knowledge of the model's custom methods.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name"
                    },
                    "method": {
                        "type": "string",
                        "description": "Method name to call on the model"
                    },
                    "args": {
                        "type": "array",
                        "description": "Positional arguments for the method"
                    },
                    "kwargs": {
                        "type": "object",
                        "description": "Keyword arguments for the method"
                    }
                },
                "required": ["model", "method"]
            }
        ),

        Tool(
            name="odoo_list_models",
            description="List all Odoo models (data tables) available in the system. "
                       "Use this to discover what data is accessible. "
                       "Optionally filter by name pattern.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Optional substring filter. "
                                     "Example: 'sale' returns sale.order, sale.order.line, etc."
                    }
                }
            }
        ),

        Tool(
            name="odoo_get_model_fields",
            description="Get field definitions for an Odoo model. "
                       "Returns field names, types, labels, and attributes. "
                       "Use this to understand what data can be queried or set on a model.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "Odoo model name (e.g., 'sale.order', 'product.template')"
                    }
                },
                "required": ["model"]
            }
        ),

        Tool(
            name="odoo_get_version",
            description="Get the Odoo server version information. "
                       "Use this to verify connectivity and get server details.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="odoo_whoami",
            description="Get information about the currently authenticated user. "
                       "Use this to verify which Odoo user account is being used for API calls.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
    ]


# Tool handlers - map tool names to callable functions

async def handle_search_read(client: OdooClient, model: str,
                             domain: Optional[list] = None, fields: Optional[list] = None,
                             offset: int = 0, limit: int = 100,
                             order: Optional[str] = None) -> str:
    """Handle odoo_search_read tool call."""
    try:
        results = client.search_read(
            model=model,
            domain=domain,
            fields=fields,
            offset=offset,
            limit=min(limit, 2000),  # Cap at 2000
            order=order
        )
        return json.dumps({"success": True, "count": len(results), "records": results})
    except OdooAPIError as e:
        return json.dumps({"success": False, "error": str(e)})
    except OdooAuthenticationError as e:
        return json.dumps({"success": False, "error": f"Authentication error: {e}"})


async def handle_create(client: OdooClient, model: str, values: dict) -> str:
    """Handle odoo_create tool call."""
    try:
        record_id = client.create(model, values)
        return json.dumps({"success": True, "id": record_id})
    except OdooAPIError as e:
        return json.dumps({"success": False, "error": str(e)})


async def handle_write(client: OdooClient, model: str, ids: list,
                       values: dict) -> str:
    """Handle odoo_write tool call."""
    try:
        result = client.write(model, ids, values)
        return json.dumps({"success": True, "result": result})
    except OdooAPIError as e:
        return json.dumps({"success": False, "error": str(e)})


async def handle_unlink(client: OdooClient, model: str, ids: list) -> str:
    """Handle odoo_unlink tool call."""
    try:
        result = client.unlink(model, ids)
        return json.dumps({"success": True, "result": result})
    except OdooAPIError as e:
        return json.dumps({"success": False, "error": str(e)})


async def handle_call_method(client: OdooClient, model: str, method: str,
                             args: Optional[list] = None, kwargs: Optional[dict] = None) -> str:
    """Handle odoo_call_method tool call."""
    try:
        result = client.call_method(model, method, args, kwargs)
        return json.dumps({"success": True, "result": result})
    except OdooAPIError as e:
        return json.dumps({"success": False, "error": str(e)})


async def handle_list_models(client: OdooClient, pattern: Optional[str] = None) -> str:
    """Handle odoo_list_models tool call."""
    try:
        models = client.list_models(pattern)
        return json.dumps({"success": True, "count": len(models), "models": models})
    except OdooAPIError as e:
        return json.dumps({"success": False, "error": str(e)})


async def handle_get_model_fields(client: OdooClient, model: str) -> str:
    """Handle odoo_get_model_fields tool call."""
    try:
        fields = client.get_model_fields(model)
        return json.dumps({"success": True, "count": len(fields), "fields": fields})
    except OdooAPIError as e:
        return json.dumps({"success": False, "error": str(e)})


async def handle_get_version(client: OdooClient) -> str:
    """Handle odoo_get_version tool call."""
    try:
        version = client.common.version()
        return json.dumps({"success": True, "version": version})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


async def handle_whoami(client: OdooClient) -> str:
    """Handle odoo_whoami tool call."""
    try:
        client.ensure_authenticated()
        user_data = client.execute_kw(
            "res.users", "read", [client._uid],
            {"fields": ["id", "name", "login", "email"]}
        )[0]
        return json.dumps({"success": True, "user": user_data})
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})


# Dispatch table
TOOL_HANDLERS = {
    "odoo_search_read": handle_search_read,
    "odoo_create": handle_create,
    "odoo_write": handle_write,
    "odoo_unlink": handle_unlink,
    "odoo_call_method": handle_call_method,
    "odoo_list_models": handle_list_models,
    "odoo_get_model_fields": handle_get_model_fields,
    "odoo_get_version": handle_get_version,
    "odoo_whoami": handle_whoami,
}
