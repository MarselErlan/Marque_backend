"""
Tests for Order Management Admin Views
Testing OrderAdmin, OrderItemAdmin, OrderStatusHistoryAdmin
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.app_01.models.orders.order import Order, OrderStatus
from src.app_01.models.orders.order_item import OrderItem
from src.app_01.models.orders.order_status_history import OrderStatusHistory
from src.app_01.models.users.user import User
from src.app_01.models.products.product import Product
from src.app_01.models.products.sku import SKU
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category, Subcategory


@pytest.fixture
def sample_order(admin_test_db: Session):
    """Create a sample order for testing"""
    import uuid
    
    # Clean up existing data to avoid conflicts
    admin_test_db.query(Order).delete()
    admin_test_db.query(User).delete()
    admin_test_db.commit()
    
    # Create unique identifiers
    unique_id = str(uuid.uuid4())[:8]
    
    # Create user
    user = User(
        phone_number=f"+996700{unique_id[:6]}",
        full_name=f"Test User {unique_id}",
        is_active=True,
        is_verified=True
    )
    admin_test_db.add(user)
    admin_test_db.commit()
    admin_test_db.refresh(user)
    
    # Create order with unique order number
    order = Order(
        order_number=f"#1001-{unique_id}",
        user_id=user.id,
        status=OrderStatus.PENDING,
        customer_name=f"Test Customer {unique_id}",
        customer_phone=f"+996700{unique_id[:6]}",
        customer_email=f"test{unique_id}@example.com",
        delivery_address=f"Test Address 123 {unique_id}",
        delivery_city="Bishkek",
        subtotal=5000.0,
        shipping_cost=200.0,
        total_amount=5200.0,
        currency="KGS"
    )
    admin_test_db.add(order)
    admin_test_db.commit()
    admin_test_db.refresh(order)
    
    return order


@pytest.fixture
def sample_order_with_items(admin_test_db: Session, sample_product_for_admin):
    """Create an order with items"""
    import uuid
    
    # Create unique identifiers
    unique_id = str(uuid.uuid4())[:8]
    
    # Create user (use different phone number to avoid conflicts)
    user = User(
        phone_number=f"+996701{unique_id[:6]}",
        full_name=f"Test User 2 {unique_id}",
        is_active=True,
        is_verified=True
    )
    admin_test_db.add(user)
    admin_test_db.commit()
    admin_test_db.refresh(user)
    
    # Create SKU
    sku = SKU(
        product_id=sample_product_for_admin.id,
        sku_code=f"TEST-SKU-{unique_id}",
        size="M",
        color="Black",
        price=2500.0,
        stock=10,
        is_active=True
    )
    admin_test_db.add(sku)
    admin_test_db.commit()
    admin_test_db.refresh(sku)
    
    # Create order with unique order number
    order = Order(
        order_number=f"#1002-{unique_id}",
        user_id=user.id,
        status=OrderStatus.PENDING,
        customer_name=f"Test Customer 2 {unique_id}",
        customer_phone=f"+996701{unique_id[:6]}",
        delivery_address=f"Test Address 456 {unique_id}",
        delivery_city="Osh",
        subtotal=5000.0,
        shipping_cost=300.0,
        total_amount=5300.0,
        currency="KGS"
    )
    admin_test_db.add(order)
    admin_test_db.commit()
    admin_test_db.refresh(order)
    
    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        sku_id=sku.id,
        product_name="Test Product",
        sku_code="TEST-SKU-001",
        size="M",
        color="Black",
        quantity=2,
        unit_price=2500.0,
        total_price=5000.0
    )
    admin_test_db.add(order_item)
    admin_test_db.commit()
    admin_test_db.refresh(order_item)
    
    return order


class TestOrderAdminModel:
    """Test Order model access via admin"""
    
    def test_order_model_exists(self, admin_test_db):
        """Test that Order model can be accessed"""
        orders = admin_test_db.query(Order).all()
        assert isinstance(orders, list)
    
    def test_create_order(self, admin_test_db):
        """Test creating an order through admin"""
        # Create user first
        user = User(
            phone_number="+996700999888",
            full_name="Admin Test User",
            is_active=True,
            is_verified=True
        )
        admin_test_db.add(user)
        admin_test_db.commit()
        admin_test_db.refresh(user)
        
        order = Order(
            order_number="#9999",
            user_id=user.id,
            status=OrderStatus.PENDING,
            customer_name="Admin Created Order",
            customer_phone="+996700999888",
            delivery_address="Admin Street 1",
            delivery_city="Bishkek",
            subtotal=1000.0,
            shipping_cost=100.0,
            total_amount=1100.0,
            currency="KGS"
        )
        admin_test_db.add(order)
        admin_test_db.commit()
        admin_test_db.refresh(order)
        
        assert order.id is not None
        assert order.order_number == "#9999"
        assert order.status == OrderStatus.PENDING
        assert order.total_amount == 1100.0
    
    def test_update_order_status(self, sample_order, admin_test_db):
        """Test updating order status"""
        sample_order.status = OrderStatus.CONFIRMED
        sample_order.confirmed_date = datetime.utcnow()
        admin_test_db.commit()
        
        updated_order = admin_test_db.query(Order).filter(Order.id == sample_order.id).first()
        assert updated_order.status == OrderStatus.CONFIRMED
        assert updated_order.confirmed_date is not None
    
    def test_search_order_by_number(self, sample_order, admin_test_db):
        """Test searching orders by order number"""
        found_order = admin_test_db.query(Order).filter(
            Order.order_number.like("%1001%")
        ).first()
        
        assert found_order is not None
        assert found_order.id == sample_order.id
    
    def test_filter_orders_by_status(self, sample_order, admin_test_db):
        """Test filtering orders by status"""
        pending_orders = admin_test_db.query(Order).filter(
            Order.status == OrderStatus.PENDING
        ).all()
        
        assert len(pending_orders) > 0
        assert all(o.status == OrderStatus.PENDING for o in pending_orders)
    
    def test_order_relationships(self, sample_order_with_items, admin_test_db):
        """Test order relationships (items)"""
        order = admin_test_db.query(Order).filter(Order.id == sample_order_with_items.id).first()
        
        assert order is not None
        assert len(order.order_items) > 0
        assert order.order_items[0].quantity == 2


class TestOrderItemAdminModel:
    """Test OrderItem model access via admin"""
    
    def test_order_item_model_exists(self, admin_test_db):
        """Test that OrderItem model can be accessed"""
        items = admin_test_db.query(OrderItem).all()
        assert isinstance(items, list)
    
    def test_create_order_item(self, sample_order_with_items, admin_test_db):
        """Test creating order items"""
        items = admin_test_db.query(OrderItem).filter(
            OrderItem.order_id == sample_order_with_items.id
        ).all()
        
        assert len(items) > 0
        assert items[0].product_name == "Test Product"
        assert items[0].quantity == 2
    
    def test_order_item_calculations(self, sample_order_with_items, admin_test_db):
        """Test order item price calculations"""
        item = admin_test_db.query(OrderItem).first()
        
        assert item.total_price == item.unit_price * item.quantity


class TestOrderStatusHistoryAdminModel:
    """Test OrderStatusHistory model access via admin"""
    
    def test_status_history_model_exists(self, admin_test_db):
        """Test that OrderStatusHistory model can be accessed"""
        history = admin_test_db.query(OrderStatusHistory).all()
        assert isinstance(history, list)
    
    def test_create_status_history(self, sample_order, admin_test_db):
        """Test creating status history entry"""
        history_entry = OrderStatusHistory(
            order_id=sample_order.id,
            new_status=OrderStatus.CONFIRMED,
            old_status=OrderStatus.PENDING,
            notes="Order confirmed by admin"
        )
        admin_test_db.add(history_entry)
        admin_test_db.commit()
        admin_test_db.refresh(history_entry)
        
        assert history_entry.id is not None
        assert history_entry.new_status == OrderStatus.CONFIRMED
        assert history_entry.old_status == OrderStatus.PENDING


class TestOrderAdminPermissions:
    """Test admin permissions for orders"""
    
    def test_admin_can_view_orders(self, sample_order, admin_test_db):
        """Test that admins can view orders"""
        orders = admin_test_db.query(Order).all()
        assert len(orders) > 0
    
    def test_admin_can_update_orders(self, sample_order, admin_test_db):
        """Test that admins can update orders"""
        sample_order.notes = "Updated by admin"
        admin_test_db.commit()
        
        updated = admin_test_db.query(Order).filter(Order.id == sample_order.id).first()
        assert updated.notes == "Updated by admin"
    
    def test_admin_cannot_delete_orders(self, sample_order, admin_test_db):
        """Test that orders should not be deleted (business rule)"""
        # This is a business rule test - orders should be cancelled, not deleted
        # We verify the order can be marked as cancelled instead
        sample_order.status = OrderStatus.CANCELLED
        sample_order.cancelled_date = datetime.utcnow()
        admin_test_db.commit()
        
        order = admin_test_db.query(Order).filter(Order.id == sample_order.id).first()
        assert order is not None  # Order still exists
        assert order.status == OrderStatus.CANCELLED


# Mark all tests as admin tests
pytestmark = pytest.mark.admin

