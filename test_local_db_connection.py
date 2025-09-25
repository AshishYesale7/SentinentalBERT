#!/usr/bin/env python3
"""
Simple test script to verify local PostgreSQL connection
"""

import os
import sys
from pathlib import Path

# Load environment variables
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

try:
    import psycopg2
    print("✅ psycopg2 is available")
except ImportError:
    print("❌ psycopg2 not found. Installing...")
    os.system("pip install psycopg2-binary")
    import psycopg2

def test_connection():
    """Test PostgreSQL connection"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'sentinelbert')
    DB_USER = os.getenv('DB_USER', 'sentinel')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'sentinel_native_2024')
    
    print(f"🔍 Testing connection to PostgreSQL:")
    print(f"   Host: {DB_HOST}:{DB_PORT}")
    print(f"   Database: {DB_NAME}")
    print(f"   User: {DB_USER}")
    
    try:
        # Test connection
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=10
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✅ Connection successful!")
        print(f"📊 PostgreSQL version: {version}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Make sure PostgreSQL is running:")
        print("   sudo systemctl status postgresql")
        print("   # or")
        print("   brew services list | grep postgresql")
        print()
        print("2. Check if database and user exist:")
        print(f"   psql -h {DB_HOST} -p {DB_PORT} -U postgres -c \"\\l\"")
        print(f"   psql -h {DB_HOST} -p {DB_PORT} -U postgres -c \"\\du\"")
        print()
        print("3. Create database and user manually:")
        print(f"   psql -h {DB_HOST} -p {DB_PORT} -U postgres")
        print(f"   CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';")
        print(f"   CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
        print(f"   GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};")
        return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)