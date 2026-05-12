#!/usr/bin/env python3

import requests
import json

# Test the voting functionality
base_url = "http://localhost:5000"

# First, let's check if we can access the vote page without login
print("Testing vote page access...")
try:
    response = requests.get(f"{base_url}/voter/vote")
    print(f"Vote page status: {response.status_code}")
    if response.status_code == 200:
        print("Vote page accessible")
    else:
        print(f"Vote page redirected to: {response.url}")
except Exception as e:
    print(f"Error accessing vote page: {e}")

# Test the cast-vote endpoint directly
print("\nTesting cast-vote endpoint...")
try:
    # Test with invalid candidate ID
    response = requests.post(
        f"{base_url}/voter/cast-vote",
        json={"candidate_id": 999, "election_id": 1},
        headers={"Content-Type": "application/json"}
    )
    print(f"Cast vote response status: {response.status_code}")
    print(f"Cast vote response: {response.text[:200]}...")
except Exception as e:
    print(f"Error testing cast-vote: {e}")

# Test with valid candidate ID but no authentication
print("\nTesting with valid candidate ID...")
try:
    response = requests.post(
        f"{base_url}/voter/cast-vote",
        json={"candidate_id": 11, "election_id": 1},
        headers={"Content-Type": "application/json"}
    )
    print(f"Valid candidate response status: {response.status_code}")
    print(f"Valid candidate response: {response.text[:200]}...")
except Exception as e:
    print(f"Error testing valid candidate: {e}")

print("\nTest completed.")