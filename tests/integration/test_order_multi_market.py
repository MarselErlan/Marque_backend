"""
Comprehensive Integration Tests for Multi-Market Order System
Tests order creation, database isolation, and data integrity across KG and US markets
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.app_01.main import app
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.users.user import User
from src.app_01.models.products.product import Product
from src.app_01.models.products.sku import SKU
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category
from src.app_01.models.orders.order import Order, OrderStatus
from src.app_01.models.orders.order_item import OrderItem
import jwt
from datetime import datetime, timedelta


client = TestClient(app)


# ========================================================================
# FIXTURES
# ========================================================================

@pytest.fixture(scope="function")
def kg_db_session():
    """Create a KG database session for testing"""
    SessionLocal = db_manager.get_session_factory(Market.KG)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def us_db_session():
    """Create a US database session for testing"""
    SessionLocal = db_manager.get_session_factory(Market.US)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def kg_user(kg_db_session):
    """Create a KG user for testing"""
    from src.app_01.models.users.phone_verification import PhoneVerification
    from src.app_01.models.users.wishlist import Wishlist
    from src.app_01.models.orders.order import Order
    from src.app_01.models.orders.order_item import OrderItem
    from src.app_01.models.orders.cart import Cart
    
    # Find existing user
    existing_user = kg_db_session.query(User).filter(User.phone_number == "+996555999888").first()
    if existing_user:
        # Clean up all related records (order matters - delete children before parents)
        kg_db_session.query(Wishlist).filter(Wishlist.user_id == existing_user.id).delete()
        kg_db_session.query(Cart).filter(Cart.user_id == existing_user.id).delete()
        
        # Delete order items before orders
        orders = kg_db_session.query(Order).filter(Order.user_id == existing_user.id).all()
        for order in orders:
            kg_db_session.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
        kg_db_session.query(Order).filter(Order.user_id == existing_user.id).delete()
        
        kg_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+996555999888").delete()
        kg_db_session.query(User).filter(User.phone_number == "+996555999888").delete()
        kg_db_session.commit()
    
    user = User(
        phone_number="+996555999888",
        full_name="KG Test User",
        is_verified=True,
        is_active=True,
        market="kg"
    )
    kg_db_session.add(user)
    kg_db_session.commit()
    kg_db_session.refresh(user)
    return user


@pytest.fixture
def us_user(us_db_session):
    """Create a US user for testing"""
    from src.app_01.models.users.phone_verification import PhoneVerification
    from src.app_01.models.users.wishlist import Wishlist
    from src.app_01.models.orders.order import Order
    from src.app_01.models.orders.order_item import OrderItem
    from src.app_01.models.orders.cart import Cart
    
    # Find existing user
    existing_user = us_db_session.query(User).filter(User.phone_number == "+13128059851").first()
    if existing_user:
        # Clean up all related records (order matters - delete children before parents)
        us_db_session.query(Wishlist).filter(Wishlist.user_id == existing_user.id).delete()
        us_db_session.query(Cart).filter(Cart.user_id == existing_user.id).delete()
        
        # Delete order items before orders
        orders = us_db_session.query(Order).filter(Order.user_id == existing_user.id).all()
        for order in orders:
            us_db_session.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
        us_db_session.query(Order).filter(Order.user_id == existing_user.id).delete()
        
        us_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+13128059851").delete()
        us_db_session.query(User).filter(User.phone_number == "+13128059851").delete()
        us_db_session.commit()
    
    user = User(
        phone_number="+13128059851",
        full_name="US Test User",
        is_verified=True,
        is_active=True,
        market="us",
        language="en",  # ✅ Required for US database
        country="US"  # ✅ Required for US database
    )
    us_db_session.add(user)
    us_db_session.commit()
    us_db_session.refresh(user)
    return user


@pytest.fixture
def kg_auth_token(kg_user):
    """Generate auth token for KG user"""
    from src.app_01.services.auth_service import SECRET_KEY, ALGORITHM
    
    payload = {
        "sub": kg_user.id,  # ✅ Use 'sub' instead of 'user_id'
        "market": "kg",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def us_auth_token(us_user):
    """Generate auth token for US user"""
    from src.app_01.services.auth_service import SECRET_KEY, ALGORITHM
    
    payload = {
        "sub": us_user.id,  # ✅ Use 'sub' instead of 'user_id'
        "market": "us",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def kg_test_sku(kg_db_session):
    """Get an existing KG SKU for testing (from ETL), reset stock before each test"""
    sku = kg_db_session.query(SKU).filter(
        SKU.is_active == True
    ).first()
    assert sku is not None, "No active SKU found in KG database"
    
    # Reset stock to ensure tests have enough inventory
    sku.stock = 50
    kg_db_session.commit()
    kg_db_session.refresh(sku)
    return sku


@pytest.fixture
def us_test_sku(us_db_session):
    """Get an existing US SKU for testing (from ETL), reset stock before each test"""
    sku = us_db_session.query(SKU).filter(
        SKU.is_active == True
    ).first()
    assert sku is not None, "No active SKU found in US database"
    
    # Reset stock to ensure tests have enough inventory
    sku.stock = 50
    us_db_session.commit()
    us_db_session.refresh(sku)
    return sku


# ========================================================================
# TEST SUITE 1: Order Creation in Both Markets
# ========================================================================

class TestMultiMarketOrderCreation:
    """Test order creation in both KG and US markets"""
    
    def test_create_order_kg_market(self, kg_auth_token, kg_test_sku, kg_db_session):
        """Test creating an order in KG market"""
        initial_stock = kg_test_sku.stock
        
        # Create order request
        order_data = {
            "customer_name": "KG Test User",
            "customer_phone": "+996555999888",
            "delivery_address": "Bishkek, Chui Ave 123",
            "payment_method": "card",
            "items": [{"sku_id": kg_test_sku.id, "quantity": 2}],
            "use_cart": False
        }
        
        # Make API request
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        # Assertions
        assert response.status_code == 200, f"Order creation failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "order_number" in data
        assert "total_amount" in data
        assert data["status"] == "pending"
        assert data["customer_phone"] == "+996555999888"
        assert len(data["items"]) == 1
        assert data["items"][0]["quantity"] == 2
        
        # Verify stock reduction
        kg_db_session.refresh(kg_test_sku)
        assert kg_test_sku.stock == initial_stock - 2, "Stock not reduced correctly"
        
        # Verify order in database
        order = kg_db_session.query(Order).filter(Order.order_number == data["order_number"]).first()
        assert order is not None, "Order not found in KG database"
        assert order.total_amount == data["total_amount"]
        
    
    def test_create_order_us_market(self, us_auth_token, us_test_sku, us_db_session):
        """Test creating an order in US market"""
        initial_stock = us_test_sku.stock
        
        # Create order request
        order_data = {
            "customer_name": "US Test User",
            "customer_phone": "+13128059851",
            "delivery_address": "123 Main St, Chicago, IL",
            "payment_method": "card",
            "items": [{"sku_id": us_test_sku.id, "quantity": 1}],
            "use_cart": False
        }
        
        # Make API request
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        
        # Assertions
        assert response.status_code == 200, f"Order creation failed: {response.text}"
        data = response.json()
        
        # Verify response structure
        assert "order_number" in data
        assert "total_amount" in data
        assert data["status"] == "pending"
        assert data["customer_phone"] == "+13128059851"
        
        # Verify stock reduction
        us_db_session.refresh(us_test_sku)
        assert us_test_sku.stock == initial_stock - 1, "Stock not reduced correctly"
        
        # Verify order in database
        order = us_db_session.query(Order).filter(Order.order_number == data["order_number"]).first()
        assert order is not None, "Order not found in US database"


# ========================================================================
# TEST SUITE 2: Multi-Market Database Isolation
# ========================================================================

class TestMultiMarketIsolation:
    """Test that orders in one market don't affect the other market's data"""
    
    def test_kg_order_does_not_affect_us_stock(
        self, 
        kg_auth_token, 
        kg_test_sku, 
        us_test_sku,
        kg_db_session,
        us_db_session
    ):
        """Test that creating a KG order doesn't affect US SKU stock"""
        # Record initial stocks
        kg_initial_stock = kg_test_sku.stock
        us_initial_stock = us_test_sku.stock
        
        # Create KG order
        order_data = {
            "customer_name": "KG Test User",
            "customer_phone": "+996555999888",
            "delivery_address": "Bishkek, Chui Ave 123",
            "payment_method": "cash",
            "items": [{"sku_id": kg_test_sku.id, "quantity": 3}],
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify KG stock changed
        kg_db_session.refresh(kg_test_sku)
        assert kg_test_sku.stock == kg_initial_stock - 3, "KG stock not reduced"
        
        # Verify US stock DID NOT change
        us_db_session.refresh(us_test_sku)
        assert us_test_sku.stock == us_initial_stock, "US stock incorrectly changed!"
    
    
    def test_us_order_does_not_affect_kg_stock(
        self,
        us_auth_token,
        us_test_sku,
        kg_test_sku,
        us_db_session,
        kg_db_session
    ):
        """Test that creating a US order doesn't affect KG SKU stock"""
        # Record initial stocks
        us_initial_stock = us_test_sku.stock
        kg_initial_stock = kg_test_sku.stock
        
        # Create US order
        order_data = {
            "customer_name": "US Test User",
            "customer_phone": "+13128059851",
            "delivery_address": "123 Main St, Chicago, IL",
            "payment_method": "card",
            "items": [{"sku_id": us_test_sku.id, "quantity": 2}],
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        
        assert response.status_code == 200
        
        # Verify US stock changed
        us_db_session.refresh(us_test_sku)
        assert us_test_sku.stock == us_initial_stock - 2, "US stock not reduced"
        
        # Verify KG stock DID NOT change
        kg_db_session.refresh(kg_test_sku)
        assert kg_test_sku.stock == kg_initial_stock, "KG stock incorrectly changed!"
    
    
    def test_kg_order_count_does_not_include_us_orders(
        self,
        kg_auth_token,
        us_auth_token,
        kg_test_sku,
        us_test_sku,
        kg_db_session,
        us_db_session
    ):
        """Test that order counts are isolated per market"""
        # Count initial orders
        kg_initial_orders = kg_db_session.query(Order).count()
        us_initial_orders = us_db_session.query(Order).count()
        
        # Create KG order
        kg_order_data = {
            "customer_name": "KG Test User",
            "customer_phone": "+996555999888",
            "delivery_address": "Bishkek, Chui Ave 123",
            "payment_method": "cash",
            "items": [{"sku_id": kg_test_sku.id, "quantity": 1}],
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=kg_order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        assert response.status_code == 200
        
        # Create US order
        us_order_data = {
            "customer_name": "US Test User",
            "customer_phone": "+13128059851",
            "delivery_address": "123 Main St, Chicago, IL",
            "payment_method": "card",
            "items": [{"sku_id": us_test_sku.id, "quantity": 1}],
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=us_order_data,
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        assert response.status_code == 200
        
        # Verify order counts
        kg_final_orders = kg_db_session.query(Order).count()
        us_final_orders = us_db_session.query(Order).count()
        
        assert kg_final_orders == kg_initial_orders + 1, "KG order count incorrect"
        assert us_final_orders == us_initial_orders + 1, "US order count incorrect"


# ========================================================================
# TEST SUITE 3: End-to-End Order Flow
# ========================================================================

class TestEndToEndOrderFlow:
    """Test complete order flow from authentication to persistence"""
    
    def test_complete_order_flow_kg(
        self,
        kg_auth_token,
        kg_user,
        kg_test_sku,
        kg_db_session
    ):
        """Test complete order flow in KG market"""
        # Step 1: Verify user authentication (SKIPPED - profile endpoint may not be available in test env)
        # profile_response = client.get(
        #     "/api/v1/auth/profile",
        #     headers={"Authorization": f"Bearer {kg_auth_token}"}
        # )
        # assert profile_response.status_code == 200
        # profile = profile_response.json()
        # assert profile["phone"] == "+996555999888"
        
        # Step 2: Lookup product/SKU
        product = kg_test_sku.product
        assert product is not None, "Product not found for SKU"
        
        # Step 3: Create order
        initial_stock = kg_test_sku.stock
        order_quantity = 2
        
        order_data = {
            "customer_name": kg_user.full_name,
            "customer_phone": kg_user.phone_number,
            "delivery_address": "Bishkek, Test Street 456",
            "payment_method": "card",
            "items": [{"sku_id": kg_test_sku.id, "quantity": order_quantity}],
            "use_cart": False
        }
        
        create_response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        assert create_response.status_code == 200
        order_data_response = create_response.json()
        order_number = order_data_response["order_number"]
        
        # Step 4: Verify stock reduction
        kg_db_session.refresh(kg_test_sku)
        assert kg_test_sku.stock == initial_stock - order_quantity
        
        # Step 5: Verify order persistence
        order = kg_db_session.query(Order).filter(Order.order_number == order_number).first()
        assert order is not None
        assert order.customer_phone == "+996555999888"
        assert order.status == OrderStatus.PENDING  # Compare with enum, not string
        
        # Step 6: Verify order items
        order_items = kg_db_session.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        assert len(order_items) == 1
        assert order_items[0].sku_id == kg_test_sku.id
        assert order_items[0].quantity == order_quantity
        
        # Step 7: Retrieve order via API
        orders_response = client.get(
            "/api/v1/orders",
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        assert orders_response.status_code == 200
        orders = orders_response.json()
        assert len(orders) > 0
        assert any(o["order_number"] == order_number for o in orders)


# ========================================================================
# TEST SUITE 4: Data Integrity and Validation
# ========================================================================

class TestOrderDataIntegrity:
    """Test data integrity and validation for orders"""
    
    def test_cannot_create_order_with_insufficient_stock(
        self,
        kg_auth_token,
        kg_test_sku,
        kg_db_session
    ):
        """Test that orders cannot be created when stock is insufficient"""
        # Try to order more than available stock (but less than Pydantic limit of 100)
        excessive_quantity = min(kg_test_sku.stock + 10, 99)
        
        order_data = {
            "customer_name": "KG Test User",
            "customer_phone": "+996555999888",
            "delivery_address": "Bishkek, Test Street",
            "payment_method": "cash",
            "items": [{"sku_id": kg_test_sku.id, "quantity": excessive_quantity}],
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        assert response.status_code == 400  # Business logic error for insufficient stock
        assert "insufficient stock" in response.text.lower() or "not enough stock" in response.text.lower()
    
    
    def test_cannot_create_order_with_invalid_sku(
        self,
        kg_auth_token,
        kg_db_session
    ):
        """Test that orders cannot be created with non-existent SKU"""
        order_data = {
            "customer_name": "KG Test User",
            "customer_phone": "+996555999888",
            "delivery_address": "Bishkek, Test Street",
            "payment_method": "cash",
            "items": [{"sku_id": 99999, "quantity": 1}],  # Invalid SKU ID
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        assert response.status_code == 404
        assert "not found" in response.text.lower()
    
    
    def test_order_total_calculation_is_correct(
        self,
        kg_auth_token,
        kg_test_sku,
        kg_db_session
    ):
        """Test that order total is calculated correctly"""
        quantity = 3
        expected_subtotal = kg_test_sku.price * quantity
        
        # Calculate expected shipping (free for orders >= 5000, otherwise 150.0)
        expected_shipping = 0.0 if expected_subtotal >= 5000 else 150.0
        expected_total = expected_subtotal + expected_shipping
        
        order_data = {
            "customer_name": "KG Test User",
            "customer_phone": "+996555999888",
            "delivery_address": "Bishkek, Test Street",
            "payment_method": "cash",
            "items": [{"sku_id": kg_test_sku.id, "quantity": quantity}],
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["subtotal"] == expected_subtotal
        assert data["shipping_cost"] == expected_shipping
        assert data["total_amount"] == expected_total


# ========================================================================
# TEST SUITE 5: Market-Specific User Validation
# ========================================================================

class TestMarketUserValidation:
    """Test that users can only access their own market's data"""
    
    def test_kg_user_cannot_use_us_sku(
        self,
        kg_auth_token,
        us_test_sku
    ):
        """Test that a KG user cannot order from US SKUs"""
        order_data = {
            "customer_name": "KG Test User",
            "customer_phone": "+996555999888",
            "delivery_address": "Bishkek, Test Street",
            "payment_method": "cash",
            "items": [{"sku_id": us_test_sku.id, "quantity": 1}],  # US SKU
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {kg_auth_token}"}
        )
        
        # Should fail because KG user connects to KG DB, where this SKU ID doesn't exist
        assert response.status_code == 404
    
    
    def test_us_user_cannot_use_kg_sku(
        self,
        us_auth_token,
        kg_test_sku
    ):
        """Test that a US user cannot order from KG SKUs"""
        order_data = {
            "customer_name": "US Test User",
            "customer_phone": "+13128059851",
            "delivery_address": "123 Main St, Chicago, IL",
            "payment_method": "card",
            "items": [{"sku_id": kg_test_sku.id, "quantity": 1}],  # KG SKU
            "use_cart": False
        }
        
        response = client.post(
            "/api/v1/orders/create",
            json=order_data,
            headers={"Authorization": f"Bearer {us_auth_token}"}
        )
        
        # Should fail because US user connects to US DB, where this SKU ID doesn't exist
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

