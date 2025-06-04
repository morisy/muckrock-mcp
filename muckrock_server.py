#!/usr/bin/env python3
"""
Enhanced MuckRock MCP Server with Advanced FOIA Assistant Features
Provides comprehensive tools for effective FOIA request management
"""

import os
from mcp.server.fastmcp import FastMCP
from muckrock import MuckRock
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MuckRock client
username = os.getenv("MUCKROCK_USERNAME")
password = os.getenv("MUCKROCK_PASSWORD")

# Debug logging to check environment variables
logger.info(f"Environment check - MUCKROCK_USERNAME: {'Set' if username else 'Not set'}")
logger.info(f"Environment check - MUCKROCK_PASSWORD: {'Set' if password else 'Not set'}")

# Global variables for authentication state
client = None
current_username = None
pending_username = None

if username and password:
    logger.info(f"Using authenticated MuckRock access for user: {username}")
    client = MuckRock(username, password)
    current_username = username
else:
    logger.info("Using anonymous MuckRock access - some features will be limited")
    logger.info("Use the 'authenticate' tool to log in with your MuckRock credentials")
    client = MuckRock()

# Create FastMCP server
mcp = FastMCP("Enhanced MuckRock FOIA Assistant")

# Helper function for parsing MuckRock request responses
def parse_request_response(response_url: str, title: str) -> dict:
    """Parse MuckRock request creation response and extract useful information."""
    import re
    
    result = {
        "url": response_url,
        "title": title,
        "id": "Unknown",
        "status": "Submitted"
    }
    
    if isinstance(response_url, str) and 'muckrock.com' in response_url:
        # Extract request ID from URL pattern like: /foi/multirequest/title-123456/
        id_match = re.search(r'-(\d+)/?$', response_url)
        if id_match:
            result["id"] = id_match.group(1)
    
    return result

# AUTHENTICATION TOOL

@mcp.tool()
def authenticate(username: str, password: str) -> str:
    """
    Authenticate with MuckRock using your username and password.
    
    Args:
        username: Your MuckRock username
        password: Your MuckRock password
    
    Returns:
        Authentication status message
    """
    global client
    
    try:
        # Test authentication by creating a new client
        test_client = MuckRock(username, password)
        
        # Try to access user info to verify credentials work
        try:
            user = test_client.users.me()
            client = test_client  # Update global client
            logger.info(f"Successfully authenticated as {username}")
            
            # Store username for status checks (but not password)
            global current_username
            current_username = username
            
            # Get user's organizations
            orgs_info = ""
            try:
                orgs = client.organizations.list()
                user_orgs = list(orgs)
                if user_orgs:
                    orgs_info = f"\n\n**Your Organizations:**\n"
                    for org in user_orgs:
                        orgs_info += f"- {org.name} (ID: {org.id})\n"
            except:
                pass
            
            return f"""✅ **Successfully authenticated!**

**Username:** {user.username}
**User ID:** {user.id}{orgs_info}

You can now use all authenticated features including:
- Filing FOIA requests
- Viewing your requests
- Managing organizations
- Following up on requests"""
            
        except Exception as e:
            return f"""❌ **Authentication failed**

Please check your username and password. Common issues:
- Incorrect username or password
- Account may need email verification
- API access may be restricted

Error: {str(e)}"""
            
    except Exception as e:
        return f"❌ **Authentication error:** {str(e)}"


@mcp.tool()
def set_username(username: str) -> str:
    """
    Set your MuckRock username (step 1 of 2 for authentication).
    
    Args:
        username: Your MuckRock username
    
    Returns:
        Instructions for next step
    """
    global pending_username
    pending_username = username
    
    return f"""✅ Username set: {username}

Now provide your password using one of these methods:

**Option 1 - Direct (less secure):**
Use the 'authenticate' tool with your username and password

**Option 2 - Environment variable (recommended):**
Set your password in the terminal before starting the server:
```
export MUCKROCK_PASSWORD="your_password"
```
Then use: `authenticate_with_env_password()`

**Option 3 - Password file:**
Save your password in a file and use:
`authenticate_with_password_file("/path/to/password.txt")`"""


