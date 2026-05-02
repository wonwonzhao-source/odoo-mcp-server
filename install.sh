#!/bin/bash
#
# Odoo MCP Server - Installer for Hermes Agent
# Run this script to install the Odoo MCP Server
#

set -e

echo "================================================"
echo "  Odoo MCP Server Installer for Hermes Agent"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect Python
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo -e "${RED}Error: Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

echo "Using: $PYTHON ($($PYTHON --version))"
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$SCRIPT_DIR"
VENV_DIR="${VENV_DIR:-$HOME/.hermes/hermes-agent/venv}"

echo "Package location: $PACKAGE_DIR"
echo "Target venv: $VENV_DIR"
echo ""

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Warning: Hermes venv not found at $VENV_DIR${NC}"
    echo "Will try to install to local Python environment instead."
    VENV_DIR=""
fi

# Install the package
echo -e "${GREEN}[1/4] Installing Odoo MCP Server package...${NC}"
if [ -n "$VENV_DIR" ]; then
    "$VENV_DIR/bin/pip" install -e "$PACKAGE_DIR" --quiet
    ODOO_MCP_CMD="$VENV_DIR/bin/odoo-mcp"
else
    "$PYTHON" -m pip install -e "$PACKAGE_DIR" --user --quiet 2>/dev/null || sudo "$PYTHON" -m pip install -e "$PACKAGE_DIR" --quiet
    ODOO_MCP_CMD="$HOME/.local/bin/odoo-mcp"
fi
echo "  Installed odoo-mcp command"

# Verify installation
echo -e "${GREEN}[2/4] Verifying installation...${NC}"
if command -v odoo-mcp &> /dev/null; then
    echo "  Command 'odoo-mcp' is available"
elif [ -f "$ODOO_MCP_CMD" ]; then
    echo "  Command installed at: $ODOO_MCP_CMD"
else
    echo -e "${YELLOW}  Warning: Command not in PATH. Manual setup may be needed.${NC}"
fi

# Create config template
echo -e "${GREEN}[3/4] Creating config template...${NC}"
CONFIG_DIR="$HOME/.config/odoo-mcp"
mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    cat > "$CONFIG_DIR/config.yaml" << 'CONFIG_EOF'
# Odoo MCP Server Configuration
# Copy this to your Hermes config.yaml or set environment variables

odoo:
  url: "https://YOUR_INSTANCE.odoo.com"
  db: "YOUR_DATABASE_NAME"
  username: "your@email.com"
  # api_key from Odoo: Settings > Users > API Key > Generate
  api_key: "YOUR_API_KEY_HERE"
  timeout: 30
  debug: false

mcp:
  name: "odoo"
  description: "Interact with Odoo ERP for manufacturing operations"
CONFIG_EOF
    echo "  Created config template at: $CONFIG_DIR/config.yaml"
    echo "  Please edit this file with your Odoo credentials!"
else
    echo "  Config already exists at: $CONFIG_DIR/config.yaml"
fi

# Show Hermes config snippet
echo -e "${GREEN}[4/4] Hermes Agent Configuration${NC}"
echo ""
echo "Add this to your ~/.hermes/config.yaml:"
echo ""
echo "  mcp_servers:"
echo "    odoo:"
echo '      command: "/HOME/.hermes/hermes-agent/venv/bin/odoo-mcp"'
echo "      env:"
echo '        ODOO_URL: "https://YOUR_INSTANCE.odoo.com"'
echo '        ODOO_DB: "YOUR_DATABASE_NAME"'
echo '        ODOO_USERNAME: "your@email.com"'
echo '        ODOO_API_KEY: "YOUR_API_KEY"'
echo ""

# Test connection (optional)
echo "================================================"
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit $CONFIG_DIR/config.yaml with your Odoo credentials"
echo "  2. Add mcp_servers.odoo section to ~/.hermes/config.yaml"
echo "  3. Restart Hermes Agent"
echo ""
echo "To test manually:"
echo "  export ODOO_URL='https://your-instance.odoo.com'"
echo "  export ODOO_DB='your-database'"
echo "  export ODOO_USERNAME='your@email.com'"
echo "  export ODOO_API_KEY='your-api-key'"
echo "  odoo-mcp"
echo ""
