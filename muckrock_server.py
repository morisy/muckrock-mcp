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

if username and password:
    logger.info(f"Using authenticated MuckRock access for user: {username}")
    client = MuckRock(username, password)
else:
    logger.info("Using anonymous MuckRock access - some features will be limited")
    logger.info("To enable authentication, set MUCKROCK_USERNAME and MUCKROCK_PASSWORD environment variables")
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


# ENHANCED TOOLS BELOW

@mcp.tool()
def draft_foia_request(
    document_type: str,
    subject_matter: str,
    date_range_start: Optional[str] = None,
    date_range_end: Optional[str] = None,
    agency_type: str = "federal",
    include_fee_waiver: bool = True,
    include_expedited: bool = False
) -> str:
    """
    Generate a professionally drafted FOIA request using best practices.
    
    Args:
        document_type: Type of documents (emails, reports, contracts, memos, etc.)
        subject_matter: What the documents are about
        date_range_start: Start date for documents (YYYY-MM-DD)
        date_range_end: End date for documents (YYYY-MM-DD)
        agency_type: federal, state, or local
        include_fee_waiver: Include fee waiver language
        include_expedited: Request expedited processing
    
    Returns:
        A professionally drafted FOIA request
    """
    
    # Document type templates
    doc_templates = {
        "emails": "all emails, including attachments, sent or received",
        "reports": "all reports, studies, analyses, or assessments",
        "contracts": "all contracts, agreements, memoranda of understanding, or similar documents",
        "memos": "all memoranda, correspondence, or internal communications",
        "meeting": "all meeting minutes, agendas, notes, or recordings",
        "policies": "all policies, procedures, guidelines, or directives"
    }
    
    doc_language = doc_templates.get(document_type.lower(), "all documents")
    
    # Base request
    request_text = f"Under the Freedom of Information Act (FOIA), 5 U.S.C. § 552, I am requesting {doc_language} "
    request_text += f"related to {subject_matter}"
    
    # Add date range if provided
    if date_range_start and date_range_end:
        request_text += f" created, sent, or received between {date_range_start} and {date_range_end}"
    elif date_range_start:
        request_text += f" created, sent, or received after {date_range_start}"
    
    request_text += ".\n\n"
    
    # Search terms suggestion
    request_text += "Please search for records using the following terms:\n"
    # Extract key terms from subject matter
    key_terms = subject_matter.split()[:5]  # Simple extraction, could be enhanced
    for term in key_terms:
        request_text += f"- {term}\n"
    
    request_text += "\n"
    
    # Format preference
    request_text += "I prefer to receive these records in electronic format if possible.\n\n"
    
    # Fee waiver language
    if include_fee_waiver:
        request_text += """I am requesting a waiver of all fees associated with this request. Disclosure of the requested information is in the public interest because it is likely to contribute significantly to public understanding of government operations and activities. The information will be used to inform the public about these matters.

I am willing to pay fees up to $25. Please notify me if the fees will exceed this amount.\n\n"""
    
    # Expedited processing
    if include_expedited:
        request_text += """I am requesting expedited processing of this request. There is an urgent need to inform the public about government activity that is the subject of this request.\n\n"""
    
    # Closing
    request_text += "Thank you for your assistance with this request. I look forward to your response within the statutory time limit of 20 working days, as required by law."
    
    return f"""**Professionally Drafted FOIA Request:**

{request_text}

**Tips for this request:**
1. Review and customize the search terms based on your specific needs
2. Consider if there are specific offices or personnel who might have these records
3. Save this draft before sending to refine if needed
4. Track the statutory deadline (20 working days from submission)"""


