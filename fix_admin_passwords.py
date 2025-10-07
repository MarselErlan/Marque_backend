#!/usr/bin/env python3
"""
Fix admin passwords in both databases
Recreate admin users with properly hashed passwords
"""

import bcrypt
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly (not passlib)"""
    # Truncate to 72 bytes if needed
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Hash with bcrypt directly
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def recreate_admin(market: Market):
    """Recreate admin user in specific market database"""
    print(f"\n{'='*70}")
    print(f"🔧 Fixing {market.value.upper()} Database Admin")
    print(f"{'='*70}")
    
    db = next(db_manager.get_db_session(market))
    
    try:
        # Delete existing admin
        existing = db.query(Admin).filter(Admin.username == "admin").first()
        if existing:
            print(f"⚠️  Deleting existing admin (ID: {existing.id})...")
            db.delete(existing)
            db.commit()
            print(f"✅ Deleted")
        
        # Create new admin with properly hashed password
        print(f"\n🔐 Creating new admin with bcrypt-hashed password...")
        
        password = "admin123"
        hashed_password = hash_password(password)
        
        admin = Admin(
            username="admin",
            email="admin@marque.com",
            hashed_password=hashed_password,
            full_name="Super Administrator",
            is_super_admin=True,
            admin_role="super_admin",
            is_active=True,
            permissions='orders.view,orders.update,orders.delete,products.create,products.update,products.delete,users.view,users.update,admins.create,admins.update'
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Admin created successfully!")
        print(f"   ID: {admin.id}")
        print(f"   Username: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Password hash length: {len(admin.hashed_password)}")
        print(f"   Hash preview: {admin.hashed_password[:30]}...")
        
        # Test password verification
        print(f"\n🧪 Testing password verification...")
        test_password = "admin123".encode('utf-8')
        if bcrypt.checkpw(test_password, admin.hashed_password.encode('utf-8')):
            print(f"✅ Password verification: SUCCESS!")
        else:
            print(f"❌ Password verification: FAILED!")
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("╔" + "="*70 + "╗")
    print("║" + " "*15 + "🔧 FIX ADMIN PASSWORDS - BOTH DATABASES" + " "*15 + "║")
    print("╚" + "="*70 + "╝")
    
    print("\nThis script will:")
    print("  1. Delete existing admin users")
    print("  2. Create new admins with properly hashed passwords")
    print("  3. Test password verification")
    print()
    
    # Fix both databases
    recreate_admin(Market.KG)
    recreate_admin(Market.US)
    
    print("\n" + "="*70)
    print("✅ COMPLETE! Admin passwords fixed in both databases.")
    print("="*70)
    print("\n🔐 Login credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🚀 Now deploy to Railway!")

