"""
Script to add banners to production database
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app_01.db import get_db
from src.app_01.models.banners.banner import Banner, BannerType
from datetime import datetime, timedelta

def add_production_banners():
    """Add banners to production database"""
    
    # Sample banners with Kyrgyzstan fashion theme
    banners = [
        {
            "title": "Новая коллекция",
            "subtitle": "Осень-Зима 2024",
            "description": "Откройте для себя нашу новую коллекцию премиальной одежды для мужчин",
            "image_url": "/uploads/banners/collection-banner.jpg",
            "banner_type": BannerType.HERO,
            "cta_text": "Смотреть коллекцию",
            "cta_url": "/category/men",
            "is_active": True,
            "display_order": 0
        },
        {
            "title": "Скидки до 80%",
            "subtitle": "На избранные товары",
            "description": "Не упустите возможность купить стильную одежду со скидкой",
            "image_url": "/uploads/banners/sale-banner.jpg",
            "banner_type": BannerType.HERO,
            "cta_text": "К скидкам",
            "cta_url": "/search?sort=discount",
            "is_active": True,
            "display_order": 1
        },
        {
            "title": "Качество премиум класса",
            "subtitle": "Местные бренды Кыргызстана",
            "description": "Поддержите местных производителей качественной одежды",
            "image_url": "/uploads/banners/quality-banner.jpg",
            "banner_type": BannerType.HERO,
            "cta_text": "Узнать больше",
            "cta_url": "/",
            "is_active": True,
            "display_order": 2
        },
        {
            "title": "Быстрее и выгоднее",
            "subtitle": "Товары с местного склада Кыргызстана",
            "description": "Доставка по всему Кыргызстану в течение 1-3 дней",
            "image_url": "/uploads/banners/promo-banner.jpg",
            "banner_type": BannerType.PROMO,
            "cta_text": "Смотреть товары",
            "cta_url": "/search",
            "is_active": True,
            "display_order": 0
        },
        {
            "title": "Мужская одежда",
            "subtitle": "Стиль для настоящих мужчин",
            "description": "Футболки, рубашки, джинсы и многое другое",
            "image_url": "/uploads/banners/men-category.jpg",
            "banner_type": BannerType.CATEGORY,
            "cta_text": "Мужчинам",
            "cta_url": "/category/men",
            "is_active": True,
            "display_order": 0
        }
    ]
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        print(f"\n{'='*60}")
        print(f"Adding banners to production database...")
        print(f"{'='*60}\n")
        
        added_count = 0
        for banner_data in banners:
            # Check if banner with this title already exists
            existing = db.query(Banner).filter(Banner.title == banner_data["title"]).first()
            if existing:
                print(f"⏭️  Banner '{banner_data['title']}' already exists, skipping...")
                continue
            
            banner = Banner(**banner_data)
            db.add(banner)
            added_count += 1
            print(f"✅ Added {banner_data['banner_type'].value} banner: {banner.title}")
        
        db.commit()
        print(f"\n✨ Successfully added {added_count} new banners to production database!")
        
        # Show banner summary
        hero_count = db.query(Banner).filter(Banner.banner_type == BannerType.HERO, Banner.is_active == True).count()
        promo_count = db.query(Banner).filter(Banner.banner_type == BannerType.PROMO, Banner.is_active == True).count()
        category_count = db.query(Banner).filter(Banner.banner_type == BannerType.CATEGORY, Banner.is_active == True).count()
        
        print(f"\n📊 Current active banners:")
        print(f"   🎯 Hero banners: {hero_count}")
        print(f"   🎁 Promo banners: {promo_count}")
        print(f"   📁 Category banners: {category_count}")
        print(f"   📈 Total: {hero_count + promo_count + category_count}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding banners: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("\n🎨 Adding Banners to Production Database\n")
    add_production_banners()
    print("\n🎉 All done! Test the API at: https://marquebackend-production.up.railway.app/api/v1/banners/\n")

