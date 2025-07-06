#!/usr/bin/env python3
"""
Test script to verify the fixes for chat and voice functionality
"""

import os
import requests
import json

def test_vercel_deployment():
    """Test the Vercel deployment with the fixes"""
    
    # Your Vercel deployment URL
    base_url = "https://agrisahayak.vercel.app"
    
    print("Testing Vercel deployment with fixes...")
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
    
    # Test 2: Debug page
    print("2. Testing debug page...")
    try:
        response = requests.get(f"{base_url}/debug", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Debug page loads successfully")
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
    
    # Test 4: Chat page
    print("4. Testing chat page...")
    try:
        response = requests.get(f"{base_url}/chat/new", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirecting to login (expected behavior)")
        elif response.status_code == 200:
            print("   ✅ Chat page loads successfully")
        else:
            print(f"   ⚠️  Unexpected status: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 50)
    print("SUMMARY:")
    print("✅ Fixed issues:")
    print("  - Removed onsubmit='return false;' from chat form")
    print("  - Updated Bootstrap CSS and JS to compatible versions")
    print("  - Added dark theme CSS")
    print("  - Improved error handling in JavaScript")
    print("  - Added debug page for troubleshooting")
    print("  - Added API connectivity testing")
    print()
    print("🔧 Next steps:")
    print("1. Deploy these changes to Vercel")
    print("2. Visit /debug to test functionality")
    print("3. Check browser console for any remaining errors")
    print("4. Test chat and voice features")

if __name__ == "__main__":
    test_vercel_deployment() 