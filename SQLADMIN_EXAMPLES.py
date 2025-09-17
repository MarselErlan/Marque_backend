"""
SQLAdmin Examples for Website Content Management
This file demonstrates how to use the SQLAdmin interface for managing website content.
"""

from src.app_01.db import SessionLocal
from src.app_01.models import (
    Product, SKU, ProductAsset, ProductAttribute, Review, User,
    Admin, AdminLog
)
from datetime import datetime

def create_sample_data():
    """Create sample data for testing the SQLAdmin interface"""
    db = SessionLocal()
    
    try:
        print("🚀 Creating sample data for SQLAdmin interface...")
        
        # 1. Create a user
        user = User(
            email="content.admin@marque.com",
            username="content_admin",
            hashed_password="hashed_password_here",
            full_name="Айгерим Сыдыкова",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 2. Create admin
        admin = Admin(
            user_id=user.id,
            admin_role="website_content"
        )
        admin.setup_default_permissions()
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        # 3. Admin created successfully
        
        # 4. Create product attributes
        sizes = [
            ProductAttribute(
                attribute_type="size",
                attribute_value="RUS 40",
                display_name="RUS 40",
                sort_order=1,
                created_by_admin_id=admin.id
            ),
            ProductAttribute(
                attribute_type="size",
                attribute_value="RUS 42",
                display_name="RUS 42",
                sort_order=2,
                created_by_admin_id=admin.id
            ),
            ProductAttribute(
                attribute_type="size",
                attribute_value="RUS 44",
                display_name="RUS 44",
                sort_order=3,
                created_by_admin_id=admin.id
            ),
            ProductAttribute(
                attribute_type="size",
                attribute_value="RUS 46",
                display_name="RUS 46",
                sort_order=4,
                created_by_admin_id=admin.id
            )
        ]
        
        colors = [
            ProductAttribute(
                attribute_type="color",
                attribute_value="black",
                display_name="Черный",
                sort_order=1,
                created_by_admin_id=admin.id
            ),
            ProductAttribute(
                attribute_type="color",
                attribute_value="white",
                display_name="Белый",
                sort_order=2,
                created_by_admin_id=admin.id
            ),
            ProductAttribute(
                attribute_type="color",
                attribute_value="red",
                display_name="Красный",
                sort_order=3,
                created_by_admin_id=admin.id
            )
        ]
        
        brands = [
            ProductAttribute(
                attribute_type="brand",
                attribute_value="H&M",
                display_name="H&M",
                sort_order=1,
                created_by_admin_id=admin.id
            ),
            ProductAttribute(
                attribute_type="brand",
                attribute_value="Zara",
                display_name="Zara",
                sort_order=2,
                created_by_admin_id=admin.id
            )
        ]
        
        db.add_all(sizes + colors + brands)
        db.commit()
        
        # 5. Create products
        products = [
            Product(
                brand="H&M",
                title="Футболка спорт. из хлопка",
                slug="hm-sport-cotton-tshirt",
                description="Спортивная футболка из качественного хлопка. Удобная и практичная для повседневной носки.",
                sold_count=120,
                rating_avg=4.4,
                rating_count=32,
                attributes={
                    "gender": "Мужской/Женский",
                    "season": "Мульти",
                    "composition": "66% полиэстер, 34% хлопок",
                    "article": "236412"
                }
            ),
            Product(
                brand="Zara",
                title="Джинсы классические",
                slug="zara-classic-jeans",
                description="Классические джинсы из денима. Универсальная модель для любого стиля.",
                sold_count=85,
                rating_avg=4.2,
                rating_count=28,
                attributes={
                    "gender": "Мужской",
                    "season": "Мульти",
                    "composition": "98% хлопок, 2% эластан",
                    "article": "789123"
                }
            )
        ]
        
        db.add_all(products)
        db.commit()
        db.refresh(products[0])
        db.refresh(products[1])
        
        # 6. Create SKUs for products
        skus = [
            # H&M T-shirt SKUs
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
            # Zara Jeans SKUs
            SKU(
                product_id=products[1].id,
                sku_code="Артикул/789123-BLU-42",
                size="RUS 42",
                color="blue",
                price=4500.0,
                stock=10
            ),
            SKU(
                product_id=products[1].id,
                sku_code="Артикул/789123-BLU-44",
                size="RUS 44",
                color="blue",
                price=4500.0,
                stock=7
            )
        ]
        
        db.add_all(skus)
        db.commit()
        
        # 7. Create product assets
        assets = [
            ProductAsset(
                product_id=products[0].id,
                url="https://example.com/images/hm-tshirt-main.jpg",
                type="image",
                alt_text="H&M спортивная футболка - основной вид",
                order=1
            ),
            ProductAsset(
                product_id=products[0].id,
                url="https://example.com/images/hm-tshirt-side.jpg",
                type="image",
                alt_text="H&M спортивная футболка - боковой вид",
                order=2
            ),
            ProductAsset(
                product_id=products[1].id,
                url="https://example.com/images/zara-jeans-main.jpg",
                type="image",
                alt_text="Zara классические джинсы - основной вид",
                order=1
            )
        ]
        
        db.add_all(assets)
        db.commit()
        
        # 8. Create reviews
        reviews = [
            Review(
                product_id=products[0].id,
                user_id=user.id,
                rating=5,
                text="Отличная футболка! Качество хорошее, размер соответствует. Очень довольна покупкой."
            ),
            Review(
                product_id=products[0].id,
                user_id=user.id,
                rating=4,
                text="Хорошая футболка, но немного мала. Рекомендую взять размер побольше."
            ),
            Review(
                product_id=products[1].id,
                user_id=user.id,
                rating=5,
                text="Отличные джинсы! Сидят идеально, качество на высоте. Рекомендую!"
            )
        ]
        
        db.add_all(reviews)
        db.commit()
        
        # 9. Create admin log entries
        admin_logs = [
            AdminLog(
                admin_id=admin.id,
                action="create",
                entity_type="product",
                entity_id=products[0].id,
                description=f"Создан товар: {products[0].title}",
                ip_address="192.168.1.1"
            ),
            AdminLog(
                admin_id=admin.id,
                action="create",
                entity_type="product",
                entity_id=products[1].id,
                description=f"Создан товар: {products[1].title}",
                ip_address="192.168.1.1"
            ),
            AdminLog(
                admin_id=admin.id,
                action="create",
                entity_type="attribute",
                entity_id=sizes[0].id,
                description=f"Добавлен размер: {sizes[0].attribute_value}",
                ip_address="192.168.1.1"
            )
        ]
        
        db.add_all(admin_logs)
        db.commit()
        
        print("✅ Sample data created successfully!")
        print(f"   - Created user: {user.full_name}")
        print(f"   - Created admin: {admin.role_display_name}")
        print(f"   - Created {len(products)} products")
        print(f"   - Created {len(skus)} SKUs")
        print(f"   - Created {len(assets)} assets")
        print(f"   - Created {len(reviews)} reviews")
        print(f"   - Created {len(sizes + colors + brands)} attributes")
        print(f"   - Created {len(admin_logs)} admin log entries")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating sample data: {e}")
        return False
    finally:
        db.close()

def show_sqladmin_usage():
    """Show how to use the SQLAdmin interface"""
    print("\n🌐 SQLADMIN WEBSITE CONTENT ADMIN INTERFACE")
    print("=" * 60)
    print()
    print("📋 Available Admin Sections:")
    print("   🛍️  Товары (Products)")
    print("      - Создание, редактирование, удаление товаров")
    print("      - Управление брендами, названиями, описаниями")
    print("      - Настройка атрибутов товаров")
    print()
    print("   🏷️  Артикулы (SKUs)")
    print("      - Создание вариантов товаров")
    print("      - Управление размерами и цветами")
    print("      - Настройка цен и остатков")
    print()
    print("   🖼️  Медиа файлы (Product Assets)")
    print("      - Загрузка изображений товаров")
    print("      - Управление видео контентом")
    print("      - Настройка порядка отображения")
    print()
    print("   📝 Атрибуты товаров (Product Attributes)")
    print("      - Управление размерами (RUS 40, 42, 44, 46)")
    print("      - Управление цветами (черный, белый, красный)")
    print("      - Управление брендами (H&M, Zara)")
    print("      - Управление категориями")
    print()
    print("   ⭐ Отзывы (Reviews)")
    print("      - Модерация отзывов покупателей")
    print("      - Управление рейтингами товаров")
    print("      - Одобрение/отклонение отзывов")
    print()
    print("   👥 Пользователи (Users)")
    print("      - Управление пользователями")
    print("      - Просмотр профилей")
    print("      - Активация/деактивация аккаунтов")
    print()
    print("   📊 Журнал действий (Admin Log)")
    print("      - Просмотр истории действий")
    print("      - Аудит изменений")
    print("      - Отслеживание активности")
    print()
    print("🚀 How to Access SQLAdmin Interface:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Create sample data: python SQLADMIN_EXAMPLES.py")
    print("   3. Run admin interface: python main_admin.py")
    print("   4. Open browser: http://localhost:8001/admin")
    print("   5. Login: username='content_admin', password='admin123'")
    print()
    print("🔧 Key Features:")
    print("   ✅ Русский интерфейс")
    print("   ✅ Красивый современный дизайн")
    print("   ✅ Поиск и фильтрация")
    print("   ✅ Сортировка по колонкам")
    print("   ✅ Массовые операции")
    print("   ✅ Валидация данных")
    print("   ✅ Безопасная аутентификация")
    print("   ✅ Аудит действий")
    print()
    print("📱 Perfect for Website Content Management:")
    print("   - Добавление новых товаров")
    print("   - Управление размерами и цветами")
    print("   - Загрузка изображений")
    print("   - Модерация отзывов")
    print("   - Управление каталогом")

def main():
    """Main function"""
    print("🚀 MARQUE SQLADMIN SETUP")
    print("=" * 40)
    
    # Create sample data
    if create_sample_data():
        # Show usage information
        show_sqladmin_usage()
        
        print("\n✅ Setup completed successfully!")
        print("   Now you can run: python main_admin.py")
        print("   Then visit: http://localhost:8001/admin")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
