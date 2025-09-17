"""
Catalog Setup Example - Creating the complete catalog structure
This demonstrates how to set up categories, subcategories, brands, and products
to match the catalog design from the Marque website.
"""

from src.app_01.db import SessionLocal
from src.app_01.models import (
    Category, Subcategory, Brand, Product, SKU, ProductAsset, ProductAttribute
)
from datetime import datetime

def create_catalog_structure():
    """Create the complete catalog structure matching the design"""
    db = SessionLocal()
    
    try:
        print("🏗️ Creating Marque Catalog Structure...")
        
        # 1. Create Main Categories (Мужчинам, Женщинам, Детям, etc.)
        print("\n📂 Creating Main Categories...")
        
        categories = [
            Category(
                name="Мужчинам",
                slug="men",
                description="Одежда для мужчин",
                icon="fa-solid fa-mars",
                sort_order=1
            ),
            Category(
                name="Женщинам", 
                slug="women",
                description="Одежда для женщин",
                icon="fa-solid fa-venus",
                sort_order=2
            ),
            Category(
                name="Детям",
                slug="kids",
                description="Детская одежда",
                icon="fa-solid fa-child",
                sort_order=3
            ),
            Category(
                name="Спорт",
                slug="sport",
                description="Спортивная одежда",
                icon="fa-solid fa-dumbbell",
                sort_order=4
            ),
            Category(
                name="Обувь",
                slug="shoes",
                description="Обувь для всех",
                icon="fa-solid fa-shoe-prints",
                sort_order=5
            ),
            Category(
                name="Аксессуары",
                slug="accessories",
                description="Аксессуары и украшения",
                icon="fa-solid fa-gem",
                sort_order=6
            ),
            Category(
                name="Бренды",
                slug="brands",
                description="Популярные бренды",
                icon="fa-solid fa-star",
                sort_order=7
            )
        ]
        
        db.add_all(categories)
        db.commit()
        for category in categories:
            db.refresh(category)
        
        print(f"✅ Created {len(categories)} main categories")
        
        # 2. Create Subcategories for "Мужчинам" (Men)
        print("\n👔 Creating Subcategories for Men...")
        
        men_category = categories[0]  # Мужчинам
        men_subcategories = [
            Subcategory(
                category_id=men_category.id,
                name="Футболки и поло",
                slug="t-shirts-polos",
                description="Футболки и поло для мужчин",
                image_url="https://example.com/images/men-t-shirts.jpg",
                sort_order=1
            ),
            Subcategory(
                category_id=men_category.id,
                name="Свитшоты и худи",
                slug="sweatshirts-hoodies", 
                description="Свитшоты и худи для мужчин",
                image_url="https://example.com/images/men-sweatshirts.jpg",
                sort_order=2
            ),
            Subcategory(
                category_id=men_category.id,
                name="Брюки и шорты",
                slug="pants-shorts",
                description="Брюки и шорты для мужчин",
                image_url="https://example.com/images/men-pants.jpg",
                sort_order=3
            ),
            Subcategory(
                category_id=men_category.id,
                name="Верхняя одежда",
                slug="outerwear",
                description="Куртки и пальто для мужчин",
                image_url="https://example.com/images/men-jackets.jpg",
                sort_order=4
            ),
            Subcategory(
                category_id=men_category.id,
                name="Нижнее бельё",
                slug="underwear",
                description="Нижнее бельё для мужчин",
                image_url="https://example.com/images/men-underwear.jpg",
                sort_order=5
            ),
            Subcategory(
                category_id=men_category.id,
                name="Рубашки",
                slug="shirts",
                description="Рубашки для мужчин",
                image_url="https://example.com/images/men-shirts.jpg",
                sort_order=6
            ),
            Subcategory(
                category_id=men_category.id,
                name="Джинсы",
                slug="jeans",
                description="Джинсы для мужчин",
                image_url="https://example.com/images/men-jeans.jpg",
                sort_order=7
            ),
            Subcategory(
                category_id=men_category.id,
                name="Костюмы и пиджаки",
                slug="suits-jackets",
                description="Костюмы и пиджаки для мужчин",
                image_url="https://example.com/images/men-suits.jpg",
                sort_order=8
            ),
            Subcategory(
                category_id=men_category.id,
                name="Спортивная одежда",
                slug="sportswear",
                description="Спортивная одежда для мужчин",
                image_url="https://example.com/images/men-sportswear.jpg",
                sort_order=9
            ),
            Subcategory(
                category_id=men_category.id,
                name="Домашняя одежда",
                slug="homewear",
                description="Домашняя одежда для мужчин",
                image_url="https://example.com/images/men-homewear.jpg",
                sort_order=10
            )
        ]
        
        db.add_all(men_subcategories)
        db.commit()
        for subcategory in men_subcategories:
            db.refresh(subcategory)
        
        print(f"✅ Created {len(men_subcategories)} subcategories for Men")
        
        # 3. Create Brands
        print("\n🏷️ Creating Brands...")
        
        brands = [
            Brand(
                name="H&M",
                slug="hm",
                description="Шведский бренд модной одежды",
                country="Sweden",
                sort_order=1
            ),
            Brand(
                name="Zara",
                slug="zara", 
                description="Испанский бренд быстрой моды",
                country="Spain",
                sort_order=2
            ),
            Brand(
                name="Nike",
                slug="nike",
                description="Американский спортивный бренд",
                country="USA",
                sort_order=3
            ),
            Brand(
                name="Adidas",
                slug="adidas",
                description="Немецкий спортивный бренд",
                country="Germany",
                sort_order=4
            ),
            Brand(
                name="Uniqlo",
                slug="uniqlo",
                description="Японский бренд базовой одежды",
                country="Japan",
                sort_order=5
            ),
            Brand(
                name="Levi's",
                slug="levis",
                description="Американский бренд джинсов",
                country="USA",
                sort_order=6
            )
        ]
        
        db.add_all(brands)
        db.commit()
        for brand in brands:
            db.refresh(brand)
        
        print(f"✅ Created {len(brands)} brands")
        
        # 4. Create Product Attributes (Sizes, Colors)
        print("\n📏 Creating Product Attributes...")
        
        # Sizes
        sizes = [
            ProductAttribute(attribute_type="size", attribute_value="RUS 40", display_name="RUS 40", sort_order=1),
            ProductAttribute(attribute_type="size", attribute_value="RUS 42", display_name="RUS 42", sort_order=2),
            ProductAttribute(attribute_type="size", attribute_value="RUS 44", display_name="RUS 44", sort_order=3),
            ProductAttribute(attribute_type="size", attribute_value="RUS 46", display_name="RUS 46", sort_order=4),
            ProductAttribute(attribute_type="size", attribute_value="RUS 48", display_name="RUS 48", sort_order=5),
            ProductAttribute(attribute_type="size", attribute_value="RUS 50", display_name="RUS 50", sort_order=6)
        ]
        
        # Colors
        colors = [
            ProductAttribute(attribute_type="color", attribute_value="black", display_name="Черный", sort_order=1),
            ProductAttribute(attribute_type="color", attribute_value="white", display_name="Белый", sort_order=2),
            ProductAttribute(attribute_type="color", attribute_value="red", display_name="Красный", sort_order=3),
            ProductAttribute(attribute_type="color", attribute_value="blue", display_name="Синий", sort_order=4),
            ProductAttribute(attribute_type="color", attribute_value="green", display_name="Зеленый", sort_order=5),
            ProductAttribute(attribute_type="color", attribute_value="gray", display_name="Серый", sort_order=6),
            ProductAttribute(attribute_type="color", attribute_value="brown", display_name="Коричневый", sort_order=7)
        ]
        
        db.add_all(sizes + colors)
        db.commit()
        
        print(f"✅ Created {len(sizes)} sizes and {len(colors)} colors")
        
        # 5. Create Sample Products
        print("\n🛍️ Creating Sample Products...")
        
        tshirts_subcategory = men_subcategories[0]  # Футболки и поло
        hm_brand = brands[0]  # H&M
        
        products = [
            Product(
                brand_id=hm_brand.id,
                category_id=men_category.id,
                subcategory_id=tshirts_subcategory.id,
                title="Футболка спорт. из хлопка",
                slug="hm-sport-cotton-tshirt",
                description="Спортивная футболка из качественного хлопка. Удобная и практичная для повседневной носки.",
                is_featured=True,
                attributes={
                    "gender": "Мужской",
                    "season": "Мульти",
                    "composition": "66% полиэстер, 34% хлопок",
                    "article": "236412"
                }
            ),
            Product(
                brand_id=hm_brand.id,
                category_id=men_category.id,
                subcategory_id=tshirts_subcategory.id,
                title="Футболка базовая белая",
                slug="hm-basic-white-tshirt",
                description="Базовая белая футболка из 100% хлопка. Идеальна для повседневной носки.",
                is_featured=False,
                attributes={
                    "gender": "Мужской",
                    "season": "Мульти", 
                    "composition": "100% хлопок",
                    "article": "236413"
                }
            )
        ]
        
        db.add_all(products)
        db.commit()
        for product in products:
            db.refresh(product)
        
        # 6. Create SKUs for products
        print("\n🏷️ Creating SKUs...")
        
        skus = [
            # First product SKUs
            SKU(
                product_id=products[0].id,
                sku_code="Артикул/236412-BLK-40",
                size="RUS 40",
                color="black",
                price=2999.0,
                stock=15
            ),
            SKU(
                product_id=products[0].id,
                sku_code="Артикул/236412-BLK-42",
                size="RUS 42",
                color="black", 
                price=2999.0,
                stock=12
            ),
            SKU(
                product_id=products[0].id,
                sku_code="Артикул/236412-WHT-40",
                size="RUS 40",
                color="white",
                price=2999.0,
                stock=8
            ),
            # Second product SKUs
            SKU(
                product_id=products[1].id,
                sku_code="Артикул/236413-WHT-42",
                size="RUS 42",
                color="white",
                price=2499.0,
                stock=20
            ),
            SKU(
                product_id=products[1].id,
                sku_code="Артикул/236413-WHT-44",
                size="RUS 44",
                color="white",
                price=2499.0,
                stock=18
            )
        ]
        
        db.add_all(skus)
        db.commit()
        
        print(f"✅ Created {len(skus)} SKUs")
        
        # 7. Create Product Assets
        print("\n🖼️ Creating Product Assets...")
        
        assets = [
            ProductAsset(
                product_id=products[0].id,
                url="https://example.com/images/hm-sport-tshirt-main.jpg",
                type="image",
                alt_text="H&M спортивная футболка - основной вид",
                order=1
            ),
            ProductAsset(
                product_id=products[0].id,
                url="https://example.com/images/hm-sport-tshirt-side.jpg",
                type="image", 
                alt_text="H&M спортивная футболка - боковой вид",
                order=2
            ),
            ProductAsset(
                product_id=products[1].id,
                url="https://example.com/images/hm-basic-tshirt-main.jpg",
                type="image",
                alt_text="H&M базовая белая футболка",
                order=1
            )
        ]
        
        db.add_all(assets)
        db.commit()
        
        print(f"✅ Created {len(assets)} product assets")
        
        print("\n🎉 Catalog structure created successfully!")
        print("\n📊 Summary:")
        print(f"   - {len(categories)} main categories")
        print(f"   - {len(men_subcategories)} subcategories for Men")
        print(f"   - {len(brands)} brands")
        print(f"   - {len(sizes + colors)} product attributes")
        print(f"   - {len(products)} sample products")
        print(f"   - {len(skus)} product SKUs")
        print(f"   - {len(assets)} product assets")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating catalog structure: {e}")
        return False
    finally:
        db.close()

