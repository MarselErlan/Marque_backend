#!/usr/bin/env python3
"""
Create Admin User in Both Markets Script
Creates super admin in both KG and US databases
"""

import sys
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin


def create_admin_in_market(
    market: Market,
    username: str,
    password: str,
    email: str,
    full_name: str = None,
    is_super_admin: bool = False,
    admin_role: str = "super_admin"
):
    """
    Create admin in specific market database
    """
    # Bcrypt limitation: passwords must be <= 72 bytes
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    # Get database session for this market
    db = next(db_manager.get_db_session(market))
    
    try:
        # Check if username already exists
        existing_admin = db.query(Admin).filter(Admin.username == username).first()
        if existing_admin:
            print(f"⚠️  Admin '{username}' already exists in {market.value.upper()} database")
            return None
        
        # Hash password
        hashed_password = bcrypt.hash(password)
        
        # Create admin
        admin = Admin(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name or username,
            is_super_admin=is_super_admin,
            is_active=True,
            admin_role=admin_role,
            market=market.value  # Set market
        )
        
        # Setup default permissions
        admin.setup_default_permissions()
        
        # Save to database
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        return admin
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin in {market.value.upper()}: {e}")
        return None
    finally:
        db.close()


def create_super_admin_both_markets(
    username: str = "admin",
    password: str = "admin123",
    email: str = "admin@marque.com",
    full_name: str = "Super Administrator"
):
    """
    Create super admin in both KG and US databases
    """
    print("\n" + "="*60)
    print("  Creating Super Admin in BOTH Markets")
    print("="*60 + "\n")
    
    results = {}
    
    # Create in KG database
    print("🇰🇬 Creating admin in KG (Kyrgyzstan) database...")
    kg_admin = create_admin_in_market(
        market=Market.KG,
        username=username,
        password=password,
        email=email,
        full_name=full_name,
        is_super_admin=True,
        admin_role="super_admin"
    )
    
    if kg_admin:
        results['kg'] = kg_admin
        print(f"   ✅ Admin created in KG database (ID: {kg_admin.id})")
    else:
        print(f"   ❌ Failed to create admin in KG database")
    
    print()
    
    # Create in US database
    print("🇺🇸 Creating admin in US (United States) database...")
    us_admin = create_admin_in_market(
        market=Market.US,
        username=username,
        password=password,
        email=email,
        full_name=full_name,
        is_super_admin=True,
        admin_role="super_admin"
    )
    
    if us_admin:
        results['us'] = us_admin
        print(f"   ✅ Admin created in US database (ID: {us_admin.id})")
    else:
        print(f"   ❌ Failed to create admin in US database")
    
    # Summary
    print("\n" + "="*60)
    if len(results) == 2:
        print("  ✅ SUCCESS! Admin created in BOTH databases!")
    elif len(results) == 1:
        print("  ⚠️  PARTIAL: Admin created in ONE database only")
    else:
        print("  ❌ FAILED: Could not create admin in any database")
    print("="*60)
    
    if results:
        print("\n📋 Admin Details:")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Username:     {username}")
        print(f"Password:     {password}")
        print(f"Email:        {email}")
        print(f"Full Name:    {full_name}")
        print(f"Role:         super_admin")
        print(f"Super Admin:  True")
        
        if 'kg' in results:
            print(f"\n🇰🇬 KG Database:")
            print(f"   ID:          {results['kg'].id}")
            print(f"   Market:      kg")
            print(f"   Permissions: {results['kg'].permissions}")
        
        if 'us' in results:
            print(f"\n🇺🇸 US Database:")
            print(f"   ID:          {results['us'].id}")
            print(f"   Market:      us")
            print(f"   Permissions: {results['us'].permissions}")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n🔐 Login at: http://localhost:8000/admin/login")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print(f"   Market:   Select KG or US")
        print()
    
    return results


def interactive_create_admin_both_markets():
    """Interactive admin creation for both markets"""
    print("\n╔═══════════════════════════════════════════════════════╗")
    print("║  Create Super Admin in BOTH KG and US Databases      ║")
    print("╚═══════════════════════════════════════════════════════╝\n")
    
    # Get admin details
    username = input("👤 Username: ").strip()
    if not username:
        print("❌ Username cannot be empty!")
        return
    
    password = input("🔒 Password: ").strip()
    if not password:
        print("❌ Password cannot be empty!")
        return
    
    if len(password) < 6:
        print("❌ Password must be at least 6 characters!")
        return
    
    email = input("📧 Email: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        return
    
    full_name = input("📝 Full Name (optional): ").strip() or username
    
    # Create in both markets
    create_super_admin_both_markets(
        username=username,
        password=password,
        email=email,
        full_name=full_name
    )


def quick_create_super_admin_both():
    """Quickly create super admin in both markets with default credentials"""
    create_super_admin_both_markets(
        username="admin",
        password="admin123",
        email="admin@marque.com",
        full_name="Super Administrator"
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # Quick create super admin in both markets
            quick_create_super_admin_both()
        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python create_admin_both_markets.py              # Interactive mode")
            print("  python create_admin_both_markets.py --quick      # Create default super admin in BOTH markets")
            print("  python create_admin_both_markets.py --help       # Show this help")
            print()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Interactive mode
        interactive_create_admin_both_markets()

