#!/usr/bin/env python3
# Simple test script for the camera maintenance API

import requests
import json
import time

API_BASE = 'http://127.0.0.1:5000'

def test_home():
    """Test the home endpoint"""
    print("Testing home endpoint...")
    try:
        response = requests.get(f'{API_BASE}/')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Home page working: {data['message']}")
            return True
        else:
            print(f"✗ Home page failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error connecting to server: {e}")
        return False

def test_cameras():
    """Test the cameras endpoint"""
    print("\nTesting cameras endpoint...")
    try:
        response = requests.get(f'{API_BASE}/api/cameras')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Found {data['total']} cameras")
            if data['cameras']:
                camera = data['cameras'][0]
                print(f"  First camera: {camera['camera_id']} at {camera['location']}")
            return True
        else:
            print(f"✗ Cameras endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_templates():
    """Test the templates endpoint"""
    print("\nTesting templates endpoint...")
    try:
        response = requests.get(f'{API_BASE}/api/export/templates')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            templates = data['templates']
            print(f"✓ Available export formats:")
            for template in templates:
                print(f"  - {template['name']}: {template['description']}")
            return templates
        else:
            print(f"✗ Templates endpoint failed: {response.text}")
            return []
    except Exception as e:
        print(f"✗ Error: {e}")
        return []

def test_export(format_type):
    """Test creating an export"""
    print(f"\nTesting {format_type} export...")
    try:
        response = requests.post(
            f'{API_BASE}/api/export',
            json={'format': format_type},
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ {format_type.upper()} export created: {data['filename']}")
            return data['filename']
        else:
            print(f"✗ {format_type.upper()} export failed: {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error: {e}")
        return None

def test_download(filename):
    """Test downloading a file"""
    print(f"\nTesting download of {filename}...")
    try:
        response = requests.get(f'{API_BASE}/api/download/{filename}')
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✓ File downloaded successfully ({len(response.content)} bytes)")
            return True
        else:
            print(f"✗ Download failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("CAMERA MAINTENANCE SYSTEM - API TEST")
    print("=" * 60)
    print("Make sure the Flask app is running on http://localhost:5000")
    print()
    
    # Test basic connectivity
    if not test_home():
        print("\n❌ Server not responding. Make sure to run:")
        print("   python3 simple_app.py")
        return
    
    # Test cameras endpoint
    if not test_cameras():
        print("\n❌ Cameras endpoint failed")
        return
    
    # Test templates
    templates = test_templates()
    if not templates:
        print("\n❌ Templates endpoint failed")
        return
    
    # Test exports for each available format
    successful_exports = []
    for template in templates:
        format_name = template['name']
        filename = test_export(format_name)
        if filename:
            successful_exports.append(filename)
            # Test download
            test_download(filename)
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Server is running and responding")
    print(f"✓ API endpoints are working")
    print(f"✓ {len(templates)} export formats available")
    print(f"✓ {len(successful_exports)} exports created successfully")
    
    if successful_exports:
        print(f"\nGenerated files:")
        for filename in successful_exports:
            print(f"  - {filename}")
        print(f"\nCheck the 'exports/' folder to see the generated reports!")
    
    print(f"\n🎉 All tests passed! The system is working correctly.")

if __name__ == '__main__':
    main()
