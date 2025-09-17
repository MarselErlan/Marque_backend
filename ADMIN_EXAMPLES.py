"""
Examples demonstrating the two admin types:
1. Order Management Admin - Manages orders, status changes, daily stats
2. Website Content Admin - Manages products, sizes, colors, website content
"""

from src.app_01.db import SessionLocal
from src.app_01.models import (
    User, Admin, AdminLog, OrderAdminStats, ContentAdminSettings, 
    ProductAttribute, Order, OrderStatus, Product, SKU, Review
)
from datetime import date, datetime

def create_admin_users():
    """Create example admin users for both types"""
    db = SessionLocal()
    
    try:
        # Create regular users first
        user1 = User(
            email="order.admin@marque.com",
            username="order_admin",
            hashed_password="hashed_password",
            full_name="Азамат Токтосунов",
            is_active=True,
            is_verified=True
        )
        
        user2 = User(
            email="content.admin@marque.com", 
            username="content_admin",
            hashed_password="hashed_password",
            full_name="Айгерим Сыдыкова",
            is_active=True,
            is_verified=True
        )
        
        db.add_all([user1, user2])
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        
        # Create Order Management Admin
        order_admin = Admin(
            user_id=user1.id,
            admin_role="order_management"
        )
        order_admin.setup_default_permissions()
        
        # Create Website Content Admin  
        content_admin = Admin(
            user_id=user2.id,
            admin_role="website_content"
        )
        content_admin.setup_default_permissions()
        
        db.add_all([order_admin, content_admin])
        db.commit()
        db.refresh(order_admin)
        db.refresh(content_admin)
        
        print(f"✅ Created Order Admin: {order_admin.role_display_name}")
        print(f"✅ Created Content Admin: {content_admin.role_display_name}")
        
        return order_admin, content_admin
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin users: {e}")
        return None, None
    finally:
        db.close()

def order_management_admin_examples(order_admin):
    """Examples for Order Management Admin functionality"""
    db = SessionLocal()
    
    try:
        print("\n📦 ORDER MANAGEMENT ADMIN EXAMPLES")
        print("=" * 50)
        
        # 1. Check admin permissions
        print(f"Admin: {order_admin.user.full_name}")
        print(f"Role: {order_admin.role_display_name}")
        print(f"Can manage orders: {order_admin.can_manage_orders()}")
        print(f"Can manage products: {order_admin.can_manage_products()}")
        print(f"Permissions: {order_admin.permissions}")
        
        # 2. Create today's order statistics
        today_stats = OrderAdminStats(
            date=date.today(),
            today_orders_count=15,
            today_orders_pending=3,
            today_orders_processing=5,
            today_orders_shipped=4,
            today_orders_delivered=2,
            today_orders_cancelled=1,
            today_sales_total=25430.0,
            today_sales_count=6,
            avg_order_value=4238.33,
            completion_rate=13.33
        )
        
        db.add(today_stats)
        db.commit()
        
        print(f"\n📊 Today's Statistics:")
        print(f"Total Orders: {today_stats.today_orders_count}")
        print(f"Sales Total: {today_stats.formatted_sales_total}")
        print(f"Orders by Status:")
        for status, count in today_stats.orders_status_summary.items():
            label = today_stats.status_labels[status]
            print(f"  - {label}: {count}")
        
        # 3. Create sample orders for demonstration
        user = db.query(User).first()
        if user:
            order = Order(
                user=user,
                order_number="#1021",
                customer_name=user.full_name,
                customer_phone="+996 700 123 456",
                delivery_address="г. Чуйская, 17",
                status=OrderStatus.PENDING,
                subtotal=2999.0,
                total_amount=2999.0
            )
            
            db.add(order)
            db.commit()
            db.refresh(order)
            
            print(f"\n📋 Sample Order Created:")
            print(f"Order #{order.order_number}")
            print(f"Status: {order.status_display}")
            print(f"Amount: {order.total_amount} KGS")
            
            # 4. Change order status (Order Management Admin function)
            print(f"\n🔄 Changing Order Status:")
            print(f"Before: {order.status_display}")
            
            order.confirm_order()
            db.commit()
            print(f"After: {order.status_display}")
            
            order.ship_order()
            db.commit()
            print(f"After: {order.status_display}")
            
            # 5. Log admin activity
            admin_log = AdminLog(
                admin_id=order_admin.id,
                action="update",
                entity_type="order",
                entity_id=order.id,
                description=f"Changed order status to {order.status_display}",
                ip_address="192.168.1.1"
            )
            db.add(admin_log)
            db.commit()
            
            print(f"✅ Admin activity logged: {admin_log.action_description}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error in order management examples: {e}")
    finally:
        db.close()

