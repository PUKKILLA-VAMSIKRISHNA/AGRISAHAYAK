#!/usr/bin/env python3
"""
Debug script for static file serving issues
"""

import requests
import os

def test_static_files():
    """Test static file serving"""
    
    base_url = "https://agrisahayak.vercel.app"
    
    print("Testing static file serving...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test static files
    static_files = [
        "/static/css/style.css",
        "/static/js/chat.js",
        "/static/js/voice.js",
        "/static/js/main.js",
        "/static/images/favicon.ico"
    ]
    
    for file_path in static_files:
        try:
            response = requests.get(f"{base_url}{file_path}", timeout=10)
            print(f"{file_path}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✅ Success - Content length: {len(response.content)} bytes")
            else:
                print(f"  ❌ Failed - Response: {response.text[:100]}...")
        except Exception as e:
            print(f"{file_path}: Error - {e}")
    
    print("\n" + "=" * 50)
    print("If static files are returning 404, the chat and voice won't work.")
    print("This is likely a Vercel configuration issue.")

if __name__ == "__main__":
    test_static_files() 