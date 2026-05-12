#!/usr/bin/env python3

import requests
import json
import time

# Test the voting functionality by bypassing face auth and testing the core logic
base_url = "http://localhost:5000"

def test_vote_logic_directly():
    """Test the core vote casting logic by simulating a logged-in session"""
    
    # First, let's check what candidates are available
    print("=== Checking Available Candidates ===")
    
    # Check candidates in database
    from database.models import Candidate, Election
    from app import app
    
    with app.app_context():
        candidates = Candidate.query.filter_by(is_active=True).all()
        election = Election.query.filter_by(is_active=True).first()
        
        print(f"Active candidates: {len(candidates)}")
        for candidate in candidates:
            print(f"  - ID: {candidate.id}, Name: {candidate.name}, Party: {candidate.party_name}")
        
        if election:
            print(f"Active election: {election.title} (ID: {election.id})")
            print(f"Election is currently active: {election.is_currently_active()}")
        else:
            print("No active election found!")
    
    # Now let's manually test the vote casting logic
    print("\n=== Testing Vote Casting Logic ===")
    
    # Test with a simple POST request to see the exact error
    test_data = {
        "candidate_id": 11,
        "election_id": 1
    }
    
    print(f"Testing with data: {test_data}")
    
    # Try different content types to see if that makes a difference
    headers_list = [
        {"Content-Type": "application/json"},
        {"Content-Type": "application/x-www-form-urlencoded"},
        {"Content-Type": "multipart/form-data"}
    ]
    
    for i, headers in enumerate(headers_list):
        print(f"\nTest {i+1}: {headers['Content-Type']}")
        
        if 'json' in headers['Content-Type']:
            data = json.dumps(test_data)
        else:
            data = test_data
        
        try:
            response = requests.post(
                f"{base_url}/voter/cast-vote",
                data=data,
                headers=headers
            )
            
            print(f"  Status: {response.status_code}")
            print(f"  Response type: {response.headers.get('content-type', 'unknown')}")
            
            if 'json' in response.headers.get('content-type', ''):
                try:
                    result = response.json()
                    print(f"  JSON response: {result}")
                except:
                    print(f"  Raw response: {response.text[:200]}")
            else:
                print(f"  HTML response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_vote_logic_directly()