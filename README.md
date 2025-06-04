# 🔍 MuckRock MCP Server

A comprehensive Model Context Protocol (MCP) server for interacting with MuckRock's FOIA platform. This server provides 20+ professional-grade tools for filing, tracking, and managing Freedom of Information Act (FOIA) requests.

## ✨ Features

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
# Install dependencies
pip install fastmcp muckrock

# Clone this repository
git clone https://github.com/your-username/mcp-muckrock-agent.git
cd mcp-muckrock-agent
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
      "args": ["/path/to/muckrock_server.py"],
      "env": {
        "MUCKROCK_USERNAME": "your_username",
        "MUCKROCK_PASSWORD": "your_password"
      }
    }
  }
}
```

### 4. **Test the Installation**

Restart Claude Desktop and try:
> **"Show me my MuckRock organizations"**

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

### **Professional FOIA Assistant**

The server acts as a professional FOIA assistant that can:

1. **Draft Professional Requests**: Generate legally compliant FOIA language
2. **Strategic Planning**: Recommend optimal agencies and timing
3. **Compliance Monitoring**: Track deadlines and suggest legal actions
4. **Cost Optimization**: Predict fees and suggest reduction strategies
5. **Appeal Generation**: Create appeals with relevant case law
6. **Campaign Management**: Coordinate multi-agency investigations

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
mcp-muckrock-agent/
├── muckrock_server.py          # Main MCP server
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── AUTHENTICATION_SETUP.md     # Authentication guide
├── MCP_SERVER_README.md        # Technical documentation
└── FOIA_ASSISTANT_USE_CASES.md # Usage examples
```

## 🔐 Security & Privacy

- ✅ Credentials are stored securely in environment variables
- ✅ No hardcoded passwords or tokens in the code
- ✅ Communications encrypted via HTTPS to MuckRock API
- ✅ Local processing - no data sent to third parties
- ✅ Comprehensive .gitignore to prevent credential commits

## 🎓 FOIA Best Practices Built-In

The server incorporates FOIA best practices:

- **Professional Language**: Generates legally compliant request language
- **Fee Optimization**: Built-in fee waiver language and cost reduction strategies  
- **Strategic Timing**: Recommendations for optimal filing timing
- **Multi-Agency Coordination**: Tools for comprehensive investigations
- **Legal Compliance**: Deadline tracking with relevant case law
- **Appeal Strategies**: Professional appeals with legal precedents

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

**Transform your FOIA research with professional-grade tools! 🚀**