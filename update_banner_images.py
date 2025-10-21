"""
Update banner images to use existing placeholder images
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app_01.db import get_db
from src.app_01.models.banners.banner import Banner

def update_banner_images():
    """Update banners to use existing placeholder images"""
    
    # Map banner titles to existing placeholder images
    banner_image_map = {
        "Новая коллекция": "/b93dc4af6b33446ca2a5472bc63797bc73a9eae2.png",
        "Скидки до 80%": "/fcdeeb08e8c20a6a5cf5276b59b60923dfb8c706(1).png",
        "Качество премиум класса": "/5891ae04bafdf76a4d441c78c7e1f8a0a3a1d631.png",
    }
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        print(f"\n{'='*60}")
        print(f"Updating banner images...")
        print(f"{'='*60}\n")
        
        updated_count = 0
        for title, image_url in banner_image_map.items():
            banner = db.query(Banner).filter(Banner.title == title).first()
            if banner:
                old_url = banner.image_url
                banner.image_url = image_url
                updated_count += 1
                print(f"✅ Updated '{title}'")
                print(f"   Old: {old_url}")
                print(f"   New: {image_url}\n")
            else:
                print(f"⚠️  Banner '{title}' not found\n")
        
        db.commit()
        print(f"✨ Successfully updated {updated_count} banner images!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating banners: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🖼️  Updating Banner Images\n")
    update_banner_images()
    print("\n🎉 All done!\n")

