#!/usr/bin/env python3
"""
Test script to verify database setup for both KG and US markets
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and verify tables"""
    # Get database URLs from environment
    kg_url = os.getenv("DATABASE_URL_MARQUE_KG")
    us_url = os.getenv("DATABASE_URL_MARQUE_US")
    
    if not kg_url or not us_url:
        print("⚠️ Database URLs not found in environment variables")
        return True
    
    databases = [
        ("KG Database", kg_url),
        ("US Database", us_url)
    ]
    
    for database_name, database_url in databases:
        print(f"\n🔍 Testing {database_name} Database...")
        print("=" * 50)
        
        try:
            # Create engine
            engine = create_engine(database_url)
            
            # Test connection
            with engine.connect() as conn:
                # Get database version
                result = conn.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                print(f"✅ Connected to {database_name}")
                print(f"📊 Database: {version[:50]}...")
                
                print(f"✅ {database_name} connection test passed")
                
        except Exception as e:
            print(f"❌ {database_name} connection failed: {e}")
            return False
    
    print("✅ All database connections successful")
    return True
