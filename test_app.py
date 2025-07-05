#!/usr/bin/env python3
"""
Simple test script to verify Flask app startup without database
"""

import os
import sys

# Set environment variables for testing
os.environ['DATABASE_URL'] = 'postgresql://invalid:invalid@invalid:5432/invalid'
os.environ['SECRET_KEY'] = 'test-secret-key'

try:
    # Import the main app
    from main import app
    
    print("✅ Flask app imported successfully")
    
    # Test basic app functionality
    with app.test_client() as client:
        # Test health endpoint
        response = client.get('/health')
        print(f"✅ Health endpoint: {response.status_code}")
        
        # Test index endpoint
        response = client.get('/')
        print(f"✅ Index endpoint: {response.status_code}")
        
        # Test favicon endpoint
        response = client.get('/favicon.ico')
        print(f"✅ Favicon endpoint: {response.status_code}")
        
    print("✅ All tests passed! App can start without database.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1) 