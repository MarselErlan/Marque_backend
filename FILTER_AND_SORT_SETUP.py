"""
Filter and Sort Setup Example
This demonstrates how to set up the complete filtering and sorting system
to match the product listing page design.
"""

from src.app_01.db import SessionLocal
from src.app_01.models import (
    ProductFilter, ProductSeason, ProductMaterial, ProductStyle, 
    ProductDiscount, ProductSearch, Product, Brand, Category, Subcategory, SKU
)
from datetime import datetime, timedelta

def create_filter_system():
    """Create the complete filter system matching the design"""
    db = SessionLocal()
    
    try:
        print("🔍 Creating Filter and Sort System...")
        
        # 1. Create Product Filters (Sizes, Colors)
        print("\n📏 Creating Product Filters...")
        
        # Sizes
        sizes = [
            ProductFilter(filter_type="size", filter_value="40", display_name="40", sort_order=1),
            ProductFilter(filter_type="size", filter_value="42", display_name="42", sort_order=2),
            ProductFilter(filter_type="size", filter_value="44", display_name="44", sort_order=3),
            ProductFilter(filter_type="size", filter_value="46", display_name="46", sort_order=4),
            ProductFilter(filter_type="size", filter_value="48", display_name="48", sort_order=5),
            ProductFilter(filter_type="size", filter_value="50", display_name="50", sort_order=6)
        ]
        
        # Colors
        colors = [
            ProductFilter(filter_type="color", filter_value="black", display_name="Чёрный", sort_order=1),
            ProductFilter(filter_type="color", filter_value="white", display_name="Белый", sort_order=2),
            ProductFilter(filter_type="color", filter_value="beige", display_name="Бежевый", sort_order=3),
            ProductFilter(filter_type="color", filter_value="gray", display_name="Серый", sort_order=4),
            ProductFilter(filter_type="color", filter_value="red", display_name="Красный", sort_order=5),
            ProductFilter(filter_type="color", filter_value="blue", display_name="Синий", sort_order=6),
            ProductFilter(filter_type="color", filter_value="green", display_name="Зелёный", sort_order=7),
            ProductFilter(filter_type="color", filter_value="brown", display_name="Коричневый", sort_order=8)
        ]
        
        # Brands (from your design)
        brand_filters = [
            ProductFilter(filter_type="brand", filter_value="ecco", display_name="Ecco", sort_order=1),
            ProductFilter(filter_type="brand", filter_value="vans", display_name="Vans", sort_order=2),
            ProductFilter(filter_type="brand", filter_value="mango", display_name="MANGO", sort_order=3),
            ProductFilter(filter_type="brand", filter_value="hm", display_name="H&M", sort_order=4),
            ProductFilter(filter_type="brand", filter_value="nike", display_name="Nike", sort_order=5),
            ProductFilter(filter_type="brand", filter_value="adidas", display_name="Adidas", sort_order=6)
        ]
        
        db.add_all(sizes + colors + brand_filters)
        db.commit()
        
        print(f"✅ Created {len(sizes)} sizes, {len(colors)} colors, {len(brand_filters)} brands")
        
        # 2. Create Product Seasons
        print("\n📅 Creating Product Seasons...")
        
        seasons = [
            ProductSeason(
                name="Лето",
                slug="summer",
                description="Летняя одежда",
                sort_order=1
            ),
            ProductSeason(
                name="Зима",
                slug="winter", 
                description="Зимняя одежда",
                sort_order=2
            ),
            ProductSeason(
                name="Мульти",
                slug="multi",
                description="Всесезонная одежда",
                sort_order=3
            ),
            ProductSeason(
                name="Весна",
                slug="spring",
                description="Весенняя одежда",
                sort_order=4
            ),
            ProductSeason(
                name="Осень",
                slug="autumn",
                description="Осенняя одежда",
                sort_order=5
            )
        ]
        
        db.add_all(seasons)
        db.commit()
        for season in seasons:
            db.refresh(season)
        
        print(f"✅ Created {len(seasons)} seasons")
        
        # 3. Create Product Materials
        print("\n🧵 Creating Product Materials...")
        
        materials = [
            ProductMaterial(
                name="Хлопок",
                slug="cotton",
                description="100% хлопок",
                sort_order=1
            ),
            ProductMaterial(
                name="Полиэстер",
                slug="polyester",
                description="100% полиэстер",
                sort_order=2
            ),
            ProductMaterial(
                name="Хлопок + Полиэстер",
                slug="cotton-polyester",
                description="Смесь хлопка и полиэстера",
                sort_order=3
            ),
            ProductMaterial(
                name="Шерсть",
                slug="wool",
                description="Натуральная шерсть",
                sort_order=4
            ),
            ProductMaterial(
                name="Джинс",
                slug="denim",
                description="Джинсовая ткань",
                sort_order=5
            ),
            ProductMaterial(
                name="Трикотаж",
                slug="knit",
                description="Трикотажная ткань",
                sort_order=6
            )
        ]
        
        db.add_all(materials)
        db.commit()
        for material in materials:
            db.refresh(material)
        
        print(f"✅ Created {len(materials)} materials")
        
        # 4. Create Product Styles
        print("\n🎨 Creating Product Styles...")
        
        styles = [
            ProductStyle(
                name="Спортивный",
                slug="sport",
                description="Спортивный стиль одежды",
                sort_order=1
            ),
            ProductStyle(
                name="Классический",
                slug="classic",
                description="Классический стиль одежды",
                sort_order=2
            ),
            ProductStyle(
                name="Повседневный",
                slug="casual",
                description="Повседневный стиль одежды",
                sort_order=3
            ),
            ProductStyle(
                name="Деловой",
                slug="business",
                description="Деловой стиль одежды",
                sort_order=4
            ),
            ProductStyle(
                name="Молодёжный",
                slug="youth",
                description="Молодёжный стиль одежды",
                sort_order=5
            ),
            ProductStyle(
                name="Элегантный",
                slug="elegant",
                description="Элегантный стиль одежды",
                sort_order=6
            )
        ]
        
        db.add_all(styles)
        db.commit()
        for style in styles:
            db.refresh(style)
        
        print(f"✅ Created {len(styles)} styles")
        
        # 5. Create Sample Product Discounts
        print("\n💰 Creating Sample Product Discounts...")
        
        # Get some products to add discounts to
        products = db.query(Product).limit(3).all()
        
        discounts = []
        for i, product in enumerate(products):
            if i == 0:
                # 20% discount
                discount = ProductDiscount(
                    product_id=product.id,
                    discount_type="percentage",
                    discount_value=20.0,
                    original_price=2999.0,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=30)
                )
            elif i == 1:
                # Fixed amount discount
                discount = ProductDiscount(
                    product_id=product.id,
                    discount_type="fixed",
                    discount_value=500.0,
                    original_price=2499.0,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=15)
                )
            else:
                # 15% discount
                discount = ProductDiscount(
                    product_id=product.id,
                    discount_type="percentage",
                    discount_value=15.0,
                    original_price=3999.0,
                    start_date=datetime.now(),
                    end_date=datetime.now() + timedelta(days=7)
                )
            
            discounts.append(discount)
        
        db.add_all(discounts)
        db.commit()
        
        print(f"✅ Created {len(discounts)} product discounts")
        
        # 6. Create Sample Search Terms
        print("\n🔍 Creating Sample Search Terms...")
        
        search_terms = [
            ProductSearch(search_term="футболка", search_count=45, last_searched=datetime.now()),
            ProductSearch(search_term="джинсы", search_count=32, last_searched=datetime.now()),
            ProductSearch(search_term="кроссовки", search_count=28, last_searched=datetime.now()),
            ProductSearch(search_term="куртка", search_count=21, last_searched=datetime.now()),
            ProductSearch(search_term="рубашка", search_count=19, last_searched=datetime.now()),
            ProductSearch(search_term="H&M", search_count=15, last_searched=datetime.now()),
            ProductSearch(search_term="Nike", search_count=12, last_searched=datetime.now()),
            ProductSearch(search_term="черный", search_count=8, last_searched=datetime.now()),
            ProductSearch(search_term="белый", search_count=7, last_searched=datetime.now()),
            ProductSearch(search_term="спортивный", search_count=6, last_searched=datetime.now())
        ]
        
        db.add_all(search_terms)
        db.commit()
        
        print(f"✅ Created {len(search_terms)} search terms")
        
        print("\n🎉 Filter and Sort system created successfully!")
        print("\n📊 Summary:")
        print(f"   - {len(sizes)} size filters")
        print(f"   - {len(colors)} color filters")
        print(f"   - {len(brand_filters)} brand filters")
        print(f"   - {len(seasons)} seasons")
        print(f"   - {len(materials)} materials")
        print(f"   - {len(styles)} styles")
        print(f"   - {len(discounts)} product discounts")
        print(f"   - {len(search_terms)} search terms")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating filter system: {e}")
        return False
    finally:
        db.close()

