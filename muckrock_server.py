#!/usr/bin/env python3
"""
Enhanced MuckRock MCP Server with Advanced FOIA Assistant Features
Provides comprehensive tools for effective FOIA request management
"""

import os
import getpass
from mcp.server.fastmcp import FastMCP
from muckrock import MuckRock
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_credentials():
    """Securely prompt for MuckRock credentials at startup."""
    username = os.getenv("MUCKROCK_USERNAME")
    password = os.getenv("MUCKROCK_PASSWORD")
    
    # If environment variables are set, use them
    if username and password:
        logger.info(f"Using credentials from environment variables for user: {username}")
        return username, password
    
    # Otherwise, prompt for credentials
    print("\n" + "="*60)
    print("🔍 MuckRock MCP Server - Authentication Setup")
    print("="*60)
    print("To use authenticated features, please provide your MuckRock credentials.")
    print("Press Enter without typing to skip authentication (anonymous mode).")
    print("")
    
    try:
        username = input("MuckRock Username: ").strip()
        if not username:
            print("Skipping authentication - starting in anonymous mode.")
            return None, None
            
        password = getpass.getpass("MuckRock Password: ")
        if not password:
            print("No password provided - starting in anonymous mode.")
            return None, None
            
        print("Testing credentials...")
        
        # Test the credentials
        test_client = MuckRock(username, password)
        try:
            user = test_client.users.me()
            print(f"✅ Successfully authenticated as: {user.username}")
            
            # Show organizations
            try:
                orgs = test_client.organizations.list()
                user_orgs = list(orgs)
                if user_orgs:
                    print(f"📋 Found {len(user_orgs)} organization(s):")
                    for org in user_orgs:
                        print(f"   - {org.name} (ID: {org.id})")
            except:
                pass
                
            return username, password
            
        except Exception as e:
            print(f"❌ Authentication failed: {str(e)}")
            print("Starting in anonymous mode.")
            return None, None
            
    except KeyboardInterrupt:
        print("\n❌ Authentication cancelled - starting in anonymous mode.")
        return None, None
    except Exception as e:
        print(f"❌ Error during authentication: {str(e)}")
        print("Starting in anonymous mode.")
        return None, None

# Initialize MuckRock client with credentials
username, password = get_credentials()

# Global variables for authentication state
client = None
current_username = None
stored_username = None
stored_password = None

def refresh_client():
    """Refresh the MuckRock client with stored credentials."""
    global client, current_username, stored_username, stored_password
    
    if stored_username and stored_password:
        try:
            logger.info("Refreshing MuckRock client credentials...")
            client = MuckRock(stored_username, stored_password)
            current_username = stored_username
            # Test the refreshed client
            user = client.users.me()
            logger.info(f"Successfully refreshed authentication for: {user.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh authentication: {str(e)}")
            return False
    return False

def ensure_authenticated():
    """Ensure the client is authenticated, refresh if needed."""
    global client, current_username
    
    if not current_username:
        return False
        
    try:
        # Test current authentication
        client.users.me()
        return True
    except Exception as e:
        logger.warning(f"Authentication test failed, attempting refresh: {str(e)}")
        # Try to refresh
        if refresh_client():
            return True
        else:
            logger.error("Failed to refresh authentication")
            return False

def with_auth_retry(func):
    """Decorator to automatically retry API calls with authentication refresh."""
    def wrapper(*args, **kwargs):
        try:
            # First attempt
            return func(*args, **kwargs)
        except Exception as e:
            # If it's an auth error, try refreshing
            if "auth" in str(e).lower() or "token" in str(e).lower() or "401" in str(e):
                logger.warning(f"API call failed with potential auth error, refreshing: {str(e)}")
                if ensure_authenticated():
                    try:
                        # Retry after refresh
                        return func(*args, **kwargs)
                    except Exception as retry_e:
                        logger.error(f"API call failed even after auth refresh: {str(retry_e)}")
                        raise retry_e
                else:
                    logger.error("Authentication refresh failed")
                    raise e
            else:
                # Not an auth error, re-raise original exception
                raise e
    return wrapper

if username and password:
    client = MuckRock(username, password)
    current_username = username
    stored_username = username
    stored_password = password
    logger.info(f"Server starting with authenticated access for: {username}")
else:
    client = MuckRock()
    logger.info("Server starting in anonymous mode - authentication features will be unavailable")

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

@mcp.tool()
def check_auth_status() -> str:
    """
    Check current authentication status.
    
    Returns:
        Current authentication status and available features
    """
    global client, current_username
    
    if current_username:
        if ensure_authenticated():
            try:
                user = client.users.me()
                return f"""✅ **Authenticated as: {current_username}**

All features are available including:
- Filing FOIA requests
- Viewing your requests
- Managing organizations
- Following up on requests

Authentication is active and automatically refreshed as needed."""
            except Exception as e:
                return f"""⚠️ **Authentication issue**

Unable to verify authentication: {str(e)}
This is unusual - please restart the server if the problem persists."""
        else:
            return """❌ **Authentication failed**

Server was started with authentication, but credentials are no longer valid.
This may be due to:
- Expired session tokens that couldn't be refreshed
- Changed password
- Account access issues

Restart the server to re-authenticate."""
    else:
        return """❌ **Not authenticated**

Server was started in anonymous mode with limited features.

**Available features (anonymous):**
- Search public FOIA requests
- View request details
- Search agencies
- View agency information

**To enable authentication:**
Restart the server and provide credentials when prompted, or set environment variables:
- MUCKROCK_USERNAME
- MUCKROCK_PASSWORD

**Features requiring authentication:**
- File new FOIA requests
- View your requests
- Manage organizations
- Send follow-ups
- File appeals"""


# BASIC TOOLS

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
    if not current_username:
        return "Error: Getting user info requires authentication. Server was started in anonymous mode."
    
    if not ensure_authenticated():
        return "Error: Authentication has expired and could not be refreshed. Please restart the server."
    
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
    if not current_username:
        return "Error: Getting organizations requires authentication. Server was started in anonymous mode."
    
    if not ensure_authenticated():
        return "Error: Authentication has expired and could not be refreshed. Please restart the server."
    
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
    if not current_username:
        return "Error: Filing requests requires authentication. Server was started in anonymous mode."
    
    if not ensure_authenticated():
        return "Error: Authentication has expired and could not be refreshed. Please restart the server."
    
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