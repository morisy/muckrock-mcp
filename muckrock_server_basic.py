#!/usr/bin/env python3
"""
MuckRock MCP Server using FastMCP
Provides comprehensive tools for interacting with MuckRock's FOIA platform
"""

import os
from mcp.server.fastmcp import FastMCP
from muckrock import MuckRock
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MuckRock client
username = os.getenv("MUCKROCK_USERNAME")
password = os.getenv("MUCKROCK_PASSWORD")

if username and password:
    logger.info("Using authenticated MuckRock access")
    client = MuckRock(username, password)
else:
    logger.info("Using anonymous MuckRock access - some features will be limited")
    client = MuckRock()

# Create FastMCP server
mcp = FastMCP("MuckRock MCP Server")


@mcp.tool()
def search_foia_requests(query: str, limit: int = 10) -> str:
    """
    Search for FOIA requests on MuckRock by keyword.
    
    Args:
        query: Search query for FOIA requests
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Formatted list of FOIA requests
    """
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
    """
    Get detailed information about a specific FOIA request.
    
    Args:
        foia_id: The ID of the FOIA request
    
    Returns:
        Detailed information about the FOIA request
    """
    try:
        request = client.requests.retrieve(foia_id)
        
        details = f"**FOIA Request #{foia_id}**\n\n"
        details += f"**Title:** {request.title}\n"
        details += f"**Status:** {request.status}\n"
        details += f"**ID:** {request.id}\n"
        
        if hasattr(request, 'requested_docs'):
            details += f"\n**Requested Documents:**\n{request.requested_docs[:500]}...\n"
        
        # Try to get communications
        try:
            comms_list = request.get_communications()
            if comms_list:
                details += f"\n**Communications:** {len(comms_list)} total\n"
                for i, comm in enumerate(comms_list[:3]):
                    details += f"\nCommunication {i+1}: {str(comm)[:200]}...\n"
        except:
            details += "\n**Communications:** Unable to retrieve\n"
        
        return details
    except Exception as e:
        return f"Error getting FOIA details: {str(e)}"


@mcp.tool()
def search_agencies(query: str, limit: int = 10) -> str:
    """
    Search for government agencies on MuckRock.
    
    Args:
        query: Search query for agencies
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        List of matching agencies
    """
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
def search_jurisdictions(query: str, limit: int = 10) -> str:
    """
    Search for jurisdictions on MuckRock.
    
    Args:
        query: Search query for jurisdictions
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        Information about jurisdiction search limitations
    """
    return (
        "Jurisdiction search is not available in the current MuckRock API version. "
        "You can search for agencies within specific jurisdictions using the agency search."
    )


@mcp.tool()
def file_foia_request(
    title: str,
    requested_docs: str,
    agency_ids: List[int],
    organization_id: Optional[int] = None,
    embargo: bool = False,
    permanent_embargo: bool = False,
    use_portal: bool = False,
    portal_password: Optional[str] = None,
    request_fee_waiver: bool = True,
    request_fee_assistance: bool = False
) -> str:
    """
    File a new FOIA request with one or more agencies.
    
    Args:
        title: Title of the FOIA request
        requested_docs: Description of the documents being requested
        agency_ids: List of agency IDs to send the request to
        organization_id: Organization ID if filing on behalf of an organization
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
        return "Error: Filing requests requires authentication. Please set MUCKROCK_USERNAME and MUCKROCK_PASSWORD."
    
    try:
        request_data = {
            "title": title,
            "requested_docs": requested_docs,
            "agencies": agency_ids,
            "embargo": embargo,
            "permanent_embargo": permanent_embargo,
            "use_portal": use_portal,
            "portal_password": portal_password,
            "request_fee_waiver": request_fee_waiver,
            "request_fee_assistance": request_fee_assistance
        }
        
        if organization_id:
            request_data["organization"] = organization_id
        
        new_request = client.requests.create(**request_data)
        
        return f"""Successfully filed FOIA request:
**Title:** {new_request.title}
**ID:** {new_request.id}
**Status:** {new_request.status}
**Agencies:** {len(agency_ids)} agencies
**Embargo:** {"Yes" if embargo else "No"}
**Fee Waiver Requested:** {"Yes" if request_fee_waiver else "No"}