def show_filter_usage():
    """Show how to use the filter and sort system"""
    print("\n🔍 FILTER AND SORT SYSTEM USAGE")
    print("=" * 50)
    print()
    print("📏 Available Sizes:")
    print("   ✅ 40, 42, 44, 46, 48, 50")
    print()
    print("🎨 Available Colors:")
    print("   ✅ Чёрный, Белый, Бежевый, Серый")
    print("   ✅ Красный, Синий, Зелёный, Коричневый")
    print()
    print("🏷️ Available Brands:")
    print("   ✅ Ecco, Vans, MANGO, H&M")
    print("   ✅ Nike, Adidas")
    print()
    print("📅 Available Seasons:")
    print("   ✅ Лето, Зима, Мульти, Весна, Осень")
    print()
    print("🧵 Available Materials:")
    print("   ✅ Хлопок, Полиэстер, Хлопок+Полиэстер")
    print("   ✅ Шерсть, Джинс, Трикотаж")
    print()
    print("🎨 Available Styles:")
    print("   ✅ Спортивный, Классический, Повседневный")
    print("   ✅ Деловой, Молодёжный, Элегантный")
    print()
    print("💰 Discount Types:")
    print("   ✅ Percentage: 20% скидка")
    print("   ✅ Fixed: 500 сом скидка")
    print()
    print("🔄 Sorting Options:")
    print("   ✅ Новинки (New arrivals)")
    print("   ✅ Популярное (Popular)")
    print("   ✅ Сначала дороже (Price: high to low)")
    print("   ✅ Сначала дешевле (Price: low to high)")
    print("   ✅ По величине скидки (By discount amount)")
    print("   ✅ Подобрали для вас (Selected for you)")
    print()
    print("🔍 Search Functionality:")
    print("   ✅ Search by product title")
    print("   ✅ Search by brand name")
    print("   ✅ Search by description")
    print("   ✅ Analytics tracking")
    print()
    print("🚀 How to Access SQLAdmin:")
    print("   1. Run: python main_admin.py")
    print("   2. Visit: http://localhost:8001/admin")
    print("   3. Login: content_admin / admin123")
    print("   4. Manage: Фильтры товаров, Сезоны, Материалы, Стили, Скидки")

