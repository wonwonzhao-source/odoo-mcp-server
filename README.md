# Odoo MCP Server

A Model Context Protocol (MCP) server that enables AI assistants (like Hermes Agent) to securely interact with Odoo ERP systems.

## For Team Members

### Quick Install

```bash
# 1. Copy the odoo-mcp-server folder to your machine
# 2. Run the installer
./install.sh

# 3. Edit config with your credentials
nano ~/.config/odoo-mcp/config.yaml

# 4. Add to your Hermes config (~/.hermes/config.yaml):
#    mcp_servers:
#      odoo:
#        command: "/HOME/.hermes/hermes-agent/venv/bin/odoo-mcp"
#        env:
#          ODOO_URL: "https://YOUR_INSTANCE.odoo.com"
#          ODOO_DB: "YOUR_DATABASE_NAME"
#          ODOO_USERNAME: "your@email.com"
#          ODOO_API_KEY: "YOUR_API_KEY"

# 5. Restart Hermes Agent
```

### Manual Install

```bash
cd ~/mcp-servers/odoo-mcp-server
pip install -e .

# Or with uv:
uv pip install -e .
```

## For Your Odoo Instance

### Getting Your Database Name

1. Log into your Odoo Sh dashboard
2. Look for the database name in the URL or settings
3. It's often something like: `canadamasq-main-6993412`

### Generating an API Key

1. Log into your Odoo instance as admin
2. Go to **Settings → Users & Companies → Users**
3. Click on your user account
4. Scroll to **API Key** section
5. Click **Generate API Key**
6. Enter a name (e.g., "Claude MCP")
7. **Copy the key immediately** - it's shown only once!

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

## Common Odoo Models

### Manufacturing
| Model | Description |
|-------|-------------|
| `mrp.production` | Manufacturing Orders |
| `mrp.bom` | Bills of Materials |
| `mrp.workorder` | Work Orders |
| `stock.picking` | Stock Transfers |

### Inventory
| Model | Description |
|-------|-------------|
| `stock.quant` | Stock Quantities |
| `stock.location` | Warehouse Locations |
| `product.product` | Product Variants |

### Sales/Purchases
| Model | Description |
|-------|-------------|
| `sale.order` | Sales Orders |
| `purchase.order` | Purchase Orders |
| `account.move` | Invoices/Journal Entries |

### Partners
| Model | Description |
|-------|-------------|
| `res.partner` | Customers, Vendors, Contacts |

## Configuration

### Environment Variables

```bash
export ODOO_URL="https://your-instance.odoo.com"
export ODOO_DB="your-database-name"
export ODOO_USERNAME="your@email.com"
export ODOO_API_KEY="your-api-key"
```

### Config File (`~/.config/odoo-mcp/config.yaml`)

```yaml
odoo:
  url: "https://canadamasq.odoo.com"
  db: "canadamasq-main-6993412"
  username: "patriciag@canadamasq.com"
  api_key: "your-api-key"
  timeout: 30
  debug: false

mcp:
  name: "odoo"
  description: "Interact with Odoo ERP"
```

## Troubleshooting

### "Database does not exist"
- Your database name might be different from the subdomain
- Check Odoo Sh dashboard for the actual database name

### "Authentication failed"
- Verify your email/username is correct
- Regenerate your API key and try again
- Make sure the user account has API access enabled

### "Permission denied"
- The API key user may not have access to the requested model
- Check Odoo access rights for the user account

## Security Notes

- API keys are passed only to the MCP server process
- Credentials are redacted from error messages
- The server uses HTTPS for all Odoo communication

## License

MIT