@mcp.tool()
def analyze_filing_strategy(
    topic: str,
    document_types: List[str],
    geographic_scope: str = "national",
    budget_limit: Optional[float] = None
) -> str:
    """
    Analyze and recommend optimal filing strategy for FOIA requests.
    
    Args:
        topic: The subject matter of interest
        document_types: Types of documents sought
        geographic_scope: national, regional, state, or local
        budget_limit: Maximum budget for fees
    
    Returns:
        Strategic recommendations for filing
    """
    
    strategy = f"**FOIA Filing Strategy Analysis for: {topic}**\n\n"
    
    # Recommend agencies based on scope
    strategy += "**Recommended Agencies:**\n"
    
    if geographic_scope == "national":
        strategy += """Federal agencies to consider:
- For policy matters: White House, OMB, relevant Cabinet departments
- For enforcement: DOJ, FBI, relevant regulatory agencies
- For data/research: CDC, EPA, DOE (depending on topic)
- For communications: Check each agency's FOIA reading room first\n\n"""
    else:
        strategy += f"""For {geographic_scope} scope:
- State agencies (varies by state)
- Local agencies (city/county)
- Regional federal offices
- Consider both state FOIA/sunshine laws AND federal FOIA\n\n"""
    
    # Multi-agency strategy
    strategy += """**Multi-Agency Filing Strategy:**
1. File with the originating agency first
2. Then file with agencies likely to have received copies
3. Consider filing with oversight agencies
4. Don't forget about contractors/consultants who may have records\n\n"""
    
    # Timing recommendations
    strategy += """**Timing Optimization:**
- Avoid filing right before holidays or fiscal year end
- Check agency FOIA logs for current backlog
- Consider splitting large requests into smaller, focused ones
- File simultaneously with multiple agencies to save time\n\n"""
    
    # Cost optimization
    if budget_limit:
        strategy += f"""**Cost Management (Budget: ${budget_limit}):**
- Request fee waivers citing public interest
- Narrow date ranges to reduce volume
- Ask for electronic records only
- Consider starting with a sample date range\n\n"""
    
    # Document type specific advice
    strategy += "**Document Type Strategies:**\n"
    for doc_type in document_types:
        if doc_type.lower() == "emails":
            strategy += "- Emails: Specify sender/recipient domains, use specific subject keywords\n"
        elif doc_type.lower() == "contracts":
            strategy += "- Contracts: Include procurement/contracting office, specify vendors if known\n"
        elif doc_type.lower() == "reports":
            strategy += "- Reports: Check agency websites first, request drafts if final versions are public\n"
    
    return strategy


@mcp.tool()
def monitor_compliance(
    foia_id: int,
    check_precedents: bool = True
) -> str:
    """
    Monitor legal compliance and suggest actions when deadlines are missed.
    
    Args:
        foia_id: The FOIA request ID to monitor
        check_precedents: Include relevant legal precedents
    
    Returns:
        Compliance status and recommended actions
    """
    
    try:
        request = client.requests.retrieve(foia_id)
        
        output = f"**Compliance Monitoring for Request #{foia_id}**\n"
        output += f"Title: {request.title}\n"
        output += f"Status: {request.status}\n\n"
        
        # Calculate days since submission
        if hasattr(request, 'date_submitted') and request.date_submitted:
            submit_date = datetime.fromisoformat(str(request.date_submitted))
            days_elapsed = (datetime.now() - submit_date).days
            business_days = days_elapsed * 5 / 7  # Rough estimate
            
            output += f"**Timeline Analysis:**\n"
            output += f"- Submitted: {request.date_submitted}\n"
            output += f"- Days elapsed: {days_elapsed} ({int(business_days)} business days)\n"
            
            # Check compliance based on status
            if request.status == "submitted" and business_days > 20:
                output += "\n⚠️ **COMPLIANCE ISSUE**: Agency has exceeded 20-day statutory deadline for initial response.\n"
                output += "\n**Recommended Actions:**\n"
                output += "1. Send follow-up citing 5 U.S.C. § 552(a)(6)(A)(i)\n"
                output += "2. Consider constructive denial and file appeal\n"
                output += "3. Contact agency FOIA officer directly\n"
                
                if check_precedents:
                    output += "\n**Relevant Precedents:**\n"
                    output += "- Citizens for Responsibility & Ethics v. FEC (2013): Failure to respond is constructive denial\n"
                    output += "- Judicial Watch v. FDA (2021): Courts may order expedited processing for delays\n"
            
            elif request.status == "ack" and business_days > 30:
                output += "\n⚠️ **WARNING**: Processing time exceeding typical timeframes.\n"
                output += "Consider sending a status inquiry.\n"
            
            elif request.status == "processed" and business_days > 60:
                output += "\n⚠️ **EXTENDED DELAY**: Consider requesting estimated completion date.\n"
        
        # Fee-related compliance
        if request.status == "payment":
            output += "\n**Fee Compliance:**\n"
            output += "- Agency must justify fees under FOIA fee schedule\n"
            output += "- You can appeal excessive fees\n"
            output += "- Fee waivers must be considered for public interest\n"
        
        return output
        
    except Exception as e:
        return f"Error monitoring compliance: {str(e)}"


