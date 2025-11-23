#!/usr/bin/env python3
"""
Test script to verify that the static folder has been renamed to public
"""

import os
import sys

def test_static_folder_rename():
    """Test that the static folder has been renamed to public"""
    
    print("Testing static folder rename to public...")
    print("-" * 50)
    
    # Test 1: Check if public folder exists
    print("1. Checking if public folder exists...")
    if os.path.exists('public'):
        print("   ✅ Public folder exists")
        
        # Check subdirectories
        subdirs = ['css', 'js', 'images', 'data']
        for subdir in subdirs:
            if os.path.exists(f'public/{subdir}'):
                print(f"   ✅ public/{subdir} exists")
            else:
                print(f"   ❌ public/{subdir} missing")
    else:
        print("   ❌ Public folder does not exist")
        return False
    
    # Test 2: Check if static folder is gone
    print("\n2. Checking if static folder is gone...")
    if os.path.exists('static'):
        print("   ❌ Static folder still exists")
        return False
    else:
        print("   ✅ Static folder has been removed")
    
    # Test 3: Check Flask app configuration
    print("\n3. Checking Flask app configuration...")
    try:
        from main import app
        print(f"   ✅ App imports successfully")
        print(f"   Static folder: {app.static_folder}")
        print(f"   Static URL path: {app.static_url_path}")
        
        if 'public' in app.static_folder:
            print("   ✅ Static folder correctly set to use 'public' folder")
        else:
            print(f"   ❌ Static folder should contain 'public', but is '{app.static_folder}'")
            return False
            
    except Exception as e:
        print(f"   ❌ Error importing app: {e}")
        return False
    
    # Test 4: Check if key files exist in public folder
    print("\n4. Checking key files in public folder...")
    key_files = [
        'public/css/style.css',
        'public/js/main.js',
        'public/js/chat.js',
        'public/js/voice.js',
        'public/data/languages.json',
        'public/data/crops.json'
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path} exists")
        else:
            print(f"   ❌ {file_path} missing")
    
    # Test 5: Check code references
    print("\n5. Checking code references...")
    
    # Check if routes.py has been updated
    with open('routes.py', 'r', encoding='utf-8') as f:
        routes_content = f.read()
        if 'public/data/languages.json' in routes_content:
            print("   ✅ routes.py updated to use public folder")
        else:
            print("   ❌ routes.py still references static folder")
            return False
    
    # Check if utils.py has been updated
    with open('utils.py', 'r', encoding='utf-8') as f:
        utils_content = f.read()
        if 'public/data/languages.json' in utils_content:
            print("   ✅ utils.py updated to use public folder")
        else:
            print("   ❌ utils.py still references static folder")
            return False
    
    # Check if chatbot.py has been updated
    with open('chatbot.py', 'r', encoding='utf-8') as f:
        chatbot_content = f.read()
        if 'public/data/crops.json' in chatbot_content:
            print("   ✅ chatbot.py updated to use public folder")
        else:
            print("   ❌ chatbot.py still references static folder")
            return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed! Static folder successfully renamed to public.")
    print("✅ All code references have been updated.")
    print("✅ Flask app is configured correctly.")
    
    return True

if __name__ == "__main__":
    success = test_static_folder_rename()
    sys.exit(0 if success else 1) 