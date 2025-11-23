#!/usr/bin/env python3
"""
Test script for Vercel deployment
"""

import requests
import json
import sys

def test_vercel_deployment():
    """Test the Vercel deployment endpoints"""
    
    # Your Vercel deployment URL
    base_url = "https://agrisahayak.vercel.app"
    
    print("Testing Vercel deployment...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Message: {data.get('message', 'unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Home page
    print("2. Testing home page...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Home page loads successfully")
        else:
            print(f"   ❌ Error: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Static files
    print("3. Testing static files...")
    static_files = [
        '/static/css/style.css',
        '/static/js/main.js',
        '/static/js/chat.js',
        '/static/js/voice.js'
    ]
    
    for static_file in static_files:
        try:
            response = requests.get(f"{base_url}{static_file}", timeout=10)
            print(f"   {static_file}: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ {static_file} loads successfully")
            else:
                print(f"   ❌ {static_file} failed to load")
        except Exception as e:
            print(f"   ❌ Error loading {static_file}: {e}")
    
    print()
    
    # Test 4: API endpoints (will fail without auth, but should return proper error)
    print("4. Testing API endpoints...")
    try:
        # Test send message endpoint
        response = requests.post(
            f"{base_url}/api/send_message",
            json={"chat_id": 1, "message": "test", "language": "en"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Send message API: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirecting to login (expected behavior)")
        elif response.status_code == 401:
            print("   ✅ Unauthorized (expected behavior)")
        else:
            print(f"   ⚠️  Unexpected status: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 5: Database status
    print("5. Testing database status...")
    try:
        response = requests.get(f"{base_url}/db-status", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Database URL set: {data.get('database_url_set', False)}")
            print(f"   Database initialized: {data.get('database_initialized', False)}")
            print(f"   Environment: {data.get('environment', 'unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    print("=" * 50)
    print("SUMMARY:")
    print("If all tests pass, your deployment is working correctly.")
    print("If you see errors, check the Vercel deployment guide.")
    print("Make sure environment variables are set in Vercel dashboard.")

if __name__ == "__main__":
    test_vercel_deployment() 