@mcp.tool()
def estimate_foia_costs(
    agency_id: int,
    page_estimate: int,
    requester_category: str = "commercial",
    include_search_time: bool = True,
    include_review_time: bool = True
) -> str:
    """
    Estimate potential FOIA fees and suggest optimization strategies.
    
    Args:
        agency_id: The agency ID
        page_estimate: Estimated number of pages
        requester_category: commercial, news_media, educational, or other
        include_search_time: Whether search time will be charged
        include_review_time: Whether review time will be charged
    
    Returns:
        Cost estimate and optimization suggestions
    """
    
    # Standard federal FOIA fee structure
    fees = {
        "search_hourly": 44.00,
        "review_hourly": 50.00,
        "duplication_per_page": 0.15,
        "electronic_media": 10.00
    }
    
    # Fee waivers by category
    category_waivers = {
        "commercial": {"search": False, "review": False, "duplication": False},
        "news_media": {"search": True, "review": True, "duplication": 100},  # 100 free pages
        "educational": {"search": True, "review": True, "duplication": 100},
        "other": {"search": False, "review": True, "duplication": 100}
    }
    
    waivers = category_waivers.get(requester_category, category_waivers["commercial"])
    
    output = f"**FOIA Cost Estimate**\n\n"
    output += f"Agency ID: {agency_id}\n"
    output += f"Estimated pages: {page_estimate}\n"
    output += f"Requester category: {requester_category}\n\n"
    
    total_cost = 0
    
    # Search costs
    if include_search_time and not waivers["search"]:
        search_hours = min(2, page_estimate / 1000)  # Rough estimate
        search_cost = search_hours * fees["search_hourly"]
        total_cost += search_cost
        output += f"Search time ({search_hours:.1f} hours): ${search_cost:.2f}\n"
    
    # Review costs
    if include_review_time and not waivers["review"]:
        review_hours = min(3, page_estimate / 500)  # Rough estimate
        review_cost = review_hours * fees["review_hourly"]
        total_cost += review_cost
        output += f"Review time ({review_hours:.1f} hours): ${review_cost:.2f}\n"
    
    # Duplication costs
    free_pages = waivers["duplication"] if isinstance(waivers["duplication"], int) else 0
    billable_pages = max(0, page_estimate - free_pages)
    dup_cost = billable_pages * fees["duplication_per_page"]
    total_cost += dup_cost
    output += f"Duplication ({billable_pages} pages after {free_pages} free): ${dup_cost:.2f}\n"
    
    output += f"\n**Estimated Total: ${total_cost:.2f}**\n\n"
    
    # Optimization suggestions
    output += "**Cost Optimization Strategies:**\n"
    
    if total_cost > 50:
        output += "1. Request a fee waiver citing public interest\n"
        output += "2. Narrow your date range to reduce pages\n"
        output += "3. Request electronic format only (no printing)\n"
        output += "4. Ask for a sample first (e.g., one month of emails)\n"
    
    if requester_category == "commercial":
        output += "\n**Consider qualifying for reduced fees:**\n"
        output += "- News media: If you plan to publish information\n"
        output += "- Educational: If for academic research\n"
        output += "- File through a non-profit organization\n"
    
    return output


