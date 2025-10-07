#!/usr/bin/env python3
"""
Create Admin User Script
Creates a new admin user for SQLAdmin access
"""

import sys
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin


def create_admin(
    username: str,
    password: str,
    email: str,
    full_name: str = None,
    is_super_admin: bool = False,
    admin_role: str = "website_content"
):
    """
    Create a new admin user
    
    Args:
        username: Admin username for login
        password: Plain text password (will be hashed)
        email: Admin email address
        full_name: Full name of admin (optional)
        is_super_admin: Whether admin has super admin privileges
        admin_role: Admin role (order_management, website_content, super_admin)
    """
    # Bcrypt limitation: passwords must be <= 72 bytes
    if len(password.encode('utf-8')) > 72:
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    # Get database session
    db = next(db_manager.get_db_session(Market.KG))
    
    try:
        # Check if username already exists
        existing_admin = db.query(Admin).filter(Admin.username == username).first()
        if existing_admin:
            print(f"❌ Error: Username '{username}' already exists!")
            return False
        
        # Check if email already exists
        existing_email = db.query(Admin).filter(Admin.email == email).first()
        if existing_email:
            print(f"❌ Error: Email '{email}' already exists!")
            return False
        
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
            admin_role=admin_role
        )
        
        # Setup default permissions
        admin.setup_default_permissions()
        
        # Save to database
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n✅ Admin user created successfully!")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"ID:           {admin.id}")
        print(f"Username:     {admin.username}")
        print(f"Email:        {admin.email}")
        print(f"Full Name:    {admin.full_name}")
        print(f"Role:         {admin.admin_role}")
        print(f"Super Admin:  {admin.is_super_admin}")
        print(f"Permissions:  {admin.permissions}")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n🔐 Login at: http://localhost:8000/admin/login")
        print(f"   Username: {admin.username}")
        print(f"   Password: [the password you entered]")
        print()
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin: {e}")
        return False
    finally:
        db.close()


def interactive_create_admin():
    """Interactive admin creation"""
    print("\n╔═══════════════════════════════════════════════════╗")
    print("║     Create New Admin User for SQLAdmin           ║")
    print("╚═══════════════════════════════════════════════════╝\n")
    
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
    
    # Bcrypt limitation: passwords must be <= 72 bytes
    if len(password.encode('utf-8')) > 72:
        print("⚠️  Password too long (bcrypt max 72 bytes), truncating...")
        password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    
    email = input("📧 Email: ").strip()
    if not email:
        print("❌ Email cannot be empty!")
        return
    
    full_name = input("📝 Full Name (optional): ").strip()
    
    # Ask about role
    print("\n👔 Select Admin Role:")
    print("   1. Website Content Admin (manage products, reviews)")
    print("   2. Order Management Admin (manage orders)")
    print("   3. Super Admin (full access)")
    
    role_choice = input("Enter choice (1-3, default: 1): ").strip() or "1"
    
    role_mapping = {
        "1": ("website_content", False),
        "2": ("order_management", False),
        "3": ("super_admin", True)
    }
    
    admin_role, is_super_admin = role_mapping.get(role_choice, ("website_content", False))
    
    # Create admin
    create_admin(
        username=username,
        password=password,
        email=email,
        full_name=full_name,
        is_super_admin=is_super_admin,
        admin_role=admin_role
    )


def quick_create_super_admin():
    """Quickly create a super admin with default credentials"""
    print("\n🚀 Creating Super Admin with default credentials...\n")
    
    create_admin(
        username="admin",
        password="admin123",
        email="admin@marque.com",
        full_name="Super Administrator",
        is_super_admin=True,
        admin_role="super_admin"
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # Quick create super admin
            quick_create_super_admin()
        elif sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python create_admin.py              # Interactive mode")
            print("  python create_admin.py --quick      # Create default super admin")
            print("  python create_admin.py --help       # Show this help")
            print()
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Interactive mode
        interactive_create_admin()

