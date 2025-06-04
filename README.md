# 🔍 MuckRock MCP Server

⚠️ **EXPERIMENTAL SOFTWARE - USE AT YOUR OWN RISK** ⚠️

An experimental Model Context Protocol (MCP) server for interacting with MuckRock's FOIA platform. This server provides basic tools for filing, tracking, and managing Freedom of Information Act (FOIA) requests.

## ⚠️ Important Disclaimers

- **ALPHA QUALITY**: This code is experimental and likely contains bugs
- **SECURITY**: Not audited for security - do not use in production without review
- **AUTHENTICATION**: Credentials are passed as environment variables - ensure proper security measures
- **NO WARRANTY**: This software comes with no guarantees or warranties
- **TEST FIRST**: Always test with test agencies before filing real requests
- **RATE LIMITS**: Be mindful of MuckRock's API rate limits
- **UNSTABLE**: APIs and functionality may change or break without notice

## ✨ Features

### 🔐 **Authentication**
- **check_auth_status** - Check current authentication status

### 🔍 **Search & Discovery**
- **search_foia_requests** - Search existing FOIA requests by keyword
- **search_agencies** - Find government agencies and their performance metrics
- **get_agency_details** - Detailed agency information including response times
- **get_foia_details** - Comprehensive request details and communications

### 📝 **Request Filing**
- **file_foia_request_simple** - File FOIA requests with automatic organization selection

### 📊 **Request Management**
- **get_my_requests** - View your FOIA requests with status filtering
- **get_my_organizations** - List your organizations and filing options
- **get_request_communications** - View all communications for a request
- **follow_up_on_request** - Send follow-up messages on existing requests
- **appeal_request** - File appeals for rejected or partial grants
- **get_request_cost** - Fee information and payment status

## 🚀 Quick Start

### 1. **Installation**

```bash
# Clone this repository
git clone https://github.com/morisy/muckrock-mcp.git
cd muckrock-mcp

# Install dependencies
pip install -r requirements.txt
```

### 2. **MuckRock Account Setup**

