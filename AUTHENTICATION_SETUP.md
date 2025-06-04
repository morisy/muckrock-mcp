# 🔐 MuckRock MCP Server - Authentication Setup Guide

## 🎯 Authentication Configuration

This guide shows how to configure your MuckRock MCP server with authenticated access and smart organization management.

## 🔐 Authentication Setup

### Option 1: Claude Desktop Configuration
Add your MuckRock credentials to Claude Desktop config:

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

### Option 2: Environment Variables
Set environment variables before running:

```bash
export MUCKROCK_USERNAME="your_username"
export MUCKROCK_PASSWORD="your_password"
python muckrock_server.py
```

### Getting MuckRock Credentials
1. Sign up at https://www.muckrock.com/accounts/signup/
2. Go to your account settings to find your API credentials
3. Or use your regular login username/password

## 🚀 Smart Filing Features

### **1. Automatic Organization Selection**
- If user has only 1 organization → Auto-selects it
- If user has multiple organizations → Prompts to choose
- Can specify organization by name (partial matching)

### **2. Filing Methods Available**

**🔥 Recommended: `file_foia_request_simple()`**
```python
# Auto-handles organization selection
file_foia_request_simple(
    title="Police Records Request",
    requested_docs="All police incident reports from 2024",
    agency_ids=[248]  # Use search_agencies() to find IDs
)
```

## 🔧 Management Tools

- **`get_my_user_info()`** - See user details and organizations
- **`get_my_organizations()`** - List all available organizations with details
- **`search_agencies()`** - Find agencies to file requests with
- **`file_foia_request_simple()`** - Smart filing with auto org selection

## ✅ Features Available After Authentication

1. **Organization Access** - Retrieve user's organizations automatically
2. **Request Filing** - File FOIA requests to any agency
3. **Smart Selection** - Handles single/multiple org scenarios  
4. **Request Tracking** - Get URLs to track your requests
5. **Token Management** - Automatic refresh handling

## 🎯 Example Usage in Claude Desktop

Once authenticated, you can use natural language:

> **"File a FOIA request asking for police reports from 2024"**

The assistant will:
1. Show available organizations
2. Ask which one to use (if multiple)
3. Help you find the right agency
4. File the request automatically
5. Provide tracking information

## 📁 Configuration Files

- ✅ **`muckrock_server.py`** - Main server with authentication
- ✅ **`claude_desktop_config.json`** - Add your credentials here
- ✅ **Environment variables** - Alternative auth method

## 🔄 Production Ready

The server:
- ✅ Authenticates securely with MuckRock
- ✅ Handles organization selection intelligently  
- ✅ Provides helpful error messages and guidance
- ✅ Includes 20+ advanced FOIA assistant tools
- ✅ Ready for token refresh management

## 🚀 Quick Start

1. **Get MuckRock account** at https://www.muckrock.com
2. **Add credentials** to Claude Desktop config or environment
3. **Restart Claude Desktop** 
4. **Test with:** "Show me my MuckRock organizations"

Your enhanced MuckRock FOIA assistant is ready to go! 🎉

## 🔒 Security Notes

- Never commit credentials to version control
- Use environment variables in production
- Credentials are only sent to MuckRock's official API
- Consider using API keys if available instead of passwords