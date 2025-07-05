#!/usr/bin/env python3
"""
Test script for chat functionality
"""

import os
import requests
import json

# Set environment variables
os.environ['DATABASE_URL'] = 'postgresql://postgres:VamsiKrishna123@db.scwrkxpsdwtehckqbjht.supabase.co:5432/postgres'
os.environ['SECRET_KEY'] = 'Vamsi@123'

def test_chat_api():
    """Test the chat API endpoint"""
    print("Testing chat API...")
    
    # Test data
    test_data = {
        'chat_id': 1,
        'message': 'Hello, how are you?',
        'language': 'en'
    }
    
    try:
        # Start the Flask app in a separate process or use a running instance
        # For now, we'll just test the import
        from main import app
        
        with app.test_client() as client:
            # Test health endpoint
            response = client.get('/health')
            print(f"Health check: {response.status_code}")
            print(f"Response: {response.get_json()}")
            
            # Test send message endpoint (this will fail without proper authentication)
            response = client.post('/api/send_message', 
                                 data=json.dumps(test_data),
                                 content_type='application/json')
            print(f"Send message: {response.status_code}")
            print(f"Response: {response.get_data(as_text=True)}")
            
    except Exception as e:
        print(f"Error testing chat API: {e}")

if __name__ == "__main__":
    test_chat_api() 