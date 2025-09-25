#!/usr/bin/env python3
"""
Setup script for local PostgreSQL database
Creates database, user, and required schema for SentinelBERT
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from pathlib import Path

def create_database_and_user():
    """Create database and user if they don't exist"""
    
    # Database connection parameters
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'sentinelbert')
    DB_USER = os.getenv('DB_USER', 'sentinel')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'sentinel_native_2024')
    
    print(f"Setting up PostgreSQL database: {DB_NAME}")
    print(f"Host: {DB_HOST}:{DB_PORT}")
    print(f"User: {DB_USER}")
    
    # Connect to PostgreSQL as superuser (you may need to modify this)
    try:
        # Try to connect as the current user first
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database='postgres',  # Connect to default database
            user=os.getenv('POSTGRES_USER', 'postgres'),  # Default superuser
            password=os.getenv('POSTGRES_SUPERUSER_PASSWORD', '')  # May be empty for local
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if not exists
        try:
            cursor.execute(f"""
                CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';
            """)
            print(f"✅ Created user: {DB_USER}")
        except psycopg2.errors.DuplicateObject:
            print(f"ℹ️  User {DB_USER} already exists")
        
        # Create database if not exists
        try:
            cursor.execute(f"""
                CREATE DATABASE {DB_NAME} OWNER {DB_USER};
            """)
            print(f"✅ Created database: {DB_NAME}")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️  Database {DB_NAME} already exists")
        
        # Grant privileges
        cursor.execute(f"""
            GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};
        """)
        print(f"✅ Granted privileges to {DB_USER}")
        
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("\n📋 Manual setup instructions:")
        print("1. Connect to PostgreSQL as superuser:")
        print(f"   psql -h {DB_HOST} -p {DB_PORT} -U postgres")
        print("2. Run these commands:")
        print(f"   CREATE USER {DB_USER} WITH PASSWORD '{DB_PASSWORD}';")
        print(f"   CREATE DATABASE {DB_NAME} OWNER {DB_USER};")
        print(f"   GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO {DB_USER};")
        return False
    
    return True

def setup_schema():
    """Setup database schema"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'sentinelbert')
    DB_USER = os.getenv('DB_USER', 'sentinel')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'sentinel_native_2024')
    
    try:
        # Connect to the application database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Read and execute schema files
        schema_files = [
            'sql/enhanced_tracking_schema.sql',
            'sql/insideout_schema.sql'
        ]
        
        for schema_file in schema_files:
            schema_path = Path(__file__).parent / schema_file
            if schema_path.exists():
                print(f"📄 Executing schema: {schema_file}")
                with open(schema_path, 'r') as f:
                    schema_sql = f.read()
                
                # Execute schema (split by semicolon for multiple statements)
                statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
                for statement in statements:
                    try:
                        cursor.execute(statement)
                    except psycopg2.Error as e:
                        print(f"⚠️  Warning executing statement: {e}")
                
                conn.commit()
                print(f"✅ Schema {schema_file} executed successfully")
            else:
                print(f"⚠️  Schema file not found: {schema_file}")
        
        cursor.close()
        conn.close()
        print("✅ Database schema setup completed")
        
    except psycopg2.Error as e:
        print(f"❌ Error setting up schema: {e}")
        return False
    
    return True

def test_connection():
    """Test database connection"""
    
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'sentinelbert')
    DB_USER = os.getenv('DB_USER', 'sentinel')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'sentinel_native_2024')
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connection successful!")
        print(f"📊 PostgreSQL version: {version}")
        
        # Test table creation
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Found {len(tables)} tables:")
            for table in tables[:5]:  # Show first 5 tables
                print(f"   - {table[0]}")
            if len(tables) > 5:
                print(f"   ... and {len(tables) - 5} more")
        else:
            print("📋 No tables found (this is normal for a fresh setup)")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Database connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up local PostgreSQL for SentinelBERT")
    print("=" * 50)
    
    # Load environment variables
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        print("📄 Loading environment variables from .env")
        with open(env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Step 1: Create database and user
    print("\n1️⃣  Creating database and user...")
    if not create_database_and_user():
        print("❌ Failed to create database and user")
        sys.exit(1)
    
    # Step 2: Setup schema
    print("\n2️⃣  Setting up database schema...")
    if not setup_schema():
        print("❌ Failed to setup schema")
        sys.exit(1)
    
    # Step 3: Test connection
    print("\n3️⃣  Testing database connection...")
    if not test_connection():
        print("❌ Database connection test failed")
        sys.exit(1)
    
    print("\n🎉 Local PostgreSQL setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Start your services with: ./native-deploy.sh")
    print("2. Or use Docker with local DB: docker-compose -f docker-compose.local.yml up")
    print("3. Access Streamlit at: http://localhost:12000")
    print("4. Access React frontend at: http://localhost:12001")

if __name__ == "__main__":
    main()