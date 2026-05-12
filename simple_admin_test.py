#!/usr/bin/env python3
"""
Simple test for admin login
"""
import requests

base_url = "http://127.0.0.1:5000"

# Test admin login
admin_login = {
    "username": "admin",
    "password": "admin123"
}

print("Testing admin login...")
admin_session = requests.Session()
response = admin_session.post(f"{base_url}/admin/login", json=admin_login)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Admin login successful")
    # Test dashboard access
    dashboard_response = admin_session.get(f"{base_url}/admin/dashboard")
    print(f"Dashboard access: {dashboard_response.status_code}")
    if dashboard_response.status_code == 200:
        print("✅ Admin dashboard accessible")
        # Check for admin content
        if "ADMINISTRATION PORTAL" in dashboard_response.text:
            print("✅ Admin portal content confirmed")
        else:
            print("⚠️  No admin portal content found")
    else:
        print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
else:
    print(f"❌ Admin login failed: {response.status_code}")
    print(f"Response: {response.text}")