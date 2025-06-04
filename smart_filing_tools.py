#!/usr/bin/env python3
"""
Smart FOIA Filing Tools with Organization Management
"""

@mcp.tool()
def file_foia_request_simple(
    title: str,
    requested_docs: str,
    agency_ids: List[int],
    organization_name: Optional[str] = None,
    embargo: bool = False,
    permanent_embargo: bool = False,
    use_portal: bool = False,
    portal_password: Optional[str] = None,
    request_fee_waiver: bool = True,
    request_fee_assistance: bool = False
) -> str:
    """
    File a new FOIA request with automatic organization selection.
    
    Args:
        title: Title of the FOIA request
        requested_docs: Description of the documents being requested
        agency_ids: List of agency IDs to send the request to
        organization_name: Organization name to file under (optional - will auto-select if only one)
        embargo: Whether to embargo the request
        permanent_embargo: Whether to permanently embargo the request
        use_portal: Whether to file through agency's online portal
        portal_password: Password for portal filing (if applicable)
        request_fee_waiver: Whether to request a fee waiver
        request_fee_assistance: Whether to request fee assistance
    
    Returns:
        Information about the filed request(s)
    """
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
            "permanent_embargo": permanent_embargo,
            "use_portal": use_portal,
            "portal_password": portal_password,
            "request_fee_waiver": request_fee_waiver,
            "request_fee_assistance": request_fee_assistance
        }
        
        new_request = client.requests.create(**request_data)
        
        return f"""✅ Successfully filed FOIA request!

{selection_info}

**Request Details:**
- **Title:** {new_request.title}
- **ID:** {new_request.id}
- **Status:** {new_request.status}
- **Organization:** {selected_org.name} (ID: {selected_org.id})
- **Agencies:** {len(agency_ids)} agencies
- **Embargo:** {"Yes" if embargo else "No"}
- **Fee Waiver Requested:** {"Yes" if request_fee_waiver else "No"}

You can track this request at: {getattr(new_request, 'absolute_url', 'URL not available')}"""
        
    except Exception as e:
        return f"Error filing FOIA request: {str(e)}"


@mcp.tool()
def get_my_user_info() -> str:
    """
    Get current user information including organizations.
    
    Returns:
        Current user details and organization memberships
    """
    if not username or not password:
        return "Error: Getting user info requires authentication."
    
    try:
        # Get current user information
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
    """
    Get all organizations the current user belongs to.
    
    Returns:
        List of user's organizations with details
    """
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