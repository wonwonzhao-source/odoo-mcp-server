@echo off
setlocal

echo ================================================
echo   Odoo MCP Server - Windows Installer
echo ================================================
echo.
echo This script installs from source (Python required).
echo.
echo For the standalone .exe (no Python needed), download from:
echo   https://github.com/wonwonzhao-source/odoo-mcp-server/releases
echo.
echo Press any key to continue or Ctrl+C to exit...
pause > nul

echo.
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Please install Python 3.10+ from https://python.org
    echo Then run this script again.
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Odoo MCP Server...
pip install -e .
if errorlevel 1 (
    echo ERROR: pip install failed. Try running as Administrator.
    pause
    exit /b 1
)

echo.
echo [3/3] Creating config file...
set CONFIG_DIR=%USERPROFILE%\.config\odoo-mcp
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

if not exist "%CONFIG_DIR%\config.yaml" (
    (
        echo # Odoo MCP Server Configuration
        echo odoo:
        echo   url: "https://YOUR_INSTANCE.odoo.com"
        echo   db: "YOUR_DATABASE_NAME"
        echo   username: "your^@email.com"
        echo   api_key: "YOUR_API_KEY"
        echo   timeout: 30
        echo   debug: false
        echo.
        echo mcp:
        echo   name: "odoo"
        echo   description: "Interact with Odoo ERP"
    ) > "%CONFIG_DIR%\config.yaml"
    echo   Created: %CONFIG_DIR%\config.yaml
    echo   ^<^< IMPORTANT: Edit this file with your Odoo credentials!
) else (
    echo   Config already exists: %CONFIG_DIR%\config.yaml
)

echo.
echo ================================================
echo   Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Edit %CONFIG_DIR%\config.yaml with your Odoo credentials
echo 2. Add the following to your Hermes Agent config:
echo    (~/.hermes/config.yaml)
echo.
echo    mcp_servers:
echo      odoo:
echo        command: "odoo-mcp"
echo        env:
echo          ODOO_URL: "https://your-instance.odoo.com"
echo          ODOO_DB: "your-database-name"
echo          ODOO_USERNAME: "your^@email.com"
echo          ODOO_API_KEY: "your-api-key"
echo.
echo 3. Restart Hermes Agent
echo.
echo To test: odoo-mcp
echo.
pause
