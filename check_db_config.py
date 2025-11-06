#!/usr/bin/env python3
"""
Check Database Configuration
Shows which database URLs are currently configured
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "="*70)
print("🔍 DATABASE CONFIGURATION CHECK")
print("="*70 + "\n")

# Check environment variables
kg_url = os.getenv("DATABASE_URL_MARQUE_KG")
us_url = os.getenv("DATABASE_URL_MARQUE_US")

print("📂 Environment Variables:")
print("-" * 70)

if kg_url:
    # Hide sensitive info
    if "://" in kg_url:
        protocol = kg_url.split("://")[0]
        rest = kg_url.split("://")[1]
        if "@" in rest:
            # Has credentials
            path = rest.split("@")[-1]
            print(f"✅ DATABASE_URL_MARQUE_KG = {protocol}://*****@{path}")
        else:
            print(f"✅ DATABASE_URL_MARQUE_KG = {kg_url}")
    else:
        print(f"✅ DATABASE_URL_MARQUE_KG = {kg_url}")
else:
    print("❌ DATABASE_URL_MARQUE_KG = NOT SET (will use default)")

print()

if us_url:
    # Hide sensitive info
    if "://" in us_url:
        protocol = us_url.split("://")[0]
        rest = us_url.split("://")[1]
        if "@" in rest:
            # Has credentials
            path = rest.split("@")[-1]
            print(f"✅ DATABASE_URL_MARQUE_US = {protocol}://*****@{path}")
        else:
            print(f"✅ DATABASE_URL_MARQUE_US = {us_url}")
    else:
        print(f"✅ DATABASE_URL_MARQUE_US = {us_url}")
else:
    print("❌ DATABASE_URL_MARQUE_US = NOT SET (will use default)")

print("\n" + "-" * 70)
print("📊 What the app will use:")
print("-" * 70)

# Import settings
try:
    from src.app_01.core.config import settings
    
    kg_actual = settings.database.url_kg
    us_actual = settings.database.url_us
    
    # Detect database type
    if kg_actual.startswith("sqlite"):
        db_type_kg = "SQLite (Local)"
    elif kg_actual.startswith("postgresql"):
        db_type_kg = "PostgreSQL (Remote)"
    else:
        db_type_kg = "Unknown"
    
    if us_actual.startswith("sqlite"):
        db_type_us = "SQLite (Local)"
    elif us_actual.startswith("postgresql"):
        db_type_us = "PostgreSQL (Remote)"
    else:
        db_type_us = "Unknown"
    
    print(f"\n🔹 KG Market Database:")
    print(f"   Type: {db_type_kg}")
    if kg_actual.startswith("sqlite"):
        # Extract file path
        path = kg_actual.replace("sqlite:///", "")
        print(f"   Path: {path}")
        # Check if file exists
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   Status: ✅ File exists ({size:,} bytes)")
        else:
            print(f"   Status: ❌ File does not exist (will be created)")
    else:
        # Show host/port
        if "@" in kg_actual:
            host_info = kg_actual.split("@")[1].split("/")[0]
            print(f"   Host: {host_info}")
    
    print(f"\n🔹 US Market Database:")
    print(f"   Type: {db_type_us}")
    if us_actual.startswith("sqlite"):
        # Extract file path
        path = us_actual.replace("sqlite:///", "")
        print(f"   Path: {path}")
        # Check if file exists
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"   Status: ✅ File exists ({size:,} bytes)")
        else:
            print(f"   Status: ❌ File does not exist (will be created)")
    else:
        # Show host/port
        if "@" in us_actual:
            host_info = us_actual.split("@")[1].split("/")[0]
            print(f"   Host: {host_info}")

except Exception as e:
    print(f"\n❌ Error loading settings: {e}")

print("\n" + "="*70)
print("💡 TIP: To use SQLite locally, create a .env file with:")
print("="*70)
print("""
DATABASE_URL_MARQUE_KG=sqlite:///databases/marque_kg.db
DATABASE_URL_MARQUE_US=sqlite:///databases/marque_us.db
""")
print("="*70 + "\n")

