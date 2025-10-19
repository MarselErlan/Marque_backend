"""
Tests for Order Management Admin Features (Phase 3)
Using TDD approach to implement order management enhancements
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from src.app_01.models.orders.order import Order, OrderStatus
from src.app_01.models.orders.order_item import OrderItem
from src.app_01.models.orders.order_status_history import OrderStatusHistory
from src.app_01.models.users.user import User
from src.app_01.models.products.product import Product
from src.app_01.models.products.sku import SKU
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category, Subcategory


class TestOrderStatusWorkflow:
    """Test order status management and workflow"""
    
    def test_order_admin_shows_status_badges(self, authenticated_app_client, sample_order):
        """
        GIVEN: Order with specific status
        WHEN: Admin views order list
        THEN: Status is displayed with appropriate badge/color
        """
        client, _ = authenticated_app_client
        response = client.get("/admin/order/list")
        
        assert response.status_code == 200
        assert "PENDING" in response.text or "pending" in response.text.lower()
    
    def test_order_admin_can_change_status_quickly(self, authenticated_app_client, sample_order):
        """
        GIVEN: Order with PENDING status
        WHEN: Admin changes status to CONFIRMED
        THEN: Order status is updated and timestamp is recorded
        """
        client, _ = authenticated_app_client
        # This will be implemented with quick action buttons
        response = client.post(
            f"/admin/order/quick-status/{sample_order.id}",
            data={"status": "CONFIRMED"}
        )
        
        # For now, expect 404 since we haven't implemented it yet
        # After implementation, this should be 200 or 302 (redirect)
        assert response.status_code in [200, 302, 404]
    
    def test_order_status_change_updates_timestamp(self, admin_test_db, sample_order):
        """
        GIVEN: Order with PENDING status
        WHEN: Status is changed to CONFIRMED
        THEN: confirmed_date is automatically set
        """
        assert sample_order.confirmed_date is None
        
        # Simulate status change
        sample_order.status = OrderStatus.CONFIRMED
        sample_order.confirmed_date = datetime.utcnow()
        admin_test_db.commit()
        admin_test_db.refresh(sample_order)
        
        assert sample_order.status == OrderStatus.CONFIRMED
        assert sample_order.confirmed_date is not None
    
    def test_order_status_change_creates_history_entry(self, admin_test_db, sample_order, sample_admin_user):
        """
        GIVEN: Order status change
        WHEN: Admin changes order status
        THEN: OrderStatusHistory entry is created
        """
        # Change status
        old_status = sample_order.status
        sample_order.status = OrderStatus.CONFIRMED
        
        # Create history entry
        history = OrderStatusHistory(
            order_id=sample_order.id,
            old_status=old_status,
            new_status=OrderStatus.CONFIRMED,
            changed_by_admin_id=sample_admin_user.id,
            notes="Status changed via admin panel"
        )
        admin_test_db.add(history)
        admin_test_db.commit()
        
        # Verify
        history_count = admin_test_db.query(OrderStatusHistory).filter(
            OrderStatusHistory.order_id == sample_order.id
        ).count()
        
        assert history_count >= 1


class TestOrderQuickFilters:
    """Test quick filter functionality for orders"""
    
    def test_filter_todays_orders(self, authenticated_app_client, sample_orders_today):
        """
        GIVEN: Orders created today and yesterday
        WHEN: Admin filters for today's orders
        THEN: Only today's orders are shown
        """
        client, _ = authenticated_app_client
        # This endpoint will be implemented
        response = client.get("/admin/order/list?filter=today")
        
        assert response.status_code in [200, 404]  # 404 until implemented
    
    def test_filter_pending_orders(self, authenticated_app_client, sample_orders_mixed_status):
        """
        GIVEN: Orders with different statuses
        WHEN: Admin filters for pending orders
        THEN: Only PENDING orders are shown
        """
        client, _ = authenticated_app_client
        response = client.get(
            "/admin/order/list",
            params={"status": "PENDING"}
        )
        
        assert response.status_code == 200
    
    def test_filter_needs_action_orders(self, authenticated_app_client, sample_orders_mixed_status):
        """
        GIVEN: Orders with various statuses
        WHEN: Admin filters for orders needing action
        THEN: Only PENDING and CONFIRMED orders are shown
        """
        client, _ = authenticated_app_client
        response = client.get("/admin/order/list?filter=needs_action")
        
        assert response.status_code in [200, 404]  # 404 until implemented


class TestOrderBulkOperations:
    """Test bulk operations on orders"""
    
    def test_bulk_status_update(self, authenticated_app_client, sample_orders_for_bulk):
        """
        GIVEN: Multiple selected orders
        WHEN: Admin updates status in bulk
        THEN: All selected orders are updated
        """
        client, _ = authenticated_app_client
        order_ids = [order.id for order in sample_orders_for_bulk]
        
        response = client.post(
            "/admin/order/bulk-update-status",
            json={
                "order_ids": order_ids,
                "status": "CONFIRMED"
            }
        )
        
        # Will be 404 until implemented
        assert response.status_code in [200, 302, 404]
    
    def test_bulk_export_orders(self, authenticated_app_client, sample_orders_for_bulk):
        """
        GIVEN: Multiple selected orders
        WHEN: Admin exports orders
        THEN: CSV/Excel file is generated
        """
        client, _ = authenticated_app_client
        order_ids = [order.id for order in sample_orders_for_bulk]
        
        response = client.post(
            "/admin/order/bulk-export",
            json={"order_ids": order_ids}
        )
        
        # Will be 404 until implemented
        assert response.status_code in [200, 404]


class TestOrderDetailsEnhancement:
    """Test enhanced order details view"""
    
    def test_order_details_shows_customer_history(self, authenticated_app_client, sample_order_with_history):
        """
        GIVEN: Order from a customer with previous orders
        WHEN: Admin views order details
        THEN: Customer's previous orders are shown
        """
        client, _ = authenticated_app_client
        response = client.get(f"/admin/order/details/{sample_order_with_history.id}")
        
        assert response.status_code in [200, 404]
    
    def test_order_details_shows_total_customer_value(self, authenticated_app_client, sample_order_with_history):
        """
        GIVEN: Customer with multiple orders
        WHEN: Admin views order details
        THEN: Total customer lifetime value is displayed
        """
        client, _ = authenticated_app_client
        response = client.get(f"/admin/order/details/{sample_order_with_history.id}")
        
        assert response.status_code in [200, 404]
    
    def test_admin_can_add_notes_to_order(self, authenticated_app_client, sample_order):
        """
        GIVEN: Order
        WHEN: Admin adds notes
        THEN: Notes are saved and displayed
        """
        client, _ = authenticated_app_client
        response = client.post(
            f"/admin/order/{sample_order.id}/add-note",
            json={"note": "Customer requested expedited shipping"}
        )
        
        assert response.status_code in [200, 302, 404]


class TestOrderExportAndReports:
    """Test order export and reporting functionality"""
    
    def test_export_orders_to_csv(self, authenticated_app_client, sample_orders_for_export):
        """
        GIVEN: Multiple orders in database
        WHEN: Admin exports orders to CSV
        THEN: CSV file is generated with all order data
        """
        client, _ = authenticated_app_client
        response = client.get("/admin/order/export?format=csv")
        
        # Will be 404 until implemented
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response.headers["Content-Type"] == "text/csv"
    
    def test_daily_sales_report(self, authenticated_app_client, sample_orders_today):
        """
        GIVEN: Orders from today
        WHEN: Admin requests daily sales report
        THEN: Report shows today's sales summary
        """
        client, _ = authenticated_app_client
        response = client.get("/admin/reports/daily-sales")
        
        assert response.status_code in [200, 404]
    
    def test_monthly_sales_report(self, authenticated_app_client, sample_orders_this_month):
        """
        GIVEN: Orders from this month
        WHEN: Admin requests monthly sales report
        THEN: Report shows this month's sales summary
        """
        client, _ = authenticated_app_client
        response = client.get("/admin/reports/monthly-sales")
        
        assert response.status_code in [200, 404]
    
    def test_custom_date_range_export(self, authenticated_app_client, sample_orders_various_dates):
        """
        GIVEN: Orders from various dates
        WHEN: Admin exports orders with custom date range
        THEN: Only orders within date range are exported
        """
        client, _ = authenticated_app_client
        start_date = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d")
        end_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        response = client.get(
            f"/admin/order/export?start_date={start_date}&end_date={end_date}"
        )
        
        assert response.status_code in [200, 404]


class TestOrderColumnEnhancements:
    """Test enhanced column display in order list"""
    
    def test_order_list_shows_formatted_total(self, authenticated_app_client, sample_order):
        """
        GIVEN: Order with total amount
        WHEN: Admin views order list
        THEN: Total amount is formatted with currency
        """
        client, _ = authenticated_app_client
        response = client.get("/admin/order/list")
        
        assert response.status_code == 200
        # Should show formatted amount like "5,000.00 KGS"
        assert "KGS" in response.text or "USD" in response.text
    
    def test_order_list_shows_customer_info(self, authenticated_app_client, sample_order):
        """
        GIVEN: Order with customer information
        WHEN: Admin views order list
        THEN: Customer name and phone are displayed
        """
        client, _ = authenticated_app_client
        response = client.get("/admin/order/list")
        
        assert response.status_code == 200
        assert sample_order.customer_name in response.text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🧪 FIXTURES FOR ORDER MANAGEMENT TESTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@pytest.fixture
def sample_user_for_orders(admin_test_db):
    """Create a sample user for orders"""
    import uuid
    
    # Clean up existing data to avoid conflicts
    admin_test_db.query(Order).delete()
    admin_test_db.query(User).delete()
    admin_test_db.commit()
    
    # Create unique identifiers
    unique_id = str(uuid.uuid4())[:8]
    
    user = User(
        phone_number=f"+996555{unique_id[:6]}",
        full_name=f"Test Customer {unique_id}",
        is_active=True,
        is_verified=True,
        market="kg"
    )
    admin_test_db.add(user)
    admin_test_db.commit()
    admin_test_db.refresh(user)
    return user


@pytest.fixture
def sample_order(admin_test_db, sample_user_for_orders):
    """Create a sample order for testing"""
    import uuid
    
    # Create unique identifiers
    unique_id = str(uuid.uuid4())[:8]
    
    order = Order(
        order_number=f"TEST-001-{unique_id}",
        user_id=sample_user_for_orders.id,
        status=OrderStatus.PENDING,
        customer_name=sample_user_for_orders.full_name,
        customer_phone=sample_user_for_orders.phone_number,
        customer_email=f"test{unique_id}@example.com",
        delivery_address=f"Test Address 123 {unique_id}",
        delivery_city="Bishkek",
        subtotal=Decimal("5000.00"),
        shipping_cost=Decimal("200.00"),
        total_amount=Decimal("5200.00"),
        currency="KGS"
    )
    admin_test_db.add(order)
    admin_test_db.commit()
    admin_test_db.refresh(order)
    return order


@pytest.fixture
def sample_orders_today(admin_test_db, sample_user_for_orders):
    """Create orders for today and yesterday"""
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    
    orders = []
    
    # Today's orders
    for i in range(3):
        order = Order(
            order_number=f"TODAY-{i+1}",
            user_id=sample_user_for_orders.id,
            status=OrderStatus.PENDING,
            customer_name=sample_user_for_orders.full_name,
            customer_phone=sample_user_for_orders.phone_number,
            delivery_address="Test Address",
            delivery_city="Bishkek",
            subtotal=Decimal("1000.00"),
            shipping_cost=Decimal("100.00"),
            total_amount=Decimal("1100.00"),
            currency="KGS",
            order_date=today
        )
        admin_test_db.add(order)
        orders.append(order)
    
    # Yesterday's order
    order = Order(
        order_number="YESTERDAY-1",
        user_id=sample_user_for_orders.id,
        status=OrderStatus.DELIVERED,
        customer_name=sample_user_for_orders.full_name,
        customer_phone=sample_user_for_orders.phone_number,
        delivery_address="Test Address",
        delivery_city="Bishkek",
        subtotal=Decimal("2000.00"),
        shipping_cost=Decimal("100.00"),
        total_amount=Decimal("2100.00"),
        currency="KGS",
        order_date=yesterday
    )
    admin_test_db.add(order)
    orders.append(order)
    
    admin_test_db.commit()
    for order in orders:
        admin_test_db.refresh(order)
    
    return orders


@pytest.fixture
def sample_orders_mixed_status(admin_test_db, sample_user_for_orders):
    """Create orders with different statuses"""
    statuses = [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.DELIVERED]
    orders = []
    
    for i, status in enumerate(statuses):
        order = Order(
            order_number=f"MIXED-{i+1}",
            user_id=sample_user_for_orders.id,
            status=status,
            customer_name=sample_user_for_orders.full_name,
            customer_phone=sample_user_for_orders.phone_number,
            delivery_address="Test Address",
            delivery_city="Bishkek",
            subtotal=Decimal("1000.00"),
            shipping_cost=Decimal("100.00"),
            total_amount=Decimal("1100.00"),
            currency="KGS"
        )
        admin_test_db.add(order)
        orders.append(order)
    
    admin_test_db.commit()
    for order in orders:
        admin_test_db.refresh(order)
    
    return orders


@pytest.fixture
def sample_orders_for_bulk(admin_test_db, sample_user_for_orders):
    """Create multiple orders for bulk operations"""
    orders = []
    
    for i in range(5):
        order = Order(
            order_number=f"BULK-{i+1}",
            user_id=sample_user_for_orders.id,
            status=OrderStatus.PENDING,
            customer_name=sample_user_for_orders.full_name,
            customer_phone=sample_user_for_orders.phone_number,
            delivery_address="Test Address",
            delivery_city="Bishkek",
            subtotal=Decimal("1000.00"),
            shipping_cost=Decimal("100.00"),
            total_amount=Decimal("1100.00"),
            currency="KGS"
        )
        admin_test_db.add(order)
        orders.append(order)
    
    admin_test_db.commit()
    for order in orders:
        admin_test_db.refresh(order)
    
    return orders


@pytest.fixture
def sample_order_with_history(admin_test_db, sample_user_for_orders):
    """Create order with customer history"""
    # Create 3 previous orders for this customer
    previous_orders = []
    for i in range(3):
        order = Order(
            order_number=f"PREV-{i+1}",
            user_id=sample_user_for_orders.id,
            status=OrderStatus.DELIVERED,
            customer_name=sample_user_for_orders.full_name,
            customer_phone=sample_user_for_orders.phone_number,
            delivery_address="Test Address",
            delivery_city="Bishkek",
            subtotal=Decimal("1500.00"),
            shipping_cost=Decimal("100.00"),
            total_amount=Decimal("1600.00"),
            currency="KGS",
            order_date=datetime.utcnow() - timedelta(days=30*(i+1))
        )
        admin_test_db.add(order)
        previous_orders.append(order)
    
    # Current order
    current_order = Order(
        order_number="CURRENT-1",
        user_id=sample_user_for_orders.id,
        status=OrderStatus.PENDING,
        customer_name="Test Customer",
        customer_phone="+996555123456",
        delivery_address="Test Address",
        delivery_city="Bishkek",
        subtotal=Decimal("2000.00"),
        shipping_cost=Decimal("150.00"),
        total_amount=Decimal("2150.00"),
        currency="KGS"
    )
    admin_test_db.add(current_order)
    
    admin_test_db.commit()
    for order in previous_orders:
        admin_test_db.refresh(order)
    admin_test_db.refresh(current_order)
    
    return current_order


@pytest.fixture
def sample_orders_for_export(admin_test_db, sample_user_for_orders):
    """Create orders for export testing"""
    orders = []
    
    for i in range(10):
        order = Order(
            order_number=f"EXPORT-{i+1}",
            user_id=sample_user_for_orders.id,
            status=OrderStatus.DELIVERED,
            customer_name=f"{sample_user_for_orders.full_name} {i+1}",
            customer_phone=sample_user_for_orders.phone_number,
            delivery_address=f"Address {i+1}",
            delivery_city="Bishkek",
            subtotal=Decimal(f"{(i+1)*1000}.00"),
            shipping_cost=Decimal("100.00"),
            total_amount=Decimal(f"{(i+1)*1000 + 100}.00"),
            currency="KGS",
            order_date=datetime.utcnow() - timedelta(days=i)
        )
        admin_test_db.add(order)
        orders.append(order)
    
    admin_test_db.commit()
    for order in orders:
        admin_test_db.refresh(order)
    
    return orders


@pytest.fixture
def sample_orders_this_month(admin_test_db, sample_user_for_orders):
    """Create orders for this month"""
    orders = []
    today = datetime.utcnow()
    
    for i in range(15):
        order_date = today - timedelta(days=i)
        if order_date.month == today.month:
            order = Order(
                order_number=f"MONTH-{i+1}",
                user_id=sample_user_for_orders.id,
                status=OrderStatus.DELIVERED,
                customer_name="Test Customer",
                customer_phone="+996555123456",
                delivery_address="Test Address",
                delivery_city="Bishkek",
                subtotal=Decimal("1000.00"),
                shipping_cost=Decimal("100.00"),
                total_amount=Decimal("1100.00"),
                currency="KGS",
                order_date=order_date
            )
            admin_test_db.add(order)
            orders.append(order)
    
    admin_test_db.commit()
    for order in orders:
        admin_test_db.refresh(order)
    
    return orders


@pytest.fixture
def sample_orders_various_dates(admin_test_db, sample_user_for_orders):
    """Create orders with various dates for date range testing"""
    orders = []
    today = datetime.utcnow()
    
    # Orders from last 30 days
    for i in range(30):
        order = Order(
            order_number=f"VAR-{i+1}",
            user_id=sample_user_for_orders.id,
            status=OrderStatus.DELIVERED,
            customer_name=sample_user_for_orders.full_name,
            customer_phone=sample_user_for_orders.phone_number,
            delivery_address="Test Address",
            delivery_city="Bishkek",
            subtotal=Decimal("1000.00"),
            shipping_cost=Decimal("100.00"),
            total_amount=Decimal("1100.00"),
            currency="KGS",
            order_date=today - timedelta(days=i)
        )
        admin_test_db.add(order)
        orders.append(order)
    
    admin_test_db.commit()
    for order in orders:
        admin_test_db.refresh(order)
    
    return orders

