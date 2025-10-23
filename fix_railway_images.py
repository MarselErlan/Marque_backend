"""
Fix Image URLs in Production Railway Database

This script connects to Railway's production database and fixes image URLs.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get Railway DATABASE_URL from environment
RAILWAY_DB_URL = os.getenv("DATABASE_URL")

if not RAILWAY_DB_URL:
    print("❌ ERROR: DATABASE_URL environment variable not set!")
    print("\nTo fix production images on Railway:")
    print("1. Get DATABASE_URL from Railway dashboard")
    print("2. Run: export DATABASE_URL='your_railway_postgres_url'")
    print("3. Run this script again")
    exit(1)

print("🚀 Connecting to Railway production database...")
print(f"URL: {RAILWAY_DB_URL[:50]}...")

# Create engine
engine = create_engine(RAILWAY_DB_URL)
SessionLocal = sessionmaker(bind=engine)


def fix_production_banners():
    """Fix banner image URLs in production"""
    print("\n🔧 Fixing PRODUCTION banner URLs...")
    
    with SessionLocal() as session:
        # Check schema
        try:
            session.execute(text('SELECT mobile_image_url FROM banners LIMIT 1'))
            has_mobile = True
        except:
            session.rollback()
            has_mobile = False
            print("   No mobile_image_url column")
        
        # Get banners
        if has_mobile:
            banners = session.execute(text('SELECT id, title, image_url, mobile_image_url FROM banners')).fetchall()
        else:
            banners_raw = session.execute(text('SELECT id, title, image_url FROM banners')).fetchall()
            banners = [(b[0], b[1], b[2], None) for b in banners_raw]
        
        print(f"   Found {len(banners)} banners")
        fixed = 0
        
        for banner_id, title, image_url, mobile_url in banners:
            new_image = image_url
            new_mobile = mobile_url
            
            # Fix main image
            if image_url and not image_url.startswith('/uploads/'):
                if image_url.startswith('/'):
                    new_image = f'/uploads/banners/{image_url.lstrip("/")}'
                else:
                    new_image = f'/uploads/banners/{image_url}'
                new_image = new_image.replace('/uploads/banner/', '/uploads/banners/')
                new_image = new_image.replace('/uploads/banners/banners/', '/uploads/banners/')
            
            # Fix mobile image
            if mobile_url and not mobile_url.startswith('/uploads/'):
                if mobile_url.startswith('/'):
                    new_mobile = f'/uploads/banners/{mobile_url.lstrip("/")}'
                else:
                    new_mobile = f'/uploads/banners/{mobile_url}'
                new_mobile = new_mobile.replace('/uploads/banner/', '/uploads/banners/')
                new_mobile = new_mobile.replace('/uploads/banners/banners/', '/uploads/banners/')
            
            # Update if changed
            if new_image != image_url or (has_mobile and new_mobile != mobile_url):
                if has_mobile:
                    session.execute(text('''
                        UPDATE banners
                        SET image_url = :img, mobile_image_url = :mobile
                        WHERE id = :id
                    '''), {'img': new_image, 'mobile': new_mobile, 'id': banner_id})
                else:
                    session.execute(text('''
                        UPDATE banners SET image_url = :img WHERE id = :id
                    '''), {'img': new_image, 'id': banner_id})
                
                print(f"   ✅ Fixed: {title}")
                print(f"      Old: {image_url}")
                print(f"      New: {new_image}")
                fixed += 1
        
        session.commit()
        print(f"\n✅ Fixed {fixed} banner URLs in production!")
        
        # Show results
        print("\n📋 All production banners:")
        result = session.execute(text('SELECT id, title, image_url FROM banners ORDER BY id')).fetchall()
        for banner_id, title, url in result:
            print(f"   {banner_id}. {title}")
            print(f"      {url}")


def fix_production_products():
    """Fix product image URLs in production"""
    print("\n🔧 Fixing PRODUCTION product URLs...")
    
    with SessionLocal() as session:
        # Check if main_image column exists
        try:
            session.execute(text('SELECT main_image FROM products LIMIT 1'))
            has_main_image = True
            image_column = 'main_image'
        except:
            session.rollback()
            try:
                session.execute(text('SELECT image_url FROM products LIMIT 1'))
                has_main_image = True
                image_column = 'image_url'
            except:
                session.rollback()
                print("   No image columns in products table")
                return
        
        # Get products
        products = session.execute(text(f'SELECT id, title, {image_column} FROM products')).fetchall()
        print(f"   Found {len(products)} products")
        fixed = 0
        
        for product_id, title, image_url in products:
            if not image_url:
                continue
            
            new_image = image_url
            
            # Fix product image
            if not image_url.startswith('/uploads/'):
                if image_url.startswith('/'):
                    new_image = f'/uploads/products/{image_url.lstrip("/")}'
                else:
                    new_image = f'/uploads/products/{image_url}'
                new_image = new_image.replace('/uploads/product/', '/uploads/products/')
                new_image = new_image.replace('/uploads/products/products/', '/uploads/products/')
            
            # Update if changed
            if new_image != image_url:
                session.execute(text(f'''
                    UPDATE products SET {image_column} = :img WHERE id = :id
                '''), {'img': new_image, 'id': product_id})
                
                print(f"   ✅ Fixed: {title}")
                print(f"      Old: {image_url}")
                print(f"      New: {new_image}")
                fixed += 1
        
        session.commit()
        print(f"\n✅ Fixed {fixed} product URLs in production!")
        
        # Show results
        print("\n📦 All production products:")
        result = session.execute(text(f'SELECT id, title, {image_column} FROM products ORDER BY id LIMIT 10')).fetchall()
        for product_id, title, url in result:
            print(f"   {product_id}. {title}")
            print(f"      {url}")


def main():
    print("=" * 80)
    print("🚀 FIXING PRODUCTION IMAGES ON RAILWAY")
    print("=" * 80)
    
    try:
        fix_production_banners()
        fix_production_products()
        
        print("\n" + "=" * 80)
        print("✅ PRODUCTION DATABASE FIXED!")
        print("=" * 80)
        print("\nYour production site should now show images correctly! 🎉")
        print("\nTest it:")
        print("  https://marquebackend-production.up.railway.app/api/v1/banners/")
        print("  https://marquebackend-production.up.railway.app/api/v1/products/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

