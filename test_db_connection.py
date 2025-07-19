#!/usr/bin/env python3
"""
Test script to verify database connection.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.config.settings import DB_CONFIG
import psycopg2
from sqlalchemy import create_engine, text

def test_connection():
    """Test database connection."""
    print("🔍 Testing Database Connection...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Port: {DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['dbname']}")
    print(f"User: {DB_CONFIG['user']}")
    print("-" * 50)
    
    # Test psycopg2 connection
    try:
        print("📡 Testing psycopg2 connection...")
        connection = psycopg2.connect(
            dbname=DB_CONFIG["dbname"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            connect_timeout=10
        )
        print("✅ psycopg2 connection successful")
        
        # Test cursor
        cursor = connection.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        # Test tables query
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ psycopg2 connection failed: {str(e)}")
        return False
    
    # Test SQLAlchemy connection
    try:
        print("\n📡 Testing SQLAlchemy connection...")
        connection_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"
        engine = create_engine(connection_string, connect_args={"connect_timeout": 10})
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            count = result.fetchone()[0]
            print(f"✅ SQLAlchemy connection successful - Found {count} tables")
        
        engine.dispose()
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {str(e)}")
        return False
    
    print("\n🎉 All connection tests passed!")
    return True

if __name__ == "__main__":
    success = test_connection()
    if not success:
        sys.exit(1) 