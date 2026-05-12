#!/usr/bin/env python3

# Test the core voting functionality by examining the exact issue
import requests
import json

base_url = "http://localhost:5000"

def test_core_voting_issue():
    """Test the core voting issue by examining what's happening"""
    
    session = requests.Session()
    
    print("=== Core Voting Issue Analysis ===\n")
    
    # Step 1: Check what happens when we access vote page
    print("1. Accessing vote page without authentication...")
    response = session.get(f"{base_url}/voter/vote", allow_redirects=False)
    print(f"   Status: {response.status_code}")
    if response.status_code == 302:
        print(f"   Redirected to: {response.headers.get('Location')}")
    
    # Step 2: Check login page
    print("\n2. Checking login page...")
    response = session.get(f"{base_url}/login")
    print(f"   Login page status: {response.status_code}")
    
    # Step 3: Try password login
    print("\n3. Password login...")
    login_data = {
        'virtual_voter_id': 'VV-2025-85113',
        'password': '12345678'
    }
    
    response = session.post(
        f"{base_url}/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Login status: {response.status_code}")
    if response.status_code == 200:
        print(f"   Login response: {response.json()}")
    
    # Step 4: Check session cookies
    print(f"\n4. Session cookies after login:")
    for cookie in session.cookies:
        print(f"   {cookie.name}: {cookie.value[:50]}...")
    
    # Step 5: Try to access vote page again
    print("\n5. Accessing vote page after password login...")
    response = session.get(f"{base_url}/voter/vote")
    print(f"   Status: {response.status_code}")
    print(f"   URL: {response.url}")
    
    # Step 6: Try to cast vote without face auth
    print("\n6. Attempting to cast vote...")
    vote_data = {
        "candidate_id": 11,
        "election_id": 10
    }
    
    response = session.post(
        f"{base_url}/voter/cast-vote",
        json=vote_data,
        headers={"Content-Type": "application/json"},
        allow_redirects=False  # Don't follow redirects
    )
    
    print(f"   Vote status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location', 'No redirect')}")
    
    if response.status_code == 302:
        print(f"   Redirected to: {response.headers.get('Location')}")
        # Follow the redirect manually
        redirect_url = response.headers.get('Location')
        if redirect_url:
            if redirect_url.startswith('/'):
                redirect_url = base_url + redirect_url
            redirect_response = session.get(redirect_url)
            print(f"   Redirect response status: {redirect_response.status_code}")
            print(f"   Redirect response type: {redirect_response.headers.get('content-type', 'unknown')}")
    
    # Step 7: Check what the actual issue is
    print("\n7. Analysis:")
    print("   The issue is that the voting system requires full authentication.")
    print("   Even though we can access the vote page after password login,")
    print("   the cast_vote endpoint still requires complete authentication.")
    print("   The 'Please select a candidate' error occurs when candidate_id is None,")
    print("   which happens when the request is redirected to login.")

if __name__ == "__main__":
    test_core_voting_issue()