@mcp.tool()
def authenticate_with_env_password() -> str:
    """
    Authenticate using the username you set and password from MUCKROCK_PASSWORD environment variable.
    
    Returns:
        Authentication status message
    """
    global client, current_username, pending_username
    
    if not hasattr(globals(), 'pending_username') or not pending_username:
        return "❌ Please set your username first using the 'set_username' tool"
    
    password = os.getenv("MUCKROCK_PASSWORD")
    if not password:
        return """❌ No password found in environment variable.

Please set your password:
```bash
export MUCKROCK_PASSWORD="your_password"
```
Then restart the server or try again."""
    
    # Use the existing authenticate logic
    try:
        test_client = MuckRock(pending_username, password)
        try:
            user = test_client.users.me()
            client = test_client
            current_username = pending_username
            pending_username = None  # Clear pending username
            
            logger.info(f"Successfully authenticated as {current_username}")
            
            # Get organizations info
            orgs_info = ""
            try:
                orgs = client.organizations.list()
                user_orgs = list(orgs)
                if user_orgs:
                    orgs_info = f"\n\n**Your Organizations:**\n"
                    for org in user_orgs:
                        orgs_info += f"- {org.name} (ID: {org.id})\n"
            except:
                pass
            
            return f"""✅ **Successfully authenticated!**

**Username:** {user.username}
**User ID:** {user.id}{orgs_info}

Password was read from environment variable (not shown).
You can now use all authenticated features."""
            
        except Exception as e:
            return f"❌ **Authentication failed:** {str(e)}"
    except Exception as e:
        return f"❌ **Authentication error:** {str(e)}"


@mcp.tool()
def authenticate_with_password_file(password_file_path: str) -> str:
    """
    Authenticate using the username you set and password from a file.
    
    Args:
        password_file_path: Path to file containing your password
    
    Returns:
        Authentication status message
    """
    global client, current_username, pending_username
    
    if not hasattr(globals(), 'pending_username') or not pending_username:
        return "❌ Please set your username first using the 'set_username' tool"
    
    try:
        with open(password_file_path, 'r') as f:
            password = f.read().strip()
    except Exception as e:
        return f"❌ Could not read password file: {str(e)}"
    
    # Use the existing authenticate logic
    try:
        test_client = MuckRock(pending_username, password)
        try:
            user = test_client.users.me()
            client = test_client
            current_username = pending_username
            pending_username = None  # Clear pending username
            
            logger.info(f"Successfully authenticated as {current_username}")
            
            # Get organizations info
            orgs_info = ""
            try:
                orgs = client.organizations.list()
                user_orgs = list(orgs)
                if user_orgs:
                    orgs_info = f"\n\n**Your Organizations:**\n"
                    for org in user_orgs:
                        orgs_info += f"- {org.name} (ID: {org.id})\n"
            except:
                pass
            
            return f"""✅ **Successfully authenticated!**

**Username:** {user.username}
**User ID:** {user.id}{orgs_info}

Password was read from file: {password_file_path}
You can now use all authenticated features."""
            
        except Exception as e:
            return f"❌ **Authentication failed:** {str(e)}"
    except Exception as e:
        return f"❌ **Authentication error:** {str(e)}"


@mcp.tool()
def check_auth_status() -> str:
    """
    Check current authentication status.
    
    Returns:
        Current authentication status and available features
    """
    global client, current_username
    
    if hasattr(globals(), 'current_username') and current_username:
        try:
            # Try to get user info to verify still authenticated
            user = client.users.me()
            return f"""✅ **Authenticated as: {current_username}**

All features are available including:
- Filing FOIA requests
- Viewing your requests
- Managing organizations
- Following up on requests

To switch accounts, use the 'authenticate' tool with different credentials."""
        except:
            return """⚠️ **Authentication may have expired**

Please re-authenticate using the 'authenticate' tool with your username and password."""
    else:
        return """❌ **Not authenticated**

You are currently using anonymous access with limited features.

**Available features (anonymous):**
- Search public FOIA requests
- View request details
- Search agencies
- View agency information

**To unlock all features, authenticate with:**
`authenticate(username="your_username", password="your_password")`

**Features requiring authentication:**
- File new FOIA requests
- View your requests
- Manage organizations
- Send follow-ups
- File appeals"""


