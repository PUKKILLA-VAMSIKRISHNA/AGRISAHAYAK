#!/usr/bin/env python3
"""
Test script for Supabase database connection
"""

import os
import psycopg2
from urllib.parse import urlparse

# Your Supabase URL
DATABASE_URL = "postgresql://postgres:VamsiKrishna123@db.scwrkxpsdwtehckqbjht.supabase.co:5432/postgres"

def test_connection():
    print("Testing Supabase database connection...")
    print(f"URL: {DATABASE_URL}")
    
    try:
        # Parse the URL
        parsed = urlparse(DATABASE_URL)
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port}")
        print(f"Database: {parsed.path[1:]}")
        print(f"Username: {parsed.username}")
        
        # Test connection with psycopg2
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password,
            sslmode='require',
            connect_timeout=10
        )
        
        print("✅ Connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        print("✅ Query test successful!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False
    
    return True

if __name__ == "__main__":
    test_connection() 