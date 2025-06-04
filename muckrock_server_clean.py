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