1. Sign up at [MuckRock.com](https://www.muckrock.com/accounts/signup/)
2. Get your account credentials (username/password)
3. Optionally create organizations for filing requests

### 3. **Claude Desktop Configuration**

Add to your Claude Desktop config file (`~/Library/Application Support/Claude/claude_desktop_config.json`):

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

**Authentication Options:**

**Option A - Interactive Prompt (Recommended):**
The server will prompt for credentials when it starts. This is the most secure method.

**Option B - Environment Variables:**
```json
"env": {
  "MUCKROCK_USERNAME": "your_username",
  "MUCKROCK_PASSWORD": "your_password"
}
```

### 4. **Start the Server**

When you restart Claude Desktop, the MuckRock server will start and prompt for authentication:

```
============================================================
🔍 MuckRock MCP Server - Authentication Setup
============================================================
To use authenticated features, please provide your MuckRock credentials.
Press Enter without typing to skip authentication (anonymous mode).

MuckRock Username: your_username
MuckRock Password: [hidden]
Testing credentials...
✅ Successfully authenticated as: your_username
📋 Found 2 organization(s):
   - Your Organization (ID: 12345)
   - Test Org (ID: 67890)
```

### 5. **Test the Installation**

Test with these commands in Claude:

1. **Check authentication status:**
   > "Check my MuckRock authentication status"

2. **Test basic functions:**
   > "Show me my MuckRock organizations"
   > "Search for agencies named 'test'"

⚠️ **ALWAYS TEST WITH TEST AGENCIES FIRST** (Agency ID: 248 is MuckRock's test agency)

## 🎯 Example Usage

### **Natural Language Interface**

Once configured, you can use natural language to interact with MuckRock:

```
"File a FOIA request to EPA asking for climate change documents"
"Show me my pending FOIA requests"
"Search for agencies that handle environmental data"
"Get details about my request #12345"
"Follow up on my pending request"
```

### **Basic FOIA Capabilities**

The server provides basic assistance with:

1. **Request Filing**: File FOIA requests to government agencies
2. **Request Tracking**: View and monitor your submitted requests
3. **Agency Search**: Find government agencies and their contact information
4. **Organization Management**: Manage which organization to file requests under
5. **Communications**: View messages and follow up on existing requests

## 🔧 Basic Features

### **Request Filing**
```python
# File a FOIA request to one or more agencies
file_foia_request_simple(
    title="Environmental Data Request",
    requested_docs="All reports on air quality from 2023",
    agency_ids=[EPA_AGENCY_ID]
)
```

### **Request Management**
```python
# View your submitted requests
get_my_requests(status="pending")

# Follow up on a specific request
follow_up_on_request(
    foia_id=12345,
    message="Requesting status update on my pending request"
)
```

## 📁 File Structure

```
muckrock-mcp/
├── muckrock_server.py              # Main MCP server using FastMCP framework
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── AUTHENTICATION_SETUP.md         # Authentication guide
├── MCP_SERVER_README.md            # Technical documentation
├── FOIA_ASSISTANT_USE_CASES.md     # Usage examples
└── DEPLOYMENT_SUMMARY.md           # Deployment guide
```

## 🔐 Security Considerations

- ⚠️ **NOT SECURITY AUDITED** - Review code before using with real credentials
- 🔑 Multiple authentication methods with varying security levels
- 🔒 Uses HTTPS for MuckRock API communications
- 💾 Local processing only (no third-party data sharing)
- 📝 .gitignore configured to avoid credential commits
- ⚠️ **PROTECT YOUR CREDENTIALS** - Never share config files with auth info

### **Authentication Security Best Practices:**

1. **Most Secure - Interactive Prompt (Default):**
   - Server prompts for credentials at startup
   - Passwords never appear in Claude chat
   - Uses getpass for hidden password input
   - Credentials only exist during server session

2. **Secure - Environment Variables:**
   - Set before starting Claude Desktop
   - No interactive prompts needed
   - Credentials cleared when session ends

3. **Never:**
   - Store passwords in git repositories
   - Share screenshots with passwords visible
   - Use production credentials for testing
   - Input credentials through Claude chat interface

## 📝 FOIA Usage Notes

When using this tool:

- **Review all requests** before filing - the tool does not generate request text
- **Verify agency information** independently - agency data may be outdated  
- **Track deadlines yourself** - no automated deadline monitoring
- **Consult FOIA resources** for legal requirements and best practices
- **Test with test agencies first** - always verify functionality before real use

⚠️ **IMPORTANT**: This tool is not a substitute for legal advice or professional FOIA expertise

## 🐛 Known Issues & Limitations

- **Error Handling**: Limited error handling for API failures
- **Token Refresh**: May need to restart if authentication tokens expire
- **Rate Limiting**: No built-in rate limit handling
- **Input Validation**: Minimal validation of user inputs
- **Agency Search**: Returns limited results, may miss some agencies
- **File Downloads**: Only provides URLs, doesn't download files
- **Appeal Filing**: Basic implementation, may not work reliably
- **Follow-ups**: Conceptual implementation, verify functionality before use

## 🛠️ Development

### **Running the Server Directly**
```bash
# Set environment variables
export MUCKROCK_USERNAME="your_username"  
export MUCKROCK_PASSWORD="your_password"

# Run the server
python muckrock_server.py
```

### **Testing Tools**
```python
# Test individual tools
from muckrock_server import search_agencies, file_foia_request_simple

# Search for agencies
agencies = search_agencies("police", limit=5)

# File a test request  
result = file_foia_request_simple(
    title="Test Request",
    requested_docs="Test documents",
    agency_ids=[248]  # Test Agency
)
```

## 📚 Documentation

- **[Authentication Setup Guide](AUTHENTICATION_SETUP.md)** - Detailed authentication configuration
- **[Technical Documentation](MCP_SERVER_README.md)** - Server implementation details  
- **[Use Cases Guide](FOIA_ASSISTANT_USE_CASES.md)** - Comprehensive usage examples
- **[MuckRock API Docs](https://www.muckrock.com/api/)** - Official API documentation

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure security best practices
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🎉 Credits

Built with:
- [FastMCP](https://github.com/pydantic/fastmcp) - MCP server framework
- [MuckRock Python API](https://python-muckrock.readthedocs.io/) - API wrapper
- [Claude Code](https://claude.ai/code) - Development assistance

---

**Use at your own risk - this is experimental software! 🚧**
