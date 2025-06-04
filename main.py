import asyncio
import os
import time
from typing import Optional, List, Dict, Any

from mcp_agent.app import MCPApp
from mcp_agent.config import Settings, LoggerSettings
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from mcp_agent.workflows.llm.augmented_llm_anthropic import AnthropicAugmentedLLM

# Import MuckRock Python wrapper
from muckrock import MuckRock


class MuckRockAgent:
    """
    An MCP agent that interacts with MuckRock's API to search for and retrieve
    public records requests, agencies, and jurisdictions.
    """
    
    def __init__(self, app: MCPApp, username: Optional[str] = None, password: Optional[str] = None):
        self.app = app
        self.logger = None
        self.context = None
        self.username = username or os.getenv("MUCKROCK_USERNAME")
        self.password = password or os.getenv("MUCKROCK_PASSWORD")
        
        if self.username and self.password:
            self.client = MuckRock(self.username, self.password)
        else:
            self.client = MuckRock()  # Anonymous access
    
    async def search_foia_requests(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for FOIA requests on MuckRock."""
        try:
            results = []
            # Search for FOIA requests
            foia_list = self.client.foia.filter(search=query, page_size=limit)
            
            for foia in foia_list:
                results.append({
                    "id": foia.id,
                    "title": foia.title,
                    "status": foia.status,
                    "agency": foia.agency.name if foia.agency else "Unknown",
                    "jurisdiction": foia.jurisdiction.name if foia.jurisdiction else "Unknown",
                    "date_submitted": str(foia.date_submitted) if foia.date_submitted else None,
                    "date_done": str(foia.date_done) if foia.date_done else None,
                    "user": foia.user.username if foia.user else "Unknown",
                    "absolute_url": foia.absolute_url,
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching FOIA requests: {e}")
            return []
    
    async def get_foia_details(self, foia_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific FOIA request."""
        try:
            foia = self.client.foia.get(foia_id)
            
            # Extract communications
            communications = []
            for comm in foia.communications:
                communications.append({
                    "date": str(comm.date) if comm.date else None,
                    "from_user": comm.from_user.username if comm.from_user else None,
                    "communication": comm.communication[:200] + "..." if len(comm.communication) > 200 else comm.communication,
                })
            
            return {
                "id": foia.id,
                "title": foia.title,
                "status": foia.status,
                "embargo": foia.embargo,
                "description": foia.description,
                "agency": {
                    "name": foia.agency.name if foia.agency else None,
                    "jurisdiction": foia.agency.jurisdiction.name if foia.agency and foia.agency.jurisdiction else None,
                },
                "jurisdiction": foia.jurisdiction.name if foia.jurisdiction else None,
                "date_submitted": str(foia.date_submitted) if foia.date_submitted else None,
                "date_done": str(foia.date_done) if foia.date_done else None,
                "user": foia.user.username if foia.user else None,
                "price": foia.price,
                "communications_count": len(communications),
                "recent_communications": communications[:3],  # Show only recent 3
                "absolute_url": foia.absolute_url,
            }
        except Exception as e:
            self.logger.error(f"Error getting FOIA details: {e}")
            return None
    
    async def search_agencies(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for agencies on MuckRock."""
        try:
            results = []
            agencies = self.client.agency.filter(search=query, page_size=limit)
            
            for agency in agencies:
                results.append({
                    "id": agency.id,
                    "name": agency.name,
                    "jurisdiction": agency.jurisdiction.name if agency.jurisdiction else "Unknown",
                    "average_response_time": agency.average_response_time,
                    "fee_rate": agency.fee_rate,
                    "success_rate": agency.success_rate,
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching agencies: {e}")
            return []
    
    async def search_jurisdictions(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for jurisdictions on MuckRock."""
        try:
            results = []
            jurisdictions = self.client.jurisdiction.filter(search=query, page_size=limit)
            
            for jurisdiction in jurisdictions:
                results.append({
                    "id": jurisdiction.id,
                    "name": jurisdiction.name,
                    "level": jurisdiction.level,
                    "parent": jurisdiction.parent.name if jurisdiction.parent else None,
                })
            
            return results
        except Exception as e:
            self.logger.error(f"Error searching jurisdictions: {e}")
            return []


async def example_usage():
    """Example usage of the MuckRock MCP Agent."""
    
    # Initialize the MCP app
    app = MCPApp(name="mcp_muckrock_agent")
    
    async with app.run() as agent_app:
        logger = agent_app.logger
        context = agent_app.context
        
        logger.info("Starting MuckRock MCP Agent...")
        
        # Create MuckRock agent instance
        muckrock_agent = MuckRockAgent(app)
        muckrock_agent.logger = logger
        muckrock_agent.context = context
        
        # Create an agent with LLM capabilities
        research_agent = Agent(
            name="muckrock_researcher",
            instruction="""You are a research assistant with access to MuckRock's database 
            of public records requests. You help users find information about FOIA requests,
            agencies, and jurisdictions. You can search for requests, get detailed information
            about specific requests, and find agencies and jurisdictions.""",
            server_names=[],  # No MCP servers needed for this example
        )
        
        async with research_agent:
            # Attach an LLM to the agent
            llm = await research_agent.attach_llm(OpenAIAugmentedLLM)
            
            # Example 1: Search for FOIA requests about police records
            logger.info("Searching for police-related FOIA requests...")
            police_requests = await muckrock_agent.search_foia_requests("police", limit=5)
            
            if police_requests:
                logger.info(f"Found {len(police_requests)} police-related FOIA requests")
                for req in police_requests[:3]:  # Show first 3
                    logger.info(f"- {req['title']} (Status: {req['status']}, Agency: {req['agency']})")
                
                # Get details of the first request
                if police_requests:
                    first_request_id = police_requests[0]['id']
                    details = await muckrock_agent.get_foia_details(first_request_id)
                    if details:
                        logger.info(f"\nDetailed info for request {first_request_id}:")
                        logger.info(f"Title: {details['title']}")
                        logger.info(f"Status: {details['status']}")
                        logger.info(f"Description: {details['description'][:200]}...")
                        logger.info(f"Communications: {details['communications_count']}")
            
            # Example 2: Search for agencies in California
            logger.info("\nSearching for agencies in California...")
            ca_agencies = await muckrock_agent.search_agencies("California", limit=5)
            
            if ca_agencies:
                logger.info(f"Found {len(ca_agencies)} California agencies")
                for agency in ca_agencies[:3]:
                    logger.info(f"- {agency['name']} (Success Rate: {agency['success_rate']}%, Avg Response: {agency['average_response_time']} days)")
            
            # Example 3: Use LLM to analyze the data
            if police_requests:
                analysis_prompt = f"""
                Based on these police-related FOIA requests:
                {[{'title': r['title'], 'status': r['status'], 'agency': r['agency']} for r in police_requests[:3]]}
                
                Provide a brief analysis of:
                1. What types of police records are being requested
                2. The success rate of these requests
                3. Which agencies are involved
                """
                
                analysis = await llm.generate_str(message=analysis_prompt)
                logger.info(f"\nLLM Analysis:\n{analysis}")


if __name__ == "__main__":
    start = time.time()
    asyncio.run(example_usage())
    end = time.time()
    print(f"\nTotal run time: {end - start:.2f}s")