def website_content_admin_examples(content_admin):
    """Examples for Website Content Admin functionality"""
    db = SessionLocal()
    
    try:
        print("\n🌐 WEBSITE CONTENT ADMIN EXAMPLES")
        print("=" * 50)
        
        # 1. Check admin permissions
        print(f"Admin: {content_admin.user.full_name}")
        print(f"Role: {content_admin.role_display_name}")
        print(f"Can manage orders: {content_admin.can_manage_orders()}")
        print(f"Can manage products: {content_admin.can_manage_products()}")
        print(f"Permissions: {content_admin.permissions}")
        
        # 2. Create content admin settings
        content_settings = ContentAdminSettings(
            admin_id=content_admin.id,
            default_currency="KGS",
            default_language="ru",
            auto_generate_sku=True,
            require_product_images=True,
            max_images_per_product=10,
            available_sizes=["RUS 40", "RUS 42", "RUS 44", "RUS 46"],
            available_colors=["black", "white", "red", "blue", "green"],
            auto_approve_reviews=False,
            require_review_approval=True,
            notify_on_new_orders=True,
            notify_on_low_stock=True
        )
        
        db.add(content_settings)
        db.commit()
        db.refresh(content_settings)
        
        print(f"\n⚙️ Content Admin Settings:")
        print(f"Default Currency: {content_settings.default_currency}")
        print(f"Available Sizes: {content_settings.available_sizes}")
        print(f"Available Colors: {content_settings.available_colors}")
        print(f"Auto Generate SKU: {content_settings.auto_generate_sku}")
        
        # 3. Manage product attributes (sizes, colors)
        print(f"\n🏷️ Managing Product Attributes:")
        
        # Add new sizes
        size_48 = ProductAttribute.add_size(
            session=db,
            size_value="RUS 48",
            display_name="RUS 48",
            admin_id=content_admin.id
        )
        size_50 = ProductAttribute.add_size(
            session=db,
            size_value="RUS 50", 
            display_name="RUS 50",
            admin_id=content_admin.id
        )
        
        # Add new colors
        color_pink = ProductAttribute.add_color(
            session=db,
            color_value="pink",
            display_name="Розовый",
            admin_id=content_admin.id
        )
        color_gray = ProductAttribute.add_color(
            session=db,
            color_value="gray",
            display_name="Серый", 
            admin_id=content_admin.id
        )
        
        db.add_all([size_48, size_50, color_pink, color_gray])
        db.commit()
        
        print(f"✅ Added sizes: RUS 48, RUS 50")
        print(f"✅ Added colors: Розовый, Серый")
        
        # 4. Get all available attributes
        all_sizes = ProductAttribute.get_sizes(db)
        all_colors = ProductAttribute.get_colors(db)
        
        print(f"\n📋 Available Attributes:")
        print(f"Sizes: {[size.attribute_value for size in all_sizes]}")
        print(f"Colors: {[color.formatted_display_name for color in all_colors]}")
        
        # 5. Create a product with the new attributes
        product = Product(
            brand="H&M",
            title="Футболка спорт. из хлопка",
            slug="hm-sport-cotton-tshirt",
            description="Спортивная футболка из качественного хлопка",
            attributes={
                "gender": "Мужской/Женский",
                "season": "Мульти",
                "composition": "66% полиэстер, 34% хлопок"
            }
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        # Create SKUs with different sizes and colors
        sku1 = SKU(
            product_id=product.id,
            sku_code="Артикул/236412-BLK-48",
            size="RUS 48",
            color="black",
            price=2999.0,
            stock=10
        )
        
        sku2 = SKU(
            product_id=product.id,
            sku_code="Артикул/236412-PINK-46",
            size="RUS 46", 
            color="pink",
            price=2999.0,
            stock=8
        )
        
        db.add_all([sku1, sku2])
        db.commit()
        
        print(f"\n🛍️ Product Created:")
        print(f"Product: {product.title}")
        print(f"Brand: {product.brand}")
        print(f"SKUs: {len(product.skus)} variants")
        for sku in product.skus:
            print(f"  - {sku.size} ({sku.color}): {sku.formatted_price}")
        
        # 6. Log content admin activity
        admin_log = AdminLog(
            admin_id=content_admin.id,
            action="create",
            entity_type="product",
            entity_id=product.id,
            description=f"Created new product: {product.title}",
            ip_address="192.168.1.2"
        )
        db.add(admin_log)
        db.commit()
        
        print(f"✅ Admin activity logged: {admin_log.action_description}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error in content admin examples: {e}")
    finally:
        db.close()

def main():
    """Main function to run all examples"""
    print("🚀 MARQUE ADMIN SYSTEM EXAMPLES")
    print("=" * 60)
    
    # Create admin users
    order_admin, content_admin = create_admin_users()
    
    if order_admin and content_admin:
        # Run order management examples
        order_management_admin_examples(order_admin)
        
        # Run content management examples  
        website_content_admin_examples(content_admin)
        
        print("\n✅ All examples completed successfully!")
        print("\n📝 Summary:")
        print("- Order Management Admin: Manages orders, status changes, daily statistics")
        print("- Website Content Admin: Manages products, sizes, colors, website content")
        print("- Both admins have role-based permissions and activity logging")
        print("- Perfect for the admin panel design you showed!")

if __name__ == "__main__":
    main()
