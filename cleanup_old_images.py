"""
Cleanup Old Image URLs
Remove all old product asset URLs from database
"""

from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.products.product_asset import ProductAsset

def cleanup_old_images():
    """Delete all existing product assets with old URLs"""
    SessionLocal = db_manager.get_session_factory(Market.KG)
    db = SessionLocal()
    
    try:
        # Get count before deletion
        total_assets = db.query(ProductAsset).count()
        print(f"📊 Found {total_assets} product assets in database")
        
        if total_assets == 0:
            print("✅ No assets to delete")
            return
        
        # Confirm deletion
        print(f"\n⚠️  This will DELETE all {total_assets} product assets!")
        confirm = input("Type 'DELETE' to confirm: ")
        
        if confirm != "DELETE":
            print("❌ Cancelled")
            return
        
        # Delete all assets
        deleted_count = db.query(ProductAsset).delete()
        db.commit()
        
        print(f"✅ Successfully deleted {deleted_count} product assets")
        print("🎉 Database cleaned! You can now upload new images using Pillow")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("🗑️  PRODUCT ASSET CLEANUP UTILITY")
    print("=" * 60)
    cleanup_old_images()

