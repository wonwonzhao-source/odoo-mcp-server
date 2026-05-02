# Odoo MCP Server

A Model Context Protocol (MCP) server that enables AI assistants (like Hermes Agent) to securely interact with Odoo ERP systems.

## For Team Members — Download Pre-Built Executables

### Windows (Recommended)
1. Go to the **Releases** page: https://github.com/wonwonzhao-source/odoo-mcp-server/releases
2. Download `odoo-mcp-windows.exe`
3. Double-click to run — no Python needed!

### macOS
1. Go to the **Releases** page: https://github.com/wonwonzhao-source/odoo-mcp-server/releases
2. Download `odoo-mcp-macos`
3. In Terminal: `chmod +x odoo-mcp-macos`
4. Run: `./odoo-mcp-macos`

### Linux
1. Go to the **Releases** page: https://github.com/wonwonzhao-source/odoo-mcp-server/releases
2. Download `odoo-mcp-linux`
3. In Terminal: `chmod +x odoo-mcp-linux`
4. Run: `./odoo-mcp-linux`

## Configuration

### Hermes Agent Configuration

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  odoo:
    command: "/full/path/to/odoo-mcp"        # macOS/Linux
    # command: "C:\\path\\to\\odoo-mcp.exe" # Windows
    env:
      ODOO_URL: "https://canadamasq.odoo.com"
      ODOO_DB: "canadamasq-main-6993412"
      ODOO_USERNAME: "your@email.com"
      ODOO_API_KEY: "your-api-key"
```

### Config File (optional — environment variables also work)

Create `~/.config/odoo-mcp/config.yaml` (macOS/Linux) or `%USERPROFILE%\.config\odoo-mcp\config.yaml` (Windows):

```yaml
odoo:
  url: "https://canadamasq.odoo.com"
  db: "canadamasq-main-6993412"
  username: "your@email.com"
  api_key: "your-api-key"
  timeout: 30
  debug: false

mcp:
  name: "odoo"
  description: "Interact with Odoo ERP"
```

### Getting Your Odoo Credentials

**Database Name:**
1. Log into your Odoo Sh dashboard
2. Find the database name (format: `canadamasq-main-6993412`)

**API Key:**
1. Log into your Odoo instance
2. Go to **Settings → Users & Companies → Users**
3. Click your user → **API Key** → **Generate**
4. Copy the key immediately (shown only once)

## For Developers

### Building from Source

```bash
git clone https://github.com/wonwonzhao-source/odoo-mcp-server.git
cd odoo-mcp-server
pip install -e .
odoo-mcp
```

### Building Standalone Executables

```bash
pip install pyinstaller
pyinstaller --name odoo-mcp --onefile --console --clean src/odoo_mcp/__main__.py
./dist/odoo-mcp          # macOS/Linux
dist\odoo-mcp.exe        # Windows
```

### Triggering a Release Build

Push a version tag — GitHub Actions will automatically build and attach the executables to the release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Features

- **Search & Read**: Query Odoo records with filtering, sorting, pagination
- **Create**: Create new records (orders, products, MOs, etc.)
- **Update**: Modify existing records
- **Delete**: Remove records (with care)
- **Model Introspection**: Discover models and field definitions
- **Method Calling**: Execute Odoo model methods

## Available Tools

| Tool | Description |
|------|-------------|
| `odoo_search_read` | Search for records and return selected fields |
| `odoo_create` | Create a new record |
| `odoo_write` | Update existing records |
| `odoo_unlink` | Delete records |
| `odoo_call_method` | Call an arbitrary model method |
| `odoo_list_models` | List all available models |
| `odoo_get_model_fields` | Get field definitions for a model |
| `odoo_get_version` | Get Odoo server version |
| `odoo_whoami` | Get current authenticated user |

## Troubleshooting

### "Database does not exist"
- Your database name might be different from the subdomain
- Check Odoo Sh dashboard for the actual database name

### "Authentication failed"
- Verify your email/username is correct
- Regenerate your API key and try again

## Security Notes

- API keys are passed only to the MCP server process
- Credentials are redacted from error messages
- The server uses HTTPS for all Odoo communication

## License

MIT
