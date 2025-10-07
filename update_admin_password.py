#!/usr/bin/env python3
"""
Update admin password in both databases
Allows setting a custom password (minimum 6 characters)
"""

import bcrypt
import sys
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly"""
    # Truncate to 72 bytes if needed
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Hash with bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def update_admin_password(market: Market, new_password: str):
    """Update admin password in specific market database"""
    print(f"\n{'='*70}")
    print(f"🔧 Updating Admin Password in {market.value.upper()} Database")
    print(f"{'='*70}")
    
    db = next(db_manager.get_db_session(market))
    
    try:
        # Find admin by username
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        
        if not admin:
            print(f"❌ Admin 'admin' not found in {market.value} database!")
            return False
        
        print(f"✅ Found admin: ID={admin.id}, Username='{admin.username}'")
        
        # Hash new password
        print(f"🔐 Hashing new password...")
        hashed_password = hash_password(new_password)
        
        # Update password
        admin.hashed_password = hashed_password
        db.commit()
        db.refresh(admin)
        
        print(f"✅ Password updated successfully!")
        print(f"   New hash length: {len(admin.hashed_password)}")
        print(f"   Hash preview: {admin.hashed_password[:30]}...")
        
        # Test password verification
        print(f"\n🧪 Testing password verification...")
        test_password = new_password.encode('utf-8')
        if bcrypt.checkpw(test_password, admin.hashed_password.encode('utf-8')):
            print(f"✅ Password verification: SUCCESS!")
            return True
        else:
            print(f"❌ Password verification: FAILED!")
            return False
        
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("╔" + "="*70 + "╗")
    print("║" + " "*20 + "🔧 UPDATE ADMIN PASSWORD" + " "*20 + "║")
    print("╚" + "="*70 + "╝")
    
    # Get password from command line or prompt
    if len(sys.argv) > 1:
        new_password = sys.argv[1]
    else:
        new_password = input("\n🔐 Enter new password (min 6 characters): ").strip()
    
    # Validate password
    if len(new_password) < 6:
        print("❌ Password must be at least 6 characters!")
        sys.exit(1)
    
    print(f"\n📝 New password: '{new_password}'")
    print(f"📏 Length: {len(new_password)} characters")
    
    # Confirm
    confirm = input("\n⚠️  Update password in BOTH databases? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Cancelled.")
        sys.exit(0)
    
    # Update both databases
    kg_success = update_admin_password(Market.KG, new_password)
    us_success = update_admin_password(Market.US, new_password)
    
    print("\n" + "="*70)
    if kg_success and us_success:
        print("✅ PASSWORD UPDATED IN BOTH DATABASES!")
        print("="*70)
        print(f"\n🔐 New login credentials:")
        print(f"   Username: admin")
        print(f"   Password: {new_password}")
        print("\n🚀 You can now login with the new password!")
    else:
        print("❌ PASSWORD UPDATE FAILED!")
        print("="*70)
        print("\nCheck the errors above and try again.")
    
    print()