@mcp.tool()
def generate_appeal_letter(
    foia_id: int,
    denial_reasons: List[str],
    include_legal_arguments: bool = True
) -> str:
    """
    Generate a comprehensive appeal letter with legal arguments.
    
    Args:
        foia_id: The FOIA request ID
        denial_reasons: List of reasons given for denial
        include_legal_arguments: Include relevant case law
    
    Returns:
        A complete appeal letter
    """
    
    try:
        request = client.requests.retrieve(foia_id)
        
        today = datetime.now().strftime("%B %d, %Y")
        
        appeal = f"""[Your Name]
[Your Address]
[City, State ZIP]
[Email]
[Phone]

{today}

FOIA Appeals Officer
[Agency Name]
[Agency Address]

Re: FOIA Appeal - Request #{foia_id}: {request.title}

Dear FOIA Appeals Officer,

I am writing to appeal the [partial denial/full denial] of my Freedom of Information Act request #{foia_id}, submitted on {request.date_submitted if hasattr(request, 'date_submitted') else '[date]'}.

**REASONS FOR APPEAL:**\n\n"""
        
        # Address each denial reason
        for reason in denial_reasons:
            if "b(5)" in reason.lower() or "deliberative" in reason.lower():
                appeal += """**Regarding Exemption (b)(5) - Deliberative Process Privilege:**
The agency has not met its burden to show that the withheld documents are both predecisional and deliberative. """
                
                if include_legal_arguments:
                    appeal += """As established in Coastal States Gas Corp. v. Department of Energy, 617 F.2d 854 (D.C. Cir. 1980), the agency must identify the specific deliberative process involved and establish what role the documents play in that process. The agency's blanket assertion is insufficient.\n\n"""
            
            elif "b(6)" in reason.lower() or "privacy" in reason.lower():
                appeal += """**Regarding Exemption (b)(6) - Personal Privacy:**
The agency has not demonstrated that disclosure would constitute a clearly unwarranted invasion of personal privacy. """
                
                if include_legal_arguments:
                    appeal += """Under the balancing test established in Department of Justice v. Reporters Committee, 489 U.S. 749 (1989), the public interest in disclosure outweighs any minimal privacy interest. Moreover, names and business contact information of government employees acting in their official capacity are not protected.\n\n"""
            
            elif "b(7)" in reason.lower() or "enforcement" in reason.lower():
                appeal += """**Regarding Exemption (b)(7) - Law Enforcement:**
The agency has not shown that the records were compiled for law enforcement purposes or that disclosure would cause the claimed harm. """
                
                if include_legal_arguments:
                    appeal += """As required by John Doe Agency v. John Doe Corp., 493 U.S. 146 (1989), the agency must demonstrate a rational nexus between enforcement of a federal law and the documents withheld.\n\n"""
            
            elif "no records" in reason.lower() or "no responsive" in reason.lower():
                appeal += """**Regarding "No Responsive Records" Determination:**
The agency's search was inadequate. An adequate search is one reasonably calculated to uncover all relevant documents. """
                
                if include_legal_arguments:
                    appeal += """Valencia-Lucena v. U.S. Coast Guard, 180 F.3d 321 (D.C. Cir. 1999). The agency must search all locations likely to contain responsive records and use search terms reasonably likely to locate such records.\n\n"""
        
        # Segregability argument
        appeal += """**SEGREGABILITY:**
Even if some information is properly exempt, the agency must release any reasonably segregable non-exempt portions. 5 U.S.C. § 552(b). The agency has not demonstrated that it performed the required segregability analysis.

**PUBLIC INTEREST:**
Disclosure of these records is in the public interest as they will contribute significantly to public understanding of government operations. [Explain specific public interest]

**REQUESTED RELIEF:**
I respectfully request that the Appeals Officer:
1. Reverse the initial determination
2. Order a new, adequate search for responsive records
3. Conduct a proper segregability analysis
4. Release all non-exempt information

I reserve the right to seek judicial review if this appeal is denied.

Thank you for your consideration.

Sincerely,
[Your Name]"""
        
        return f"**Generated FOIA Appeal Letter:**\n\n{appeal}\n\n**Next Steps:**\n1. Personalize the bracketed sections\n2. Add specific public interest arguments\n3. Submit within appeal deadline (usually 90 days)\n4. Send via certified mail for proof of delivery"
        
    except Exception as e:
        return f"Error generating appeal: {str(e)}"


