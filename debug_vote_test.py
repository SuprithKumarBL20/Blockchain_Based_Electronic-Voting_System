#!/usr/bin/env python3

import requests
import json
import base64
import time

# Test the voting functionality with proper authentication flow
base_url = "http://localhost:5000"

def test_voting_with_face_auth():
    """Test the complete voting flow including face authentication"""
    
    session = requests.Session()
    
    print("=== Testing Complete Voting Flow ===\n")
    
    # Step 1: Login with password
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
    if response.status_code == 200:
        login_response = response.json()
        print(f"   Message: {login_response.get('message', 'Success')}")
        print(f"   Next step: {login_response.get('next_step', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
        return
    
    # Step 2: Face authentication (simulate with a dummy image)
    print("\n2. Face authentication...")
    
    # Create a dummy base64 image (1x1 transparent PNG)
    dummy_image = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    face_auth_data = {
        'face_image': dummy_image
    }
    
    response = session.post(
        f"{base_url}/auth/face-auth",
        json=face_auth_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        face_response = response.json()
        print(f"   Message: {face_response.get('message', 'Success')}")
        print(f"   OTP: {face_response.get('otp', 'N/A')}")
    else:
        print(f"   Error: {response.text}")
        # Continue anyway for testing
    
    # Step 3: Test vote casting with different candidate IDs
    print("\n3. Testing vote casting...")
    
    # Test with candidate ID 11 (Varsha, BJP)
    test_data = {
        "candidate_id": 11,
        "election_id": 1
    }
    
    print(f"   Testing with data: {test_data}")
    response = session.post(
        f"{base_url}/voter/cast-vote",
        json=test_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        try:
            result = response.json()
            print(f"   Success: {result}")
        except:
            print(f"   Raw response: {response.text[:200]}")
    else:
        try:
            error = response.json()
            print(f"   Error: {error.get('error', 'Unknown error')}")
        except:
            print(f"   Raw error: {response.text[:200]}")

if __name__ == "__main__":
    test_voting_with_face_auth()