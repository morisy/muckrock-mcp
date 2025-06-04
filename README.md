# 🔍 MuckRock MCP Server

⚠️ **EXPERIMENTAL SOFTWARE - USE AT YOUR OWN RISK** ⚠️

An experimental Model Context Protocol (MCP) server for interacting with MuckRock's FOIA platform. This server provides 20+ highly experimental, unstable, and ~potentially~ definitely insecure tools for filing, tracking, and managing Freedom of Information Act (FOIA) requests.

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
- **authenticate** - Log in with your MuckRock credentials (direct method)
- **set_username** - Set username separately (more secure - step 1)
- **authenticate_with_env_password** - Authenticate using environment variable (step 2)
- **authenticate_with_password_file** - Authenticate using password file (step 2)
- **check_auth_status** - Check current authentication status

### 🔍 **Search & Discovery**
- **search_foia_requests** - Search existing FOIA requests by keyword
- **search_agencies** - Find government agencies and their performance metrics
- **get_agency_details** - Detailed agency information including response times
- **get_foia_details** - Comprehensive request details and communications

### 📝 **Smart Request Filing**
- **file_foia_request_simple** - Smart filing with automatic organization selection
- **draft_foia_request** - AI-powered professional request drafting
- **analyze_filing_strategy** - Multi-agency strategic recommendations

### 📊 **Request Management**
- **get_my_requests** - View your FOIA requests with status filtering
- **get_my_organizations** - List your organizations and filing options
- **get_request_communications** - View all communications for a request
- **follow_up_on_request** - Send follow-up messages on existing requests

### ⚖️ **Legal & Compliance Tools**
- **monitor_compliance** - Automated deadline tracking with legal precedents
- **generate_appeal_letter** - Professional appeals with case law citations
- **appeal_request** - File appeals for rejected or partial grants
- **estimate_foia_costs** - Accurate fee predictions and optimization strategies

### 📈 **Analytics & Strategy**
- **track_request_patterns** - Success factor analysis by topic
- **create_foia_campaign** - Multi-agency coordination tools
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

**Note:** You can optionally add credentials in the config, but it's more secure to authenticate interactively:
```json
"env": {
  "MUCKROCK_USERNAME": "your_username",
  "MUCKROCK_PASSWORD": "your_password"
}
```

### 4. **Test the Installation**

Restart Claude Desktop and test with these commands:

1. **Check authentication status:**
   > "Check my MuckRock authentication status"

2. **Authenticate (if needed):**
   
   **Option A - Environment Variable (Most Secure):**
   ```bash
   # In terminal before starting server:
   export MUCKROCK_PASSWORD="your_password"
   ```
   Then in Claude:
   > "Set my MuckRock username to 'myusername'"
   > "Authenticate with environment password"
   
   **Option B - Password File:**
   Save password in a file, then in Claude:
   > "Set my MuckRock username to 'myusername'"
   > "Authenticate with password file at /path/to/password.txt"
   
   **Option C - Direct (Less Secure):**
   > "Authenticate with MuckRock using username 'myusername' and password 'mypassword'"

3. **Test with safe commands:**
   > "Show me my MuckRock organizations"
   > "Search for agencies named 'test'"

⚠️ **ALWAYS TEST WITH TEST AGENCIES FIRST** (Agency ID: 248 is MuckRock's test agency)

## 🎯 Example Usage

### **Natural Language Interface**

Once configured, you can use natural language to interact with MuckRock:

```
"Draft a FOIA request for police contracts from 2020-2024"
"File a request to EPA asking for climate change documents"
"Show me my pending FOIA requests"
"Monitor compliance for request 12345"
"Generate an appeal letter for a b(5) exemption denial"
"Analyze filing strategy for environmental records"
```

### **FOIA Assistant Capabilities** (Experimental)

The server attempts to provide assistance with:

1. **Request Drafting**: Generate FOIA request language (review before using)
2. **Planning Tools**: Basic agency and timing recommendations
3. **Deadline Tracking**: Monitor request deadlines (verify independently)
4. **Cost Estimates**: Rough fee predictions (actual costs may vary)
5. **Appeal Templates**: Basic appeal letter generation
6. **Campaign Planning**: Multi-agency coordination concepts

## 🔧 Advanced Features

### **Multi-Agency Filing Strategy**
```python
# The server can recommend comprehensive filing strategies
analyze_filing_strategy(
    topic="government AI contracts",
    document_types=["contracts", "emails", "reports"],
    geographic_scope="national"
)
```

### **Legal Compliance Monitoring**
```python
# Automated deadline tracking with legal precedents
monitor_compliance(
    foia_id=12345,
    check_precedents=True
)
```

### **Professional Appeal Generation**
```python
# Generate appeals with case law citations
generate_appeal_letter(
    foia_id=12345,
    denial_reasons=["b(5) deliberative process", "b(6) personal privacy"]
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
├── FOIA_ASSISTANT_USE_CASES.md     # Comprehensive usage examples
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

1. **Most Secure - Environment Variable:**
   - Set `MUCKROCK_PASSWORD` in terminal before starting
   - Password never appears in Claude chat
   - Cleared when terminal session ends

2. **Secure - Password File:**
   - Store password in a protected file
   - Set file permissions: `chmod 600 password.txt`
   - Delete file after use

3. **Least Secure - Direct Input:**
   - Password visible in Claude chat history
   - Only use for testing with non-sensitive accounts

4. **Never:**
   - Store passwords in git repositories
   - Share screenshots with passwords visible
   - Use production credentials for testing

## 🎓 FOIA Best Practices (Attempted)

The server attempts to incorporate FOIA best practices, but **always verify**:

- **Request Language**: Templates provided - review and customize before filing
- **Fee Waivers**: Basic fee waiver language included - may need adjustment
- **Timing Suggestions**: General recommendations - use your judgment
- **Multi-Agency Tools**: Experimental coordination features
- **Deadline Tracking**: Basic monitoring - maintain your own calendar
- **Appeal Templates**: Starting points only - consult legal resources

⚠️ **IMPORTANT**: This tool is not a substitute for legal advice or professional FOIA expertise

## 🐛 Known Issues & Limitations

- **Campaign Tool**: Currently only creates plans, doesn't actually file requests
- **Error Handling**: Limited error handling for API failures
- **Token Refresh**: May need to restart if authentication tokens expire
- **Rate Limiting**: No built-in rate limit handling
- **Input Validation**: Minimal validation of user inputs
- **Agency Search**: Returns limited results, may miss some agencies
- **File Downloads**: Only provides URLs, doesn't download files
- **Appeal Filing**: Conceptual implementation, may not work with current API

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
