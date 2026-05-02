"""MCP server for Odoo ERP integration using FastMCP."""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .config import load_config, ServerConfig
from .client import OdooClient, OdooAuthenticationError, OdooAPIError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("odoo-mcp-server")


def create_server(config: ServerConfig) -> FastMCP:
    """Create and configure the MCP server using FastMCP."""
    
    # Create FastMCP server
    mcp = FastMCP(
        config.mcp.name,
        instructions=config.mcp.description,
    )
    
    # Create shared Odoo client
    odoo_client = OdooClient(config.odoo)
    
    def _ensure_authenticated():
        """Ensure Odoo client is authenticated."""
        if not odoo_client._authenticated:
            try:
                auth_result = odoo_client.authenticate()
                logger.info(f"Authenticated as: {auth_result.name} (UID: {auth_result.uid})")
            except OdooAuthenticationError as e:
                logger.error(f"Authentication failed: {e}")
                raise
    
    # -------------------------------------------------------------------------
    # Tool: search_read
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_search_read(
        model: str,
        domain: Optional[list] = None,
        fields: Optional[list] = None,
        offset: int = 0,
        limit: int = 100,
        order: Optional[str] = None,
    ) -> str:
        """Search for records in Odoo and return selected fields.
        
        Use this for querying data - equivalent to Odoo's search_read method.
        Supports filtering, sorting, pagination, and selecting specific fields.
        
        Args:
            model: Odoo model name (e.g., 'sale.order', 'stock.picking', 
                  'mrp.production', 'product.product')
            domain: Search domain as array of tuples, e.g. [['state', '=', 'done']]
            fields: List of field names to return
            offset: Number of records to skip (for pagination)
            limit: Maximum records to return (default 100, max 2000)
            order: Sort order, e.g. 'date_order desc'
        """
        try:
            _ensure_authenticated()
            results = odoo_client.search_read(
                model=model,
                domain=domain,
                fields=fields,
                offset=offset,
                limit=min(limit, 2000),
                order=order,
            )
            return json.dumps({"success": True, "count": len(results), "records": results})
        except (OdooAPIError, OdooAuthenticationError) as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: create
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_create(model: str, values: dict) -> str:
        """Create a new record in Odoo.
        
        Create new sales orders, purchase orders, manufacturing orders,
        products, partners, or any other Odoo record.
        
        Args:
            model: Odoo model name to create record in
            values: Field values for the new record as a dictionary
        """
        try:
            _ensure_authenticated()
            record_id = odoo_client.create(model, values)
            return json.dumps({"success": True, "id": record_id})
        except (OdooAPIError, OdooAuthenticationError) as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: write
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_write(model: str, ids: list, values: dict) -> str:
        """Update existing records in Odoo.
        
        Modify fields on existing records like updating order states,
        changing quantities, assigning users, etc.
        
        Args:
            model: Odoo model name
            ids: List of record IDs to update
            values: Field values to update
        """
        try:
            _ensure_authenticated()
            result = odoo_client.write(model, ids, values)
            return json.dumps({"success": True, "result": result})
        except (OdooAPIError, OdooAuthenticationError) as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: unlink
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_unlink(model: str, ids: list) -> str:
        """Delete records from Odoo.
        
        WARNING: This permanently removes records. Use with caution.
        
        Args:
            model: Odoo model name
            ids: List of record IDs to delete
        """
        try:
            _ensure_authenticated()
            result = odoo_client.unlink(model, ids)
            return json.dumps({"success": True, "result": result})
        except (OdooAPIError, OdooAuthenticationError) as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: call_method
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_call_method(
        model: str,
        method: str,
        args: Optional[list] = None,
        kwargs: Optional[dict] = None,
    ) -> str:
        """Call an arbitrary method on an Odoo model.
        
        Use for model-specific operations like confirming orders,
        validating invoices, transferring stock, etc.
        
        Args:
            model: Odoo model name
            method: Method name to call on the model
            args: Positional arguments for the method
            kwargs: Keyword arguments for the method
        """
        try:
            _ensure_authenticated()
            result = odoo_client.call_method(model, method, args, kwargs)
            return json.dumps({"success": True, "result": result})
        except (OdooAPIError, OdooAuthenticationError) as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: list_models
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_list_models(pattern: Optional[str] = None) -> str:
        """List all Odoo models available in the system.
        
        Discover what data is accessible. Optionally filter by name pattern.
        
        Args:
            pattern: Optional substring filter, e.g. 'sale' returns sale.order, etc.
        """
        try:
            _ensure_authenticated()
            models = odoo_client.list_models(pattern)
            return json.dumps({"success": True, "count": len(models), "models": models})
        except (OdooAPIError, OdooAuthenticationError) as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: get_model_fields
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_get_model_fields(model: str) -> str:
        """Get field definitions for an Odoo model.
        
        Returns field names, types, labels, and attributes.
        
        Args:
            model: Odoo model name (e.g., 'sale.order', 'product.template')
        """
        try:
            _ensure_authenticated()
            fields = odoo_client.get_model_fields(model)
            return json.dumps({"success": True, "count": len(fields), "fields": fields})
        except (OdooAPIError, OdooAuthenticationError) as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: get_version
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_get_version() -> str:
        """Get the Odoo server version information.
        
        Verify connectivity and get server details.
        """
        try:
            version = odoo_client.common.version()
            return json.dumps({"success": True, "version": version})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    # -------------------------------------------------------------------------
    # Tool: whoami
    # -------------------------------------------------------------------------
    @mcp.tool()
    def odoo_whoami() -> str:
        """Get information about the currently authenticated user.
        
        Verify which Odoo user account is being used for API calls.
        """
        try:
            _ensure_authenticated()
            user_data = odoo_client.execute_kw(
                "res.users", "read", [odoo_client._uid],
                {"fields": ["id", "name", "login", "email"]}
            )[0]
            return json.dumps({"success": True, "user": user_data})
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})

    return mcp


def main():
    """Main entry point for the MCP server."""
    # Load config from default locations
    config_path = None
    
    # Check common config locations
    for path in [
        Path("config.yaml"),
        Path.home() / ".config" / "odoo-mcp" / "config.yaml",
        Path(__file__).parent.parent.parent / "config.yaml",
    ]:
        if path.exists():
            config_path = str(path)
            break
    
    try:
        config = load_config(config_path)
        logger.info(f"Loaded config for Odoo: {config.odoo.url}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        print("Set ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_API_KEY environment variables.",
              file=sys.stderr)
        sys.exit(1)
    
    # Create and run server
    server = create_server(config)
    
    logger.info("Starting Odoo MCP server...")
    server.run()


if __name__ == "__main__":
    main()
