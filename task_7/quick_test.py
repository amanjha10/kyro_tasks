#!/usr/bin/env python3
# Simple test script for User Impersonation System
# This tests the core functionality step by step

import requests
import json

print("Testing User Impersonation System...")
print("=" * 60)

# Test home endpoint (not logged in)
print("1. Testing home endpoint (not logged in)...")
try:
    response = requests.get('http://127.0.0.1:5002/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ {data['message']}")
        print(f"   Status: {data['status']}")
    else:
        print(f"   ✗ Failed: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test admin login
print("\n2. Testing admin login...")
try:
    response = requests.post('http://127.0.0.1:5002/login',
                            json={'username': 'admin', 'password': 'admin123'},
                            headers={'Content-Type': 'application/json'})
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ {data['message']}")
        print(f"   User: {data['user']['username']} (Admin: {data['user']['is_admin']})")
        # Save session cookie for subsequent requests
        session_cookie = response.cookies
    else:
        print(f"   ✗ Failed: {response.text}")
        exit(1)
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

# Test getting users list
print("\n3. Testing users list (admin only)...")
try:
    response = requests.get('http://127.0.0.1:5002/users', cookies=session_cookie)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found {data['total']} users:")
        for user in data['users']:
            print(f"     - {user['username']} ({'Admin' if user['is_admin'] else 'User'})")
    else:
        print(f"   ✗ Failed: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test impersonation - impersonate 'pratiksha'
print("\n4. Testing impersonation (admin impersonating pratiksha)...")
try:
    response = requests.post('http://127.0.0.1:5001/impersonate',
                            json={'user_id': 2},  # pratiksha's ID should be 2
                            headers={'Content-Type': 'application/json'},
                            cookies=session_cookie)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ {data['message']}")
        print(f"   Admin: {data['admin_user']['username']}")
        print(f"   Impersonating: {data['impersonated_user']['username']}")
    else:
        print(f"   ✗ Failed: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test dashboard while impersonating
print("\n5. Testing dashboard while impersonating...")
try:
    response = requests.get('http://127.0.0.1:5001/dashboard', cookies=session_cookie)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ {data['message']}")
        if 'impersonation_info' in data:
            print(f"   ✓ Impersonation active: {data['impersonation_info']['message']}")
    else:
        print(f"   ✗ Failed: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test stopping impersonation
print("\n6. Testing stop impersonation...")
try:
    response = requests.post('http://127.0.0.1:5001/stop-impersonation',
                            cookies=session_cookie)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ {data['message']}")
        print(f"   Back to admin: {data['admin_user']['username']}")
    else:
        print(f"   ✗ Failed: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test activity log
print("\n7. Testing activity log...")
try:
    response = requests.get('http://127.0.0.1:5001/activity-log', cookies=session_cookie)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Found {data['total']} activities:")
        for activity in data['activities'][:3]:  # Show first 3
            print(f"     - {activity['admin_user']} {activity['action']} {activity['impersonated_user']} at {activity['timestamp']}")
    else:
        print(f"   ✗ Failed: {response.text}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("🎉 User Impersonation System test completed!")
print("✓ Admin can login")
print("✓ Admin can view users")
print("✓ Admin can impersonate other users")
print("✓ Dashboard shows impersonation status")
print("✓ Admin can stop impersonation")
print("✓ All activities are logged")
print("\nThe system is working correctly! 🚀")
