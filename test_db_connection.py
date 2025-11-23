#!/usr/bin/env python3
"""
Test script for Supabase database connection
Enhanced with DNS checks and multiple connection methods
"""

import os
import socket
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Try to get DATABASE_URL from environment, fallback to hardcoded value
DATABASE_URL = os.environ.get('DATABASE_URL') or "postgresql://postgres:VamsiKrishna123@db.scwrkxpsdwtehckqbjht.supabase.co:5432/postgres"

def check_dns(hostname):
    """Check if hostname can be resolved"""
    try:
        print(f"\n🔍 Checking DNS resolution for {hostname}...")
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS resolution successful: {hostname} -> {ip}")
        return True
    except socket.gaierror as e:
        print(f"❌ DNS resolution failed: {e}")
        print(f"   This means the hostname '{hostname}' cannot be found.")
        print(f"   Possible causes:")
        print(f"   1. The Supabase project may have been deleted or paused")
        print(f"   2. The hostname in the connection string is incorrect")
        print(f"   3. There's a network/DNS issue")
        print(f"   4. The Supabase project needs to be reactivated")
        return False
    except Exception as e:
        print(f"❌ DNS check error: {e}")
        return False

def test_connection_method(url, description):
    """Test a specific connection method"""
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"URL: {url}")
    
    try:
        parsed = urlparse(url)
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port or 5432}")
        print(f"Database: {parsed.path[1:] if parsed.path else 'postgres'}")
        print(f"Username: {parsed.username}")
        
        # Check DNS first
        if not check_dns(parsed.hostname):
            return False
        
        # Test connection with psycopg2
        print(f"\n🔌 Attempting connection...")
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path[1:] if parsed.path else 'postgres',
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
        return True
        
    except psycopg2.OperationalError as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        if "could not translate host name" in error_msg or "No such host is known" in error_msg:
            print(f"\n💡 DNS Resolution Error:")
            print(f"   The hostname cannot be resolved. Please check:")
            print(f"   1. Go to your Supabase dashboard: https://supabase.com/dashboard")
            print(f"   2. Select your project")
            print(f"   3. Go to Settings > Database")
            print(f"   4. Copy the connection string from 'Connection string' section")
            print(f"   5. Make sure the project is not paused")
        
        elif "password authentication failed" in error_msg:
            print(f"\n💡 Authentication Error:")
            print(f"   The username or password is incorrect.")
        
        elif "timeout" in error_msg.lower():
            print(f"\n💡 Timeout Error:")
            print(f"   The connection timed out. Check your network/firewall settings.")
        
        return False
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def test_connection():
    """Test database connection with multiple methods"""
    print("="*60)
    print("Supabase Database Connection Test")
    print("="*60)
    
    # Check if using environment variable
    env_url = os.environ.get('DATABASE_URL')
    if env_url:
        print(f"\n📋 Using DATABASE_URL from environment variable")
    else:
        print(f"\n📋 Using hardcoded DATABASE_URL (consider using .env file)")
        print(f"   Tip: Create a .env file with: DATABASE_URL=your_connection_string")
    
    # Parse the URL to check format
    parsed = urlparse(DATABASE_URL)
    if not parsed.hostname:
        print(f"\n❌ Invalid DATABASE_URL format!")
        print(f"   Expected format: postgresql://user:password@host:port/database")
        print(f"   Got: {DATABASE_URL}")
        return False
    
    # Try direct connection (port 5432)
    success = test_connection_method(DATABASE_URL, "Direct Connection (Port 5432)")
    
    if not success and 'supabase.co' in parsed.hostname:
        # Try connection pooler (port 6543)
        print(f"\n{'='*60}")
        print("Trying alternative: Connection Pooler (Port 6543)")
        
        # Replace hostname and port for pooler
        pooler_hostname = parsed.hostname.replace('db.', 'pooler.') if parsed.hostname.startswith('db.') else f"pooler.{parsed.hostname}"
        pooler_url = f"postgresql://{parsed.username}:{parsed.password}@{pooler_hostname}:6543/{parsed.path[1:] if parsed.path else 'postgres'}"
        
        success = test_connection_method(pooler_url, "Connection Pooler (Port 6543)")
    
    if not success:
        print(f"\n{'='*60}")
        print("📝 TROUBLESHOOTING STEPS:")
        print("="*60)
        print("1. Verify your Supabase project exists and is not paused:")
        print("   - Visit: https://supabase.com/dashboard")
        print("   - Check if your project is listed and active")
        print()
        print("2. Get the correct connection string:")
        print("   - Go to: Settings > Database")
        print("   - Copy the connection string from the 'Connection string' section")
        print("   - Use either 'Connection pooling' or 'Direct connection'")
        print()
        print("3. Update your connection string:")
        print("   - Create a .env file in the project root")
        print("   - Add: DATABASE_URL=your_connection_string_here")
        print("   - Or update the hardcoded value in this script")
        print()
        print("4. Common Supabase connection formats:")
        print("   - Direct: postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres")
        print("   - Pooler: postgresql://postgres:[PASSWORD]@pooler.[PROJECT].supabase.co:6543/postgres")
    
    return success

if __name__ == "__main__":
    test_connection() 