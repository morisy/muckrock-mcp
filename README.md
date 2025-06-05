# MuckRock MCP Server

A Model Context Protocol (MCP) server for interacting with MuckRock's FOIA platform.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Add to Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "muckrock": {
      "command": "/path/to/python",
      "args": ["/path/to/muckrock_server.py"]
    }
  }
}
```

## Authentication

The server will prompt for MuckRock credentials on startup. You can also set environment variables:

```bash
export MUCKROCK_USERNAME="your_username"
export MUCKROCK_PASSWORD="your_password"
```

## Features

- **Search** - Search FOIA requests and government agencies
- **File Requests** - File new FOIA requests with automatic organization selection
- **Track Requests** - View your submitted requests and their status
- **Organizations** - Manage which organization to file under

## Usage

Once configured, use natural language in Claude:

- "Search for EPA FOIA requests"
- "File a FOIA request for police records"
- "Show my pending requests"
- "What organizations can I file under?"

## Tools Available

- `check_auth_status` - Check authentication status
- `search_foia_requests` - Search public FOIA requests
- `search_agencies` - Find government agencies
- `get_foia_details` - Get request details
- `get_my_user_info` - View your user info
- `get_my_organizations` - List your organizations
- `file_foia_request_simple` - File new FOIA requests

## Notes

- Always test with test agencies first (ID: 248)
- Authentication tokens are automatically refreshed
- This is experimental software - use at your own risk

## Documentation

See the `docs/` folder for detailed guides on authentication, deployment, and use cases.