# ORIGINAL BASIC TOOLS

@mcp.tool()
def search_foia_requests(query: str, limit: int = 10) -> str:
    """Search for FOIA requests on MuckRock by keyword."""
    try:
        results = []
        request_list = client.requests.list(search=query)
        
        count = 0
        for request in request_list:
            count += 1
            results.append({
                "id": request.id,
                "title": request.title,
                "status": request.status,
                "agency_id": request.agency if hasattr(request, 'agency') else None,
                "user_id": request.user if hasattr(request, 'user') else None,
            })
            
            if count >= limit:
                break
        
        output = f"Found {len(results)} FOIA requests matching '{query}':\n\n"
        for r in results:
            output += f"**{r['title']}**\n"
            output += f"- ID: {r['id']}\n"
            output += f"- Status: {r['status']}\n"
            output += f"- Agency ID: {r['agency_id']}\n"
            output += f"- User ID: {r['user_id']}\n\n"
        
        return output
    except Exception as e:
        return f"Error searching FOIA requests: {str(e)}"


@mcp.tool()
def get_foia_details(foia_id: int) -> str:
    """Get detailed information about a specific FOIA request."""
    try:
        request = client.requests.retrieve(foia_id)
        
        details = f"**FOIA Request #{foia_id}**\n\n"
        details += f"**Title:** {request.title}\n"
        details += f"**Status:** {request.status}\n"
        details += f"**ID:** {request.id}\n"
        
        if hasattr(request, 'requested_docs'):
            details += f"\n**Requested Documents:**\n{request.requested_docs[:500]}...\n"
        
        return details
    except Exception as e:
        return f"Error getting FOIA details: {str(e)}"


@mcp.tool()
def search_agencies(query: str, limit: int = 10) -> str:
    """Search for government agencies on MuckRock."""
    try:
        results = []
        agencies = client.agencies.list(search=query)
        
        count = 0
        for agency in agencies:
            count += 1
            results.append({
                "id": agency.id if hasattr(agency, 'id') else None,
                "name": agency.name if hasattr(agency, 'name') else str(agency),
            })
            
            if count >= limit:
                break
        
        output = f"Found {len(results)} agencies matching '{query}':\n\n"
        for a in results:
            output += f"- {a['name']} (ID: {a['id']})\n"
        
        return output
    except Exception as e:
        return f"Error searching agencies: {str(e)}"


@mcp.tool()
def get_my_user_info() -> str:
    """Get current user information including organizations."""
    if not username or not password:
        return "Error: Getting user info requires authentication."
    
    try:
        user = client.users.me()
        
        output = f"**Current User Information**\n\n"
        output += f"**Username:** {user.username}\n"
        output += f"**User ID:** {user.id}\n"
        
        # Get user's organizations
        try:
            orgs = client.organizations.list()
            user_orgs = list(orgs)
            
            if user_orgs:
                output += f"\n**Organizations ({len(user_orgs)}):**\n"
                for org in user_orgs:
                    output += f"- {org.name} (ID: {org.id})\n"
            else:
                output += "\n**Organizations:** None found\n"
        except:
            output += "\n**Organizations:** Unable to retrieve\n"
        
        return output
    except Exception as e:
        return f"Error getting user info: {str(e)}"