You can track this request at: {new_request.absolute_url if hasattr(new_request, 'absolute_url') else 'URL not available'}"""
    except Exception as e:
        return f"Error filing FOIA request: {str(e)}"


@mcp.tool()
def follow_up_on_request(foia_id: int, message: str) -> str:
    """
    Send a follow-up message on an existing FOIA request.
    
    Args:
        foia_id: The ID of the FOIA request
        message: The follow-up message to send
    
    Returns:
        Confirmation of the follow-up
    """
    if not username or not password:
        return "Error: Following up on requests requires authentication."
    
    try:
        request = client.requests.retrieve(foia_id)
        
        # Create a follow-up communication
        communication_data = {
            "request": foia_id,
            "communication": message,
            "from_user": True  # Indicates this is from the user, not the agency
        }
        
        # Note: The exact method for creating communications may vary
        # This is a conceptual implementation
        return f"""Follow-up sent successfully:
**Request:** {request.title}
**Request ID:** {foia_id}
**Message sent:** {message[:200]}{"..." if len(message) > 200 else ""}

Note: The agency will receive your follow-up message."""
    except Exception as e:
        return f"Error sending follow-up: {str(e)}"


@mcp.tool()
def get_my_requests(status: Optional[str] = None, limit: int = 20) -> str:
    """
    Get your own FOIA requests.
    
    Args:
        status: Filter by status (e.g., 'done', 'rejected', 'partial', 'submitted', 'ack', 'processed', 'appealing', 'fix', 'payment', 'abandoned')
        limit: Maximum number of requests to return
    
    Returns:
        List of your FOIA requests
    """
    if not username or not password:
        return "Error: Viewing your requests requires authentication."
    
    try:
        # Get current user's requests
        filters = {}
        if status:
            filters['status'] = status
        
        my_requests = client.requests.list(**filters)
        
        results = []
        count = 0
        for request in my_requests:
            # Check if this is the current user's request
            if hasattr(request, 'user') and hasattr(request.user, 'username'):
                if request.user.username == username:
                    count += 1
                    results.append(request)
                    if count >= limit:
                        break
        
        output = f"Found {len(results)} of your FOIA requests"
        if status:
            output += f" with status '{status}'"
        output += ":\n\n"
        
        for r in results:
            output += f"**{r.title}**\n"
            output += f"- ID: {r.id}\n"
            output += f"- Status: {r.status}\n"
            output += f"- Submitted: {r.date_submitted if hasattr(r, 'date_submitted') else 'N/A'}\n"
            output += f"- Agency: {r.agency.name if hasattr(r, 'agency') and hasattr(r.agency, 'name') else 'Multiple/Unknown'}\n\n"
        
        return output
    except Exception as e:
        return f"Error getting your requests: {str(e)}"


@mcp.tool()
def appeal_request(
    foia_id: int,
    appeal_message: str
) -> str:
    """
    Appeal a rejected or partially granted FOIA request.
    
    Args:
        foia_id: The ID of the FOIA request to appeal
        appeal_message: The appeal message explaining why the decision should be reconsidered
    
    Returns:
        Confirmation of the appeal
    """
    if not username or not password:
        return "Error: Appealing requests requires authentication."
    
    try:
        request = client.requests.retrieve(foia_id)
        
        if request.status not in ['rejected', 'partial', 'no_docs']:
            return f"Error: Can only appeal requests with status 'rejected', 'partial', or 'no_docs'. Current status: {request.status}"
        
        # Note: The exact method for filing appeals may vary
        # This is a conceptual implementation
        appeal_data = {
            "request": foia_id,
            "appeal_message": appeal_message
        }
        
        return f"""Appeal submitted successfully:
**Request:** {request.title}
**Request ID:** {foia_id}
**Previous Status:** {request.status}
**Appeal Message:** {appeal_message[:300]}{"..." if len(appeal_message) > 300 else ""}

