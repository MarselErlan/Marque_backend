"""
Fix Image URLs in Database

Problem:
- Frontend requests: /banner/xxx.png, /product/xxx.png
- Static files mounted at: /uploads/
- Database has inconsistent URLs

Solution:
- Add /uploads/ prefix if missing
- Fix /banner/ -> /banners/
- Fix /product/ -> /products/
"""

from src.app_01.db.market_db import db_manager, Market
from sqlalchemy import text

def fix_banner_urls(market: Market):
    """Fix banner image URLs"""
    print(f"\n🔧 Fixing banner URLs for {market.value} market...")
    session_factory = db_manager.get_session_factory(market)
    
    with session_factory() as session:
        # Check if mobile_image_url column exists
        try:
            session.execute(text('SELECT mobile_image_url FROM banners LIMIT 1'))
            has_mobile_column = True
        except:
            session.rollback()  # Rollback failed transaction
            has_mobile_column = False
        
        # Get all banners
        if has_mobile_column:
            banners = session.execute(text('''
                SELECT id, title, image_url, mobile_image_url
                FROM banners
            ''')).fetchall()
        else:
            banners_raw = session.execute(text('''
                SELECT id, title, image_url
                FROM banners
            ''')).fetchall()
            # Add None for mobile_image_url
            banners = [(b[0], b[1], b[2], None) for b in banners_raw]
        
        fixed_count = 0
        
        for banner_id, title, image_url, mobile_image_url in banners:
            new_image_url = image_url
            new_mobile_url = mobile_image_url
            
            # Fix main image URL
            if image_url:
                if not image_url.startswith('/uploads/'):
                    if image_url.startswith('/'):
                        # Remove leading slash and add /uploads/
                        new_image_url = f'/uploads/banners/{image_url.lstrip("/")}'
                    else:
                        # Add /uploads/ prefix
                        new_image_url = f'/uploads/banners/{image_url}'
                
                # Fix /banner/ -> /banners/
                new_image_url = new_image_url.replace('/uploads/banner/', '/uploads/banners/')
                
                # Fix /banners/banners/ (in case of double prefix)
                new_image_url = new_image_url.replace('/uploads/banners/banners/', '/uploads/banners/')
            
            # Fix mobile image URL
            if mobile_image_url:
                if not mobile_image_url.startswith('/uploads/'):
                    if mobile_image_url.startswith('/'):
                        new_mobile_url = f'/uploads/banners/{mobile_image_url.lstrip("/")}'
                    else:
                        new_mobile_url = f'/uploads/banners/{mobile_image_url}'
                
                new_mobile_url = new_mobile_url.replace('/uploads/banner/', '/uploads/banners/')
                new_mobile_url = new_mobile_url.replace('/uploads/banners/banners/', '/uploads/banners/')
            
            # Update if changed
            if new_image_url != image_url or (has_mobile_column and new_mobile_url != mobile_image_url):
                if has_mobile_column:
                    session.execute(text('''
                        UPDATE banners
                        SET image_url = :new_image_url,
                            mobile_image_url = :new_mobile_url
                        WHERE id = :banner_id
                    '''), {
                        'new_image_url': new_image_url,
                        'new_mobile_url': new_mobile_url,
                        'banner_id': banner_id
                    })
                else:
                    session.execute(text('''
                        UPDATE banners
                        SET image_url = :new_image_url
                        WHERE id = :banner_id
                    '''), {
                        'new_image_url': new_image_url,
                        'banner_id': banner_id
                    })
                
                print(f"  ✅ Fixed banner '{title}':")
                if image_url != new_image_url:
                    print(f"     Old: {image_url}")
                    print(f"     New: {new_image_url}")
                if mobile_image_url and mobile_image_url != new_mobile_url:
                    print(f"     Mobile old: {mobile_image_url}")
                    print(f"     Mobile new: {new_mobile_url}")
                
                fixed_count += 1
        
        session.commit()
        print(f"\n✅ Fixed {fixed_count} banner URLs in {market.value} market")
        
        # Show all banners after fix
        print(f"\n📋 All banners in {market.value} after fix:")
        banners_after = session.execute(text('''
            SELECT id, title, image_url
            FROM banners
            ORDER BY id
        ''')).fetchall()
        
        for banner_id, title, image_url in banners_after:
            print(f"  {banner_id}. {title}")
            print(f"     {image_url}")


def fix_product_urls(market: Market):
    """Fix product image URLs"""
    print(f"\n🔧 Fixing product URLs for {market.value} market...")
    session_factory = db_manager.get_session_factory(market)
    
    with session_factory() as session:
        # Get all products
        products = session.execute(text('''
            SELECT id, title, main_image
            FROM products
        ''')).fetchall()
        
        fixed_count = 0
        
        for product_id, title, main_image in products:
            if not main_image:
                continue
            
            new_main_image = main_image
            
            # Fix product image URL
            if not main_image.startswith('/uploads/'):
                if main_image.startswith('/'):
                    # Remove leading slash and add /uploads/
                    new_main_image = f'/uploads/products/{main_image.lstrip("/")}'
                else:
                    # Add /uploads/ prefix
                    new_main_image = f'/uploads/products/{main_image}'
            
            # Fix /product/ -> /products/
            new_main_image = new_main_image.replace('/uploads/product/', '/uploads/products/')
            
            # Fix /products/products/ (in case of double prefix)
            new_main_image = new_main_image.replace('/uploads/products/products/', '/uploads/products/')
            
            # Update if changed
            if new_main_image != main_image:
                session.execute(text('''
                    UPDATE products
                    SET main_image = :new_main_image
                    WHERE id = :product_id
                '''), {
                    'new_main_image': new_main_image,
                    'product_id': product_id
                })
                
                print(f"  ✅ Fixed product '{title}':")
                print(f"     Old: {main_image}")
                print(f"     New: {new_main_image}")
                
                fixed_count += 1
        
        session.commit()
        print(f"\n✅ Fixed {fixed_count} product URLs in {market.value} market")
        
        # Show all products after fix
        print(f"\n📦 All products in {market.value} after fix:")
        products_after = session.execute(text('''
            SELECT id, title, main_image
            FROM products
            ORDER BY id
        ''')).fetchall()
        
        for product_id, title, main_image in products_after:
            print(f"  {product_id}. {title}")
            print(f"     {main_image}")


def main():
    """Fix all image URLs in all markets"""
    print("=" * 80)
    print("🔧 FIXING IMAGE URLS IN DATABASE")
    print("=" * 80)
    
    print("\nThis script will fix:")
    print("  1. Add /uploads/ prefix if missing")
    print("  2. Fix /banner/ -> /banners/")
    print("  3. Fix /product/ -> /products/")
    
    # Fix KG market
    print("\n" + "=" * 80)
    print("🇰🇬 KYRGYZSTAN MARKET")
    print("=" * 80)
    fix_banner_urls(Market.KG)
    fix_product_urls(Market.KG)
    
    # Fix US market
    print("\n" + "=" * 80)
    print("🇺🇸 USA MARKET")
    print("=" * 80)
    fix_banner_urls(Market.US)
    fix_product_urls(Market.US)
    
    print("\n" + "=" * 80)
    print("✅ ALL IMAGE URLS FIXED!")
    print("=" * 80)
    print("\nYour images should now load correctly:")
    print("  ✅ /uploads/banners/...")
    print("  ✅ /uploads/products/...")
    print("\nTest your frontend now! 🎉")


if __name__ == "__main__":
    main()