@mcp.tool()
def get_my_organizations() -> str:
    """Get all organizations the current user belongs to."""
    if not username or not password:
        return "Error: Getting organizations requires authentication."
    
    try:
        orgs = client.organizations.list()
        user_orgs = list(orgs)
        
        if not user_orgs:
            return "No organizations found for your account."
        
        output = f"**Your Organizations**\n\n"
        
        for org in user_orgs:
            output += f"**{org.name}**\n"
            output += f"- ID: {org.id}\n"
            
            if hasattr(org, 'private'):
                output += f"- Private: {org.private}\n"
            if hasattr(org, 'monthly_requests'):
                output += f"- Monthly Requests: {org.monthly_requests}\n"
            
            output += "\n"
        
        output += f"**Total:** {len(user_orgs)} organizations\n"
        output += "\n💡 **Tip:** Use these organization names or IDs when filing FOIA requests!"
        
        return output
    except Exception as e:
        return f"Error getting organizations: {str(e)}"


@mcp.tool()
def file_foia_request_simple(
    title: str,
    requested_docs: str,
    agency_ids: List[int],
    organization_name: Optional[str] = None,
    embargo: bool = False,
    request_fee_waiver: bool = True
) -> str:
    """File a new FOIA request with automatic organization selection."""
    if not username or not password:
        return "Error: Filing requests requires authentication."
    
    try:
        # Get user's available organizations
        orgs = client.organizations.list()
        user_orgs = list(orgs)
        
        if not user_orgs:
            return "Error: No organizations found for your account. You need to be associated with an organization to file FOIA requests."
        
        # Select organization
        selected_org = None
        
        if len(user_orgs) == 1:
            # Only one organization - use it automatically
            selected_org = user_orgs[0]
            selection_info = f"**Auto-selected organization:** {selected_org.name} (only option available)"
            
        elif organization_name:
            # User specified an organization name - find it
            for org in user_orgs:
                if organization_name.lower() in org.name.lower():
                    selected_org = org
                    selection_info = f"**Selected organization:** {selected_org.name} (matched '{organization_name}')"
                    break
            
            if not selected_org:
                org_list = "\n".join([f"- {org.name}" for org in user_orgs])
                return f"""Error: Could not find organization matching '{organization_name}'.

**Your available organizations:**
{org_list}

**Please specify one of these organization names.**"""
        
        else:
            # Multiple organizations available - ask user to choose
            org_list = "\n".join([f"- {org.name}" for org in user_orgs])
            return f"""Multiple organizations available. Please specify which one to file under:

**Your available organizations:**
{org_list}

**To file this request, use:**
file_foia_request_simple(title="{title}", requested_docs="...", agency_ids={agency_ids}, organization_name="[org name]")"""
        
        # File the request with selected organization
        request_data = {
            "title": title,
            "requested_docs": requested_docs,
            "agencies": agency_ids,
            "organization": selected_org.id,
            "embargo": embargo,
            "request_fee_waiver": request_fee_waiver
        }
        
        new_request_url = client.requests.create(**request_data)
        
        # Extract request ID from URL if possible
        request_id = "Unknown"
        if isinstance(new_request_url, str) and 'muckrock.com' in new_request_url:
            # Try to extract ID from URL pattern like: /foi/multirequest/title-123456/
            import re
            id_match = re.search(r'-(\d+)/?$', new_request_url)
            if id_match:
                request_id = id_match.group(1)
        
        return f"""✅ Successfully filed FOIA request!

{selection_info}

**Request Details:**
- **Title:** {title}
- **Request ID:** {request_id}
- **Status:** Submitted
- **Organization:** {selected_org.name} (ID: {selected_org.id})
- **Agencies:** {len(agency_ids)} agencies  
- **Embargo:** {"Yes" if embargo else "No"}
- **Fee Waiver Requested:** {"Yes" if request_fee_waiver else "No"}

🔗 **Track your request at:** {new_request_url}

💡 **Bookmark this URL** to monitor updates, communications, and document releases!"""
        
    except Exception as e:
        return f"Error filing FOIA request: {str(e)}"



if __name__ == "__main__":
    # Run the server
    mcp.run()