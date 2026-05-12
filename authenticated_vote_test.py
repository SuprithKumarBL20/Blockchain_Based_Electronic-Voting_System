#!/usr/bin/env python3

import requests
import json
import base64

# Test the voting functionality by properly authenticating and then voting
base_url = "http://localhost:5000"

def test_complete_voting_flow():
    """Test the complete voting flow with proper authentication"""
    
    session = requests.Session()
    
    print("=== Complete Voting Flow Test ===\n")
    
    # Step 1: Password authentication
    print("1. Password authentication...")
    login_data = {
        'virtual_voter_id': 'VV-2025-85113',
        'password': '12345678'
    }
    
    response = session.post(
        f"{base_url}/auth/login", 
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Login failed: {response.text}")
        return
    
    login_response = response.json()
    print(f"   Message: {login_response.get('message', 'Success')}")
    
    # Step 2: Try to bypass face authentication by directly accessing vote page
    print("\n2. Accessing vote page...")
    response = session.get(f"{base_url}/voter/vote")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        # Check if we can see candidates
        if "candidate" in response.text.lower():
            print("   ✓ Vote page loaded successfully")
            # Count candidates
            candidate_count = response.text.lower().count("vote for")
            print(f"   Found {candidate_count} candidates on page")
        else:
            print("   ✗ No candidates found on page")
    
    # Step 3: Test vote casting with proper authentication
    print("\n3. Testing vote casting...")
    
    # Use the correct election ID (10) and candidate ID (11)
    vote_data = {
        "candidate_id": 11,
        "election_id": 10  # Correct election ID from our earlier check
    }
    
    print(f"   Sending vote data: {vote_data}")
    
    response = session.post(
        f"{base_url}/voter/cast-vote",
        json=vote_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"   ✓ Vote successful!")
            print(f"   Block hash: {result.get('block_hash', 'N/A')}")
            print(f"   Block index: {result.get('block_index', 'N/A')}")
        except Exception as e:
            print(f"   Failed to parse JSON: {e}")
            print(f"   Raw response: {response.text[:300]}")
    elif response.status_code == 400:
        try:
            error = response.json()
            print(f"   ✗ Vote failed: {error.get('error', 'Unknown error')}")
        except:
            print(f"   Raw error: {response.text[:300]}")
    else:
        print(f"   Unexpected status: {response.status_code}")
        print(f"   Response: {response.text[:300]}")
    
    # Step 4: Test duplicate vote prevention
    print("\n4. Testing duplicate vote prevention...")
    response = session.post(
        f"{base_url}/voter/cast-vote",
        json=vote_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 400:
        try:
            error = response.json()
            print(f"   ✓ Correctly prevented duplicate vote: {error.get('error', 'Unknown error')}")
        except:
            print(f"   Raw error: {response.text[:300]}")

if __name__ == "__main__":
    test_complete_voting_flow()