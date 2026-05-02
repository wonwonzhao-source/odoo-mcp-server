"""Odoo XML-RPC client with authentication and error handling."""

import xmlrpc.client as xmlrpclib
from dataclasses import dataclass
from typing import Any, Optional

from .config import OdooConfig


@dataclass
class OdooUIDResult:
    """Result of uid authentication call."""
    uid: int
    name: str


class OdooClient:
    """Thread-safe Odoo XML-RPC client."""

    def __init__(self, config: OdooConfig):
        self.config = config
        self._uid: Optional[int] = None
        self._name: Optional[str] = None
        self._common: Optional[xmlrpclib.ServerProxy] = None
        self._models: Optional[xmlrpclib.ServerProxy] = None
        self._authenticated = False

    def _create_server_proxy(self, url: str) -> xmlrpclib.ServerProxy:
        """Create a ServerProxy with timeout support."""
        # Create transport with timeout
        transport = xmlrpclib.Transport()
        transport.timeout = self.config.timeout
        return xmlrpclib.ServerProxy(url, transport=transport)

    @property
    def common(self) -> xmlrpclib.ServerProxy:
        if self._common is None:
            self._common = self._create_server_proxy(
                f"{self.config.url}/xmlrpc/2/common"
            )
        return self._common

    @property
    def models(self) -> xmlrpclib.ServerProxy:
        if self._models is None:
            self._models = self._create_server_proxy(
                f"{self.config.url}/xmlrpc/2/object"
            )
        return self._models

    def authenticate(self) -> OdooUIDResult:
        """Authenticate with Odoo and store UID for subsequent calls."""
        try:
            result = self.common.authenticate(
                self.config.db,
                self.config.username,
                self.config.api_key,
                {}
            )
            if not isinstance(result, int):
                raise OdooAuthenticationError(
                    f"Authentication failed: {result}"
                )
            self._uid = result
            self._authenticated = True

            # Get user name for logging
            try:
                self._name = self.execute_kw(
                    "res.users", "read", [self._uid], {"fields": ["name"]}
                )[0].get("name", "Unknown")
            except Exception:
                self._name = self.config.username

            return OdooUIDResult(uid=self._uid, name=self._name)
        except xmlrpclib.Fault as e:
            raise OdooAuthenticationError(f"XML-RPC auth error: {e}")

    def ensure_authenticated(self):
        """Raise if not authenticated."""
        if not self._authenticated or self._uid is None:
            raise OdooAuthenticationError("Not authenticated. Call authenticate() first.")

    def execute_kw(self, model: str, method: str, args: list, kwargs: dict = None) -> Any:
        """Execute a method on a model.

        Args:
            model: Odoo model name (e.g., 'sale.order', 'stock.picking')
            method: Method name to call (e.g., 'search', 'read', 'write', 'create')
            args: Positional arguments for the method
            kwargs: Keyword arguments for the method

        Returns:
            Result of the method call
        """
        self.ensure_authenticated()
        kwargs = kwargs or {}
        try:
            return self.models.execute_kw(
                self.config.db,
                self._uid,
                self.config.api_key,
                model,
                method,
                args,
                kwargs
            )
        except xmlrpclib.Fault as e:
            raise OdooAPIError(f"execute_kw({model}.{method}) failed: {e}")

    def search_read(self, model: str, domain: list = None, fields: list = None,
                    offset: int = 0, limit: int = 100, order: str = None) -> list[dict]:
        """Search for records and return selected fields.

        Args:
            model: Odoo model name
            domain: Search domain (e.g., [('state', '=', 'done')])
            fields: Fields to return (None = all)
            offset: Number of records to skip
            limit: Maximum records to return
            order: Sort order (e.g., 'date desc')

        Returns:
            List of record dictionaries
        """
        domain = domain or []
        kwargs = {
            "domain": domain,
            "fields": fields or ["id"],
            "offset": offset,
            "limit": limit,
        }
        if order:
            kwargs["order"] = order
        return self.execute_kw(model, "search_read", [], kwargs)

    def create(self, model: str, values: dict) -> int:
        """Create a new record.

        Returns:
            ID of the created record
        """
        return self.execute_kw(model, "create", [values])

    def write(self, model: str, ids: list[int], values: dict) -> bool:
        """Update existing records.

        Returns:
            True if successful
        """
        return self.execute_kw(model, "write", [ids, values])

    def unlink(self, model: str, ids: list[int]) -> bool:
        """Delete records.

        Returns:
            True if successful
        """
        return self.execute_kw(model, "unlink", [ids])

    def call_method(self, model: str, method: str, args: list = None,
                    kwargs: dict = None) -> Any:
        """Call an arbitrary model method.

        Args:
            model: Odoo model name
            method: Method name to call
            args: Positional arguments
            kwargs: Keyword arguments

        Returns:
            Result of the method call
        """
        args = args or []
        kwargs = kwargs or {}
        return self.execute_kw(model, method, args, kwargs)

    def list_models(self, pattern: str = None) -> list[str]:
        """List available models, optionally filtered by pattern.

        Args:
            pattern: Substring filter (e.g., 'sale' returns 'sale.order', etc.)

        Returns:
            List of model names
        """
        # IrModel model contains all registered models
        domain = []
        if pattern:
            domain = [("model", "ilike", pattern)]
        records = self.search_read(
            "ir.model", domain, ["model"], limit=1000
        )
        return [r["model"] for r in records]

    def get_model_fields(self, model: str) -> list[dict]:
        """Get field definitions for a model.

        Returns:
            List of field definition dicts with name, type, required, etc.
        """
        result = self.call_method(
            model, "fields_get",
            kwargs={"attributes": ["string", "type", "required", "readonly", "help"]}
        )
        return [
            {"name": name, **attrs}
            for name, attrs in result.items()
        ]


class OdooAuthenticationError(Exception):
    """Raised when authentication with Odoo fails."""
    pass


class OdooAPIError(Exception):
    """Raised when an Odoo API call fails."""
    pass
