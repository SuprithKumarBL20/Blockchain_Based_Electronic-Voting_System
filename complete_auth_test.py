#!/usr/bin/env python3

import requests
import json
import base64
import time

# Test the complete authentication flow including OTP
base_url = "http://localhost:5000"

def test_complete_auth_flow():
    """Test the complete authentication flow"""
    
    session = requests.Session()
    
    print("=== Complete Authentication Flow ===\n")
    
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
    
    # Step 2: Try face authentication with a real image
    print("\n2. Face authentication...")
    
    # Create a simple base64 encoded image (1x1 pixel)
    # This is just to test the flow - it will likely fail but we need to try
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
        otp_code = face_response.get('otp_code')
        print(f"   OTP Code: {otp_code}")
        
        # Step 3: OTP verification
        print("\n3. OTP verification...")
        otp_data = {
            'otp_code': otp_code
        }
        
        response = session.post(
            f"{base_url}/auth/otp-verify",
            json=otp_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            otp_response = response.json()
            print(f"   Message: {otp_response.get('message', 'Success')}")
            print(f"   Access token: {otp_response.get('access_token', 'N/A')[:20]}...")
            
            # Step 4: Test vote casting
            print("\n4. Testing vote casting...")
            vote_data = {
                "candidate_id": 11,
                "election_id": 10
            }
            
            response = session.post(
                f"{base_url}/voter/cast-vote",
                json=vote_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Vote status: {response.status_code}")
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"   ✓ Vote successful!")
                    print(f"   Block hash: {result.get('block_hash', 'N/A')}")
                except:
                    print(f"   Raw response: {response.text[:200]}")
            else:
                try:
                    error = response.json()
                    print(f"   ✗ Vote failed: {error.get('error', 'Unknown error')}")
                except:
                    print(f"   Raw error: {response.text[:200]}")
        else:
            print(f"   OTP verification failed: {response.text}")
    else:
        print(f"   Face authentication failed: {response.text}")
        # Let's try to proceed anyway to see what happens
        print("\n   Attempting to access vote page despite face auth failure...")
        response = session.get(f"{base_url}/voter/vote")
        print(f"   Vote page status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Can access vote page")
        else:
            print(f"   Redirected to: {response.url}")

if __name__ == "__main__":
    test_complete_auth_flow()