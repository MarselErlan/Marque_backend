"""
Update existing admins with their correct market based on which database they're in
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

def update_admin_markets():
    """Update admin market fields based on phone number or database location"""
    
    print("="*70)
    print("🔄 UPDATING ADMIN MARKETS")
    print("="*70)
    
    # Update KG database admins
    print("\n📊 Updating KG database admins...")
    kg_session = next(db_manager.get_db_session(Market.KG))
    try:
        kg_admins = kg_session.query(Admin).all()
        count = 0
        for admin in kg_admins:
            if not admin.market or admin.market != 'kg':
                admin.market = 'kg'
                count += 1
                print(f"   ✅ Updated {admin.username} → market='kg'")
        
        kg_session.commit()
        print(f"   ✅ Updated {count} admin(s) in KG database")
    except Exception as e:
        print(f"   ❌ Error updating KG admins: {e}")
        kg_session.rollback()
    finally:
        kg_session.close()
    
    # Update US database admins
    print("\n📊 Updating US database admins...")
    us_session = next(db_manager.get_db_session(Market.US))
    try:
        us_admins = us_session.query(Admin).all()
        count = 0
        for admin in us_admins:
            if not admin.market or admin.market != 'us':
                admin.market = 'us'
                count += 1
                print(f"   ✅ Updated {admin.username} → market='us'")
        
        us_session.commit()
        print(f"   ✅ Updated {count} admin(s) in US database")
    except Exception as e:
        print(f"   ❌ Error updating US admins: {e}")
        us_session.rollback()
    finally:
        us_session.close()
    
    print("\n" + "="*70)
    print("✅ ADMIN MARKET UPDATE COMPLETE!")
    print("="*70)

if __name__ == "__main__":
    update_admin_markets()

