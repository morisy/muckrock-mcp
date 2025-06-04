#!/usr/bin/env python3
"""
MuckRock MCP Server
An MCP server that provides tools for searching FOIA requests, agencies, and jurisdictions
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from muckrock import MuckRock
from datetime import datetime


# Initialize MuckRock client
username = os.getenv("MUCKROCK_USERNAME")
password = os.getenv("MUCKROCK_PASSWORD")

if username and password:
    client = MuckRock(username, password)
else:
    client = MuckRock()  # Anonymous access


# Create MCP server
server = Server("muckrock-mcp-server")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MuckRock tools."""
    return [
        Tool(
            name="search_foia_requests",
            description="Search for FOIA requests on MuckRock by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for FOIA requests"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_foia_details",
            description="Get detailed information about a specific FOIA request",
            inputSchema={
                "type": "object",
                "properties": {
                    "foia_id": {
                        "type": "integer",
                        "description": "The ID of the FOIA request"
                    }
                },
                "required": ["foia_id"]
            }
        ),
        Tool(
            name="search_agencies",
            description="Search for government agencies on MuckRock",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for agencies"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="search_jurisdictions",
            description="Search for jurisdictions on MuckRock",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for jurisdictions"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Execute MuckRock tools."""
    
    if name == "search_foia_requests":
        query = arguments["query"]
        limit = arguments.get("limit", 10)
        
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
            
            return [TextContent(
                type="text",
                text=f"Found {len(results)} FOIA requests matching '{query}':\n\n" + 
                     "\n\n".join([
                         f"**{r['title']}**\n" +
                         f"- ID: {r['id']}\n" +
                         f"- Status: {r['status']}\n" +
                         f"- Agency ID: {r['agency_id']}\n" +
                         f"- User ID: {r['user_id']}"
                         for r in results
                     ])
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching FOIA requests: {str(e)}")]
    
    elif name == "get_foia_details":
        foia_id = arguments["foia_id"]
        
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
            
            return [TextContent(type="text", text=details)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting FOIA details: {str(e)}")]
    
    elif name == "search_agencies":
        query = arguments["query"]
        limit = arguments.get("limit", 10)
        
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
            
            return [TextContent(
                type="text",
                text=f"Found {len(results)} agencies matching '{query}':\n\n" + 
                     "\n".join([f"- {a['name']} (ID: {a['id']})" for a in results])
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching agencies: {str(e)}")]
    
    elif name == "search_jurisdictions":
        query = arguments["query"]
        limit = arguments.get("limit", 10)
        
        try:
            # Note: The newer API may not have direct jurisdiction endpoint
            return [TextContent(
                type="text", 
                text=f"Jurisdiction search is not available in the current MuckRock API version. " +
                     f"You can search for agencies within specific jurisdictions using the agency search."
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching jurisdictions: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    """Run the MCP server."""
    from mcp.server.lowlevel import InitializationOptions
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream, 
            InitializationOptions()
        )


if __name__ == "__main__":
    asyncio.run(main())