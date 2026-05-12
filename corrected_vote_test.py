#!/usr/bin/env python3

import requests
import json
import time

# Test the complete voting functionality with authentication
base_url = "http://localhost:5000"

def test_voting_flow():
    """Test the complete voting flow with authentication"""
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("=== Testing Voting Flow ===\n")
    
    # Step 1: Try to access vote page without authentication
    print("1. Testing vote page access without authentication...")
    try:
        response = session.get(f"{base_url}/voter/vote", allow_redirects=False)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print(f"   Redirected to: {response.headers.get('Location', 'Unknown')}")
            print("   ✓ Correctly requires authentication")
        else:
            print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 2: Login as a voter using the correct API endpoint
    print("\n2. Logging in as voter...")
    try:
        # Use the correct API endpoint for voter login
        login_data = {
            'virtual_voter_id': 'VV-2025-85113',  # Virtual ID from our test
            'password': '12345678'
        }
        
        response = session.post(
            f"{base_url}/auth/login", 
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Login status: {response.status_code}")
        
        if response.status_code == 200:
            login_response = response.json()
            print(f"   ✓ Login successful: {login_response.get('message', 'Success')}")
            print(f"   Token received: {login_response.get('access_token', 'No token')[:20]}...")
        else:
            print(f"   ✗ Login failed: {response.text[:200]}...")
            
    except Exception as e:
        print(f"   Error during login: {e}")
    
    # Step 3: Access vote page after authentication
    print("\n3. Testing vote page access after authentication...")
    try:
        response = session.get(f"{base_url}/voter/vote")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Vote page accessible")
            # Check if candidates are shown
            if "candidate" in response.text.lower():
                print("   ✓ Candidates displayed on page")
                # Count candidates
                candidate_count = response.text.lower().count("vote for")
                print(f"   Found {candidate_count} candidates")
            else:
                print("   ? No candidates found on page")
        else:
            print(f"   ✗ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 4: Test cast-vote endpoint with invalid candidate
    print("\n4. Testing cast-vote with invalid candidate...")
    try:
        response = session.post(
            f"{base_url}/voter/cast-vote",
            json={"candidate_id": 999, "election_id": 1},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            response_data = response.json()
            print(f"   ✓ Correctly rejected invalid candidate: {response_data.get('error', 'Unknown error')}")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 5: Test cast-vote with valid candidate
    print("\n5. Testing cast-vote with valid candidate...")
    try:
        response = session.post(
            f"{base_url}/voter/cast-vote",
            json={"candidate_id": 11, "election_id": 1},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            response_data = response.json()
            print(f"   ✓ Vote cast successfully!")
            print(f"   Block hash: {response_data.get('block_hash', 'N/A')}")
            print(f"   Block index: {response_data.get('block_index', 'N/A')}")
        elif response.status_code == 400:
            response_data = response.json()
            print(f"   ✗ Vote failed: {response_data.get('error', 'Unknown error')}")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Step 6: Test voting again (should fail)
    print("\n6. Testing duplicate vote prevention...")
    try:
        response = session.post(
            f"{base_url}/voter/cast-vote",
            json={"candidate_id": 15, "election_id": 1},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            response_data = response.json()
            if "already voted" in response_data.get('error', '').lower():
                print(f"   ✓ Correctly prevented duplicate vote: {response_data.get('error')}")
            else:
                print(f"   ? Unexpected error: {response_data.get('error')}")
        else:
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_voting_flow()