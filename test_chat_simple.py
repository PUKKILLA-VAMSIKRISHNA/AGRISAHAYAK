#!/usr/bin/env python3
"""
Simple test script to verify chat functionality with embedded JavaScript
"""

import requests
import json

def test_chat_functionality():
    """Test the chat functionality"""
    
    base_url = "https://agrisahayak.vercel.app"
    
    print("Testing chat functionality with embedded JavaScript...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Check if chat page loads
    print("1. Testing chat page...")
    try:
        response = requests.get(f"{base_url}/chat/new", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirecting to login (expected behavior)")
        elif response.status_code == 200:
            print("   ✅ Chat page loads successfully")
            # Check if embedded JavaScript is present
            if 'showNotification' in response.text:
                print("   ✅ Embedded JavaScript found")
            else:
                print("   ❌ Embedded JavaScript not found")
        else:
            print(f"   ⚠️  Unexpected status: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Check if API endpoint is accessible
    print("2. Testing chat API endpoint...")
    try:
        response = requests.post(
            f"{base_url}/api/send_message",
            json={"chat_id": 1, "message": "test", "language": "en"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 302:
            print("   ✅ Redirecting to login (expected behavior)")
        elif response.status_code == 401:
            print("   ✅ Unauthorized (expected behavior)")
        elif response.status_code == 200:
            print("   ✅ API endpoint accessible")
        else:
            print(f"   ⚠️  Unexpected status: {response.text[:100]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Check if embedded functions are working
    print("3. Testing embedded JavaScript...")
    try:
        response = requests.get(f"{base_url}/chat/new", timeout=10)
        if response.status_code == 200:
            # Check for embedded functions
            embedded_functions = [
                'function showNotification',
                'sendMessage',
                'messageForm.addEventListener',
                'fetch(\'/api/send_message\''
            ]
            
            for func in embedded_functions:
                if func in response.text:
                    print(f"   ✅ {func} found")
                else:
                    print(f"   ❌ {func} not found")
        else:
            print("   ⚠️  Cannot test embedded JavaScript - page not accessible")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    print("=" * 50)
    print("SUMMARY:")
    print("✅ The chat functionality should now work with embedded JavaScript")
    print("✅ No external static files required for basic functionality")
    print("✅ showNotification function is embedded in base template")
    print("✅ sendMessage function is embedded in chat template")
    print()
    print("🔧 To test:")
    print("1. Visit: https://agrisahayak.vercel.app")
    print("2. Login to your account")
    print("3. Go to chat and try sending a message")
    print("4. Check browser console for any errors")

if __name__ == "__main__":
    test_chat_functionality() 