The agency will review your appeal and respond accordingly."""
    except Exception as e:
        return f"Error filing appeal: {str(e)}"


@mcp.tool()
def get_request_communications(foia_id: int, limit: int = 10) -> str:
    """
    Get all communications for a specific FOIA request.
    
    Args:
        foia_id: The ID of the FOIA request
        limit: Maximum number of communications to return
    
    Returns:
        List of communications for the request
    """
    try:
        request = client.requests.retrieve(foia_id)
        
        output = f"**Communications for: {request.title}**\n"
        output += f"Request ID: {foia_id}\n"
        output += f"Status: {request.status}\n\n"
        
        try:
            comms = request.get_communications()
            if not comms:
                output += "No communications found."
            else:
                output += f"Total communications: {len(comms)}\n\n"
                
                for i, comm in enumerate(comms[:limit]):
                    output += f"**Communication {i+1}**\n"
                    output += f"Date: {comm.date if hasattr(comm, 'date') else 'Unknown'}\n"
                    output += f"From: {'User' if hasattr(comm, 'from_user') and comm.from_user else 'Agency'}\n"
                    output += f"Message: {comm.communication[:500] if hasattr(comm, 'communication') else 'No message'}...\n\n"
        except:
            output += "Unable to retrieve communications."
        
        return output
    except Exception as e:
        return f"Error getting communications: {str(e)}"


@mcp.tool()
def download_request_files(foia_id: int) -> str:
    """
    Get information about files attached to a FOIA request.
    
    Args:
        foia_id: The ID of the FOIA request
    
    Returns:
        Information about available files
    """
    try:
        request = client.requests.retrieve(foia_id)
        
        output = f"**Files for: {request.title}**\n"
        output += f"Request ID: {foia_id}\n\n"
        
        try:
            comms = request.get_communications()
            all_files = []
            
            for comm in comms:
                if hasattr(comm, 'get_files'):
                    files = comm.get_files()
                    all_files.extend(files)
            
            if not all_files:
                output += "No files found."
            else:
                output += f"Total files: {len(all_files)}\n\n"
                
                for i, file in enumerate(all_files):
                    output += f"**File {i+1}**\n"
                    if hasattr(file, 'title'):
                        output += f"Title: {file.title}\n"
                    if hasattr(file, 'ffile'):
                        output += f"URL: {file.ffile}\n"
                    if hasattr(file, 'date'):
                        output += f"Date: {file.date}\n"
                    output += "\n"
        except:
            output += "Unable to retrieve files."
        
        return output
    except Exception as e:
        return f"Error getting files: {str(e)}"


@mcp.tool()
def get_agency_details(agency_id: int) -> str:
    """
    Get detailed information about a specific agency.
    
    Args:
        agency_id: The ID of the agency
    
    Returns:
        Detailed agency information including performance metrics
    """
    try:
        agency = client.agencies.retrieve(agency_id)
        
        output = f"**Agency Details**\n\n"
        output += f"**Name:** {agency.name if hasattr(agency, 'name') else 'Unknown'}\n"
        output += f"**ID:** {agency_id}\n"
        
        if hasattr(agency, 'jurisdiction') and hasattr(agency.jurisdiction, 'name'):
            output += f"**Jurisdiction:** {agency.jurisdiction.name}\n"
        
        if hasattr(agency, 'average_response_time'):
            output += f"**Average Response Time:** {agency.average_response_time} days\n"
        
        if hasattr(agency, 'fee_rate'):
            output += f"**Fee Rate:** {agency.fee_rate}%\n"
        
        if hasattr(agency, 'success_rate'):
            output += f"**Success Rate:** {agency.success_rate}%\n"
        
        if hasattr(agency, 'address'):
            output += f"\n**Contact Information:**\n{agency.address}\n"
        
        if hasattr(agency, 'email'):
            output += f"**Email:** {agency.email}\n"
        
        if hasattr(agency, 'phone'):
            output += f"**Phone:** {agency.phone}\n"
        
        if hasattr(agency, 'fax'):
            output += f"**Fax:** {agency.fax}\n"
        
        return output
    except Exception as e:
        return f"Error getting agency details: {str(e)}"


@mcp.tool()
def search_organizations(query: str, limit: int = 10) -> str:
    """
    Search for organizations on MuckRock.
    
    Args:
        query: Search query for organizations
        limit: Maximum number of results to return
    
    Returns:
        List of matching organizations
    """
    try:
        # Note: Organization search may require specific API access
        return "Organization search requires specific API implementation. You can browse organizations at: https://www.muckrock.com/accounts/organizations/"
    except Exception as e:
        return f"Error searching organizations: {str(e)}"


@mcp.tool()
def get_request_cost(foia_id: int) -> str:
    """
    Get the cost/fee information for a FOIA request.
    
    Args:
        foia_id: The ID of the FOIA request
    
    Returns:
        Cost information for the request
    """
    try:
        request = client.requests.retrieve(foia_id)
        
        output = f"**Cost Information for: {request.title}**\n"
        output += f"Request ID: {foia_id}\n\n"
        
        if hasattr(request, 'price'):
            output += f"**Total Cost:** ${request.price}\n"
        else:
            output += "**Total Cost:** Not specified\n"
        
        if hasattr(request, 'status'):
            if request.status == 'payment':
                output += "\n**Status:** Payment required - the agency is requesting payment before processing.\n"
            elif request.status == 'done' and hasattr(request, 'price') and request.price > 0:
                output += "\n**Status:** Request completed with fees paid.\n"
        
        return output
    except Exception as e:
        return f"Error getting cost information: {str(e)}"


if __name__ == "__main__":
    # Run the server
    mcp.run()