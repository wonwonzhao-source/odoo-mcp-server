"""Standalone entry point for PyInstaller builds (Windows/macOS executables)."""

import sys
import os

# Add src to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from odoo_mcp.server import main

if __name__ == "__main__":
    main()
