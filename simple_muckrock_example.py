#!/usr/bin/env python3
"""
Simple MuckRock API example without MCP Agent framework dependencies.
This can run with just the python-muckrock package installed.
"""

import os
from muckrock import MuckRock


def main():
    """Simple example of using the MuckRock Python wrapper."""
    
    # Initialize MuckRock client
    # You need to provide username and password for authenticated access
    username = os.getenv("MUCKROCK_USERNAME")
    password = os.getenv("MUCKROCK_PASSWORD")
    
    if username and password:
        print("Using authenticated MuckRock access")
        client = MuckRock(username, password)
    else:
        print("Note: MuckRock API requires authentication. Set MUCKROCK_USERNAME and MUCKROCK_PASSWORD environment variables.")
        print("Attempting to proceed with anonymous access (may have limitations)...")
        client = MuckRock()
    
    print("\n1. Searching for police-related FOIA requests...")
    print("-" * 60)
    
    try:
        # Search for FOIA requests
        request_list = client.requests.list(search="police")
        
        count = 0
        first_foia_id = None
        for request in request_list:
            count += 1
            print(f"\n{count}. {request.title}")
            print(f"   Status: {request.status}")
            print(f"   Agency: {request.agency if hasattr(request, 'agency') else 'Unknown'}")
            print(f"   User: {request.user if hasattr(request, 'user') else 'Unknown'}")
            print(f"   ID: {request.id}")
            
            # Get first request ID for detailed view
            if count == 1:
                first_foia_id = request.id
            
            # Limit to 5 results
            if count >= 5:
                break
    
    except Exception as e:
        print(f"Error searching FOIA requests: {e}")
        first_foia_id = None
    
    # Get details of a specific request
    if first_foia_id:
        print(f"\n\n2. Getting details for FOIA request #{first_foia_id}...")
        print("-" * 60)
        
        try:
            detailed_request = client.requests.retrieve(first_foia_id)
            print(f"Title: {detailed_request.title}")
            print(f"Status: {detailed_request.status}")
            print(f"ID: {detailed_request.id}")
            
            if hasattr(detailed_request, 'requested_docs'):
                print(f"\nRequested Documents: {detailed_request.requested_docs[:300]}...")
            
            # Get communications if available
            try:
                comms_list = detailed_request.get_communications()
                if comms_list:
                    print(f"\nCommunications ({len(comms_list)} total):")
                    for comm in comms_list[:2]:
                        print(f"\n  Communication: {str(comm)[:150]}...")
            except:
                print("\nCommunications: Unable to retrieve")
        
        except Exception as e:
            print(f"Error getting FOIA details: {e}")
    
    print("\n\n3. Searching for agencies in California...")
    print("-" * 60)
    
    try:
        agencies = client.agencies.list(search="California")
        
        count = 0
        for agency in agencies:
            count += 1
            print(f"\n{count}. {agency.name if hasattr(agency, 'name') else str(agency)}")
            if hasattr(agency, 'id'):
                print(f"   ID: {agency.id}")
            
            # Limit to 5 results
            if count >= 5:
                break
    
    except Exception as e:
        print(f"Error searching agencies: {e}")
    
    # Note: The newer API may not have direct jurisdiction endpoint access
    print("\n\n4. Additional Information")
    print("-" * 60)
    print("\nFor more advanced usage, you can:")
    print("- File new FOIA requests using client.requests.create()")
    print("- Get communications for a request using request.get_communications()")
    print("- Download files from communications")
    print("\nRefer to the python-muckrock documentation for more details.")
    
    print("\n\nExample complete!")


if __name__ == "__main__":
    main()