"""
Script to add sample banners for testing
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app_01.db import Market, db_manager
from src.app_01.models.banners.banner import Banner, BannerType
from datetime import datetime, timedelta

def add_sample_banners():
    """Add sample banners to both databases"""
    
    # Sample sale banners
    sale_banners = [
        {
            "title": "Summer Sale - Up to 80% Off",
            "description": "Huge discounts on selected items! Don't miss out!",
            "image_url": "https://example.com/banners/summer-sale.jpg",
            "banner_type": BannerType.SALE,
            "link_url": "/products?category=sale",
            "is_active": True,
            "display_order": 1
        },
        {
            "title": "Black Friday Special",
            "description": "Amazing deals for Black Friday weekend",
            "image_url": "https://example.com/banners/black-friday.jpg",
            "banner_type": BannerType.SALE,
            "link_url": "/products?category=black-friday",
            "is_active": True,
            "display_order": 2,
            "start_date": datetime.utcnow(),
            "end_date": datetime.utcnow() + timedelta(days=7)
        },
        {
            "title": "New Arrivals - 20% Off",
            "description": "Get 20% off on all new arrivals this week",
            "image_url": "https://example.com/banners/new-arrivals-sale.jpg",
            "banner_type": BannerType.SALE,
            "link_url": "/products?category=new-arrivals",
            "is_active": True,
            "display_order": 3
        }
    ]
    
    # Sample model banners
    model_banners = [
        {
            "title": "Spring Collection 2024",
            "description": "Check out our latest spring fashion collection",
            "image_url": "https://example.com/banners/spring-collection.jpg",
            "banner_type": BannerType.MODEL,
            "link_url": "/products?collection=spring-2024",
            "is_active": True,
            "display_order": 1
        },
        {
            "title": "Premium Denim Collection",
            "description": "Discover our premium denim range",
            "image_url": "https://example.com/banners/denim-collection.jpg",
            "banner_type": BannerType.MODEL,
            "link_url": "/products?category=denim",
            "is_active": True,
            "display_order": 2
        },
        {
            "title": "Casual Wear Essentials",
            "description": "Comfortable and stylish casual outfits",
            "image_url": "https://example.com/banners/casual-wear.jpg",
            "banner_type": BannerType.MODEL,
            "link_url": "/products?category=casual",
            "is_active": True,
            "display_order": 3
        }
    ]
    
    # Add to both KG and US databases
    for market in [Market.KG, Market.US]:
        session_factory = db_manager.get_session_factory(market)
        
        with session_factory() as db:
            print(f"\n{'='*50}")
            print(f"Adding banners to {market.value.upper()} database...")
            print(f"{'='*50}\n")
            
            # Add sale banners
            for banner_data in sale_banners:
                banner = Banner(**banner_data)
                db.add(banner)
                print(f"✅ Added sale banner: {banner.title}")
            
            # Add model banners
            for banner_data in model_banners:
                banner = Banner(**banner_data)
                db.add(banner)
                print(f"✅ Added model banner: {banner.title}")
            
            db.commit()
            print(f"\n✨ Successfully added {len(sale_banners) + len(model_banners)} banners to {market.value.upper()} database!\n")

if __name__ == "__main__":
    print("\n🎨 Adding Sample Banners to Database\n")
    add_sample_banners()
    print("\n🎉 All done! You can now test the banner endpoints.\n")