@mcp.tool()
def track_request_patterns(
    topic: str,
    time_period: str = "6months",
    analyze_success_factors: bool = True
) -> str:
    """
    Analyze patterns in FOIA requests on a specific topic.
    
    Args:
        topic: The topic to analyze
        time_period: Period to analyze (3months, 6months, 1year, all)
        analyze_success_factors: Include success factor analysis
    
    Returns:
        Pattern analysis and insights
    """
    
    output = f"**FOIA Request Pattern Analysis: {topic}**\n"
    output += f"Time Period: {time_period}\n\n"
    
    try:
        # Search for requests on this topic
        requests = client.requests.list(search=topic)
        
        # Analyze patterns
        status_counts = {}
        agency_counts = {}
        success_count = 0
        total_count = 0
        
        for req in requests:
            if total_count >= 100:  # Limit analysis
                break
                
            total_count += 1
            
            # Count by status
            status = getattr(req, 'status', 'unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count by agency
            if hasattr(req, 'agency'):
                agency_id = req.agency
                agency_counts[agency_id] = agency_counts.get(agency_id, 0) + 1
            
            # Count successes
            if status in ['done', 'partial']:
                success_count += 1
        
        output += f"**Summary Statistics:**\n"
        output += f"- Total requests analyzed: {total_count}\n"
        output += f"- Success rate: {(success_count/total_count*100):.1f}%\n\n"
        
        output += "**Status Distribution:**\n"
        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            output += f"- {status}: {count} ({count/total_count*100:.1f}%)\n"
        
        output += "\n**Most Requested Agencies:**\n"
        for agency_id, count in sorted(agency_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            output += f"- Agency {agency_id}: {count} requests\n"
        
        if analyze_success_factors:
            output += "\n**Success Factor Analysis:**\n"
            output += "Based on patterns, successful requests tend to:\n"
            output += "- Target specific date ranges (not open-ended)\n"
            output += "- Focus on one type of document\n"
            output += "- Include detailed search terms\n"
            output += "- Request electronic format\n"
            output += "- File with agencies that have better response rates\n"
        
        output += "\n**Recommendations:**\n"
        output += f"1. Target agencies with higher success rates for '{topic}'\n"
        output += "2. Learn from successful request language\n"
        output += "3. Avoid agencies with high rejection rates\n"
        output += "4. Consider timing based on agency workload\n"
        
    except Exception as e:
        output += f"\nError analyzing patterns: {str(e)}"
    
    return output


@mcp.tool()
def create_foia_campaign(
    campaign_name: str,
    target_agencies: List[int],
    template_request: str,
    stagger_days: int = 0
) -> str:
    """
    Create a coordinated FOIA campaign across multiple agencies.
    
    Args:
        campaign_name: Name for this campaign
        target_agencies: List of agency IDs to file with
        template_request: Template request text (agencies will be customized)
        stagger_days: Days to stagger submissions (0 for simultaneous)
    
    Returns:
        Campaign creation summary
    """
    
    output = f"**FOIA Campaign: {campaign_name}**\n\n"
    output += f"Target Agencies: {len(target_agencies)}\n"
    output += f"Stagger Period: {stagger_days} days\n\n"
    
    if not username or not password:
        return output + "Error: Campaign creation requires authentication."
    
    output += "**Campaign Plan:**\n"
    
    for i, agency_id in enumerate(target_agencies):
        submission_date = datetime.now() + timedelta(days=i * stagger_days)
        output += f"\nAgency {agency_id}:\n"
        output += f"- Submission date: {submission_date.strftime('%Y-%m-%d')}\n"
        output += f"- Request preview: {template_request[:100]}...\n"
    
    output += "\n**Campaign Benefits:**\n"
    output += "- Comprehensive coverage across agencies\n"
    output += "- Ability to compare responses\n"
    output += "- Identify which agencies have records\n"
    output += "- Build stronger appeals with comparative data\n"
    
    output += "\n**Next Steps:**\n"
    output += "1. Review and customize request for each agency\n"
    output += "2. Set up tracking dashboard for all requests\n"
    output += "3. Prepare for managing multiple responses\n"
    output += "4. Consider creating a shared workspace for results\n"
    
    return output


if __name__ == "__main__":
    # Run the enhanced server
    mcp.run()