# MuckRock MCP Server

A comprehensive Model Context Protocol (MCP) server for interacting with MuckRock's FOIA platform.

## Features

### Search & Discovery
- **search_foia_requests** - Search for FOIA requests by keyword
- **search_agencies** - Search for government agencies
- **search_jurisdictions** - Get jurisdiction information
- **search_organizations** - Search for organizations on MuckRock

### Request Management
- **file_foia_request** - File new FOIA requests with one or more agencies
  - Supports embargo options
  - Fee waiver requests
  - Portal filing
  - Organization filing
- **follow_up_on_request** - Send follow-up messages on existing requests
- **appeal_request** - Appeal rejected or partially granted requests
- **get_my_requests** - View your own FOIA requests with optional status filtering

### Request Details
- **get_foia_details** - Get comprehensive details about a specific request
- **get_request_communications** - View all communications for a request
- **download_request_files** - Get information about files attached to a request
- **get_request_cost** - Check fees and costs for a request

### Agency Information
- **get_agency_details** - Get detailed agency information including:
  - Average response time
  - Fee rate
  - Success rate
  - Contact information

## Test Information

For testing purposes, you can use:
- Any MuckRock account for testing
- Test Agency (ID: 248) - Available for filing test requests

## Example Usage in Claude Desktop

Once configured, you can use natural language to interact with MuckRock:

1. **Search for requests**: "Search for FOIA requests about climate change"
2. **File a request**: "File a FOIA request to Test Agency (ID 248) asking for public records about environmental policies"
3. **Check your requests**: "Show me my pending FOIA requests"
4. **Get request details**: "Get details about FOIA request 170089"
5. **Follow up**: "Send a follow-up on request 170089 asking about the status"
6. **Search agencies**: "Find agencies in California"
7. **Get agency info**: "Get details about agency 248"

## Authentication

The server requires MuckRock credentials for most operations:
- Anonymous access: Limited to searching and viewing public requests
- Authenticated access: Full functionality including filing requests, follow-ups, and appeals

## Configuration

The server is configured in Claude Desktop's config file:
```json
{
  "mcpServers": {
    "muckrock": {
      "command": "/path/to/python",
      "args": ["/path/to/muckrock_server.py"],
      "env": {
        "MUCKROCK_USERNAME": "your-username",
        "MUCKROCK_PASSWORD": "your-password"
      }
    }
  }
}
```

## Status Codes

FOIA request statuses include:
- `submitted` - Request submitted, awaiting acknowledgment
- `ack` - Request acknowledged by agency
- `processed` - Being processed by agency
- `appealing` - Under appeal
- `fix` - Requires fix from requester
- `payment` - Payment required
- `done` - Request completed
- `partial` - Partially granted
- `rejected` - Request rejected
- `no_docs` - No responsive documents
- `abandoned` - Request abandoned

## Limitations

Some features may have limitations based on the MuckRock API:
- Organization search requires specific implementation
- Follow-up and appeal methods are conceptual and may need adjustment based on API specifics
- File downloads provide URLs but don't actually download files

## Error Handling

The server includes comprehensive error handling:
- Authentication checks for operations requiring login
- Graceful handling of missing data fields
- Clear error messages for troubleshooting