def show_catalog_usage():
    """Show how to use the catalog structure"""
    print("\n🌐 CATALOG STRUCTURE USAGE")
    print("=" * 50)
    print()
    print("📂 Main Categories:")
    print("   👔 Мужчинам (men)")
    print("   👗 Женщинам (women)")
    print("   👶 Детям (kids)")
    print("   🏃 Спорт (sport)")
    print("   👟 Обувь (shoes)")
    print("   💎 Аксессуары (accessories)")
    print("   ⭐ Бренды (brands)")
    print()
    print("👔 Men's Subcategories:")
    print("   📝 Футболки и поло (t-shirts-polos)")
    print("   🧥 Свитшоты и худи (sweatshirts-hoodies)")
    print("   👖 Брюки и шорты (pants-shorts)")
    print("   🧥 Верхняя одежда (outerwear)")
    print("   🩲 Нижнее бельё (underwear)")
    print("   👔 Рубашки (shirts)")
    print("   👖 Джинсы (jeans)")
    print("   🤵 Костюмы и пиджаки (suits-jackets)")
    print("   🏃 Спортивная одежда (sportswear)")
    print("   🏠 Домашняя одежда (homewear)")
    print()
    print("🏷️ Popular Brands:")
    print("   🛍️ H&M (Sweden)")
    print("   🛍️ Zara (Spain)")
    print("   👟 Nike (USA)")
    print("   👟 Adidas (Germany)")
    print("   👕 Uniqlo (Japan)")
    print("   👖 Levi's (USA)")
    print()
    print("📏 Available Sizes: RUS 40, 42, 44, 46, 48, 50")
    print("🎨 Available Colors: Черный, Белый, Красный, Синий, Зеленый, Серый, Коричневый")
    print()
    print("🚀 How to Access SQLAdmin:")
    print("   1. Run: python main_admin.py")
    print("   2. Visit: http://localhost:8001/admin")
    print("   3. Login: content_admin / admin123")
    print("   4. Manage: Категории, Подкатегории, Бренды, Товары")

def main():
    """Main function"""
    print("🏗️ MARQUE CATALOG SETUP")
    print("=" * 40)
    
    if create_catalog_structure():
        show_catalog_usage()
        print("\n✅ Catalog setup completed successfully!")
        print("   Now you can run: python main_admin.py")
        print("   Then visit: http://localhost:8001/admin")
    else:
        print("\n❌ Catalog setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