def demonstrate_filtering():
    """Demonstrate how to use the filtering system"""
    db = SessionLocal()
    
    try:
        print("\n🔍 FILTERING EXAMPLES")
        print("=" * 30)
        
        # Example 1: Filter by category and subcategory
        print("\n1. Filter by Category & Subcategory:")
        men_tshirts = Product.filter_by_subcategory(db, "men", "t-shirts-polos")
        print(f"   Found {len(men_tshirts)} products in Men's T-shirts")
        
        # Example 2: Filter by price range
        print("\n2. Filter by Price Range:")
        affordable_products = Product.filter_by_price_range(db, min_price=1000, max_price=3000)
        print(f"   Found {len(affordable_products)} products between 1000-3000 сом")
        
        # Example 3: Filter by color
        print("\n3. Filter by Color:")
        black_products = Product.filter_by_color(db, "black")
        print(f"   Found {len(black_products)} black products")
        
        # Example 4: Search by term
        print("\n4. Search by Term:")
        search_results = Product.search_by_term(db, "футболка")
        print(f"   Found {len(search_results)} products matching 'футболка'")
        
        # Example 5: Sort by newest
        print("\n5. Sort by Newest:")
        newest_products = Product.sort_by_newest(db)
        print(f"   Showing {min(5, len(newest_products))} newest products")
        for product in newest_products[:5]:
            print(f"   - {product.title} (created: {product.created_at.strftime('%Y-%m-%d')})")
        
        # Example 6: Sort by popularity
        print("\n6. Sort by Popularity:")
        popular_products = Product.sort_by_popular(db)
        print(f"   Showing {min(5, len(popular_products))} most popular products")
        for product in popular_products[:5]:
            print(f"   - {product.title} (sold: {product.sold_count})")
        
        # Example 7: Sort by price
        print("\n7. Sort by Price (Low to High):")
        cheap_products = Product.sort_by_price_low_to_high(db)
        print(f"   Showing {min(5, len(cheap_products))} cheapest products")
        for product in cheap_products[:5]:
            print(f"   - {product.title} (price: {product.price_range})")
        
    except Exception as e:
        print(f"❌ Error demonstrating filters: {e}")
    finally:
        db.close()

def main():
    """Main function"""
    print("🔍 MARQUE FILTER & SORT SETUP")
    print("=" * 40)
    
    if create_filter_system():
        show_filter_usage()
        demonstrate_filtering()
        print("\n✅ Filter and sort setup completed successfully!")
        print("   Now you can run: python main_admin.py")
        print("   Then visit: http://localhost:8001/admin")
        print("   Manage filters in: Фильтры товаров, Сезоны, Материалы, Стили, Скидки")
    else:
        print("\n❌ Filter and sort setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
