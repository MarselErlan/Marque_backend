"""
Unit Tests for Order Router
Tests order creation, validation, and business logic
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.app_01.routers.order_router import (
    generate_order_number,
    calculate_shipping_cost,
    validate_and_get_sku,
    CreateOrderRequest,
    OrderItemCreate
)
from src.app_01.models.orders.order import Order, OrderStatus
from src.app_01.models.products.sku import SKU
from src.app_01.models.products.product import Product


class TestOrderNumberGeneration:
    """Test order number generation logic"""
    
    def test_generate_first_order_number(self, db_session: Session):
        """Test generating first order number when no orders exist"""
        # Arrange: Empty database
        db_session.query(Order).delete()
        db_session.commit()
        
        # Act
        order_number = generate_order_number(db_session)
        
        # Assert
        assert order_number == "#1001"
    
    def test_generate_sequential_order_number(self, db_session: Session):
        """Test generating sequential order numbers"""
        # Arrange: Create existing order
        db_session.query(Order).delete()
        db_session.commit()
        
        existing_order = Order(
            order_number="#1005",
            user_id=1,
            status=OrderStatus.PENDING,
            customer_name="Test",
            customer_phone="+996505231255",
            delivery_address="Test Address",
            subtotal=100.0,
            shipping_cost=0.0,
            total_amount=100.0
        )
        db_session.add(existing_order)
        db_session.commit()
        
        # Act
        order_number = generate_order_number(db_session)
        
        # Assert
        assert order_number == "#1006"
    
    def test_handle_invalid_order_number_format(self, db_session: Session):
        """Test handling orders with invalid number format"""
        # Arrange: Create order with invalid format
        db_session.query(Order).delete()
        db_session.commit()
        
        existing_order = Order(
            order_number="INVALID",
            user_id=1,
            status=OrderStatus.PENDING,
            customer_name="Test",
            customer_phone="+996505231255",
            delivery_address="Test Address",
            subtotal=100.0,
            shipping_cost=0.0,
            total_amount=100.0
        )
        db_session.add(existing_order)
        db_session.commit()
        
        # Act
        order_number = generate_order_number(db_session)
        
        # Assert: Should default to #1001
        assert order_number == "#1001"


class TestShippingCalculation:
    """Test shipping cost calculation logic"""
    
    def test_free_shipping_for_large_orders(self):
        """Test free shipping for orders >= 5000 KGS"""
        # Arrange
        subtotal = 5000.0
        
        # Act
        shipping_cost = calculate_shipping_cost(subtotal)
        
        # Assert
        assert shipping_cost == 0.0
    
    def test_free_shipping_for_orders_above_threshold(self):
        """Test free shipping for orders > 5000 KGS"""
        # Arrange
        subtotal = 7500.0
        
        # Act
        shipping_cost = calculate_shipping_cost(subtotal)
        
        # Assert
        assert shipping_cost == 0.0
    
    def test_standard_shipping_for_small_orders(self):
        """Test standard shipping for orders < 5000 KGS"""
        # Arrange
        subtotal = 1000.0
        
        # Act
        shipping_cost = calculate_shipping_cost(subtotal)
        
        # Assert
        assert shipping_cost == 150.0
    
    def test_standard_shipping_just_below_threshold(self):
        """Test standard shipping for orders just below threshold"""
        # Arrange
        subtotal = 4999.0
        
        # Act
        shipping_cost = calculate_shipping_cost(subtotal)
        
        # Assert
        assert shipping_cost == 150.0


class TestSKUValidation:
    """Test SKU validation logic"""
    
    def test_validate_existing_sku_with_stock(self, db_session: Session, sample_product_with_skus):
        """Test validating existing SKU with stock"""
        # Arrange
        product, skus = sample_product_with_skus
        sku = skus[0]
        sku.stock = 10
        sku.is_active = True
        db_session.commit()
        
        # Act
        validated_sku = validate_and_get_sku(sku.id, db_session)
        
        # Assert
        assert validated_sku is not None
        assert validated_sku.id == sku.id
        assert validated_sku.stock > 0
    
    def test_validate_nonexistent_sku(self, db_session: Session):
        """Test validating non-existent SKU raises 404"""
        # Arrange
        nonexistent_id = 99999
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_get_sku(nonexistent_id, db_session)
        
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail).lower()
    
    def test_validate_out_of_stock_sku(self, db_session: Session, sample_product_with_skus):
        """Test validating SKU with no stock raises 400"""
        # Arrange
        product, skus = sample_product_with_skus
        sku = skus[0]
        sku.stock = 0
        sku.is_active = True
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_get_sku(sku.id, db_session)
        
        assert exc_info.value.status_code == 400
        assert "out of stock" in str(exc_info.value.detail).lower()
    
    def test_validate_inactive_sku(self, db_session: Session, sample_product_with_skus):
        """Test validating inactive SKU raises 404"""
        # Arrange
        product, skus = sample_product_with_skus
        sku = skus[0]
        sku.is_active = False
        db_session.commit()
        
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            validate_and_get_sku(sku.id, db_session)
        
        assert exc_info.value.status_code == 404


class TestOrderRequestValidation:
    """Test order request validation"""
    
    def test_valid_order_request(self):
        """Test creating valid order request"""
        # Arrange & Act
        request = CreateOrderRequest(
            customer_name="John Doe",
            customer_phone="+996505231255",
            delivery_address="Юнусалиева, 40",
            payment_method="card",
            use_cart=True
        )
        
        # Assert
        assert request.customer_name == "John Doe"
        assert request.payment_method == "card"
        assert request.use_cart is True
    
    def test_invalid_phone_number(self):
        """Test validation fails for invalid phone"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError) as exc_info:
            CreateOrderRequest(
                customer_name="John Doe",
                customer_phone="123",  # Too short
                delivery_address="Юнусалиева, 40",
                payment_method="card"
            )
        
        assert "Invalid phone" in str(exc_info.value)
    
    def test_invalid_address(self):
        """Test validation fails for short address"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError) as exc_info:
            CreateOrderRequest(
                customer_name="John Doe",
                customer_phone="+996505231255",
                delivery_address="123",  # Too short
                payment_method="card"
            )
        
        assert "too short" in str(exc_info.value).lower()
    
    def test_order_item_validation(self):
        """Test order item validation"""
        # Valid item
        item = OrderItemCreate(sku_id=1, quantity=2)
        assert item.quantity == 2
        
        # Invalid quantity (too low)
        with pytest.raises(ValueError):
            OrderItemCreate(sku_id=1, quantity=0)
        
        # Invalid quantity (too high)
        with pytest.raises(ValueError):
            OrderItemCreate(sku_id=1, quantity=101)


class TestOrderBusinessLogic:
    """Test order business logic"""
    
    def test_calculate_order_totals(self):
        """Test calculating order totals"""
        # Arrange
        subtotal = 2999.0
        shipping_cost = calculate_shipping_cost(subtotal)
        
        # Act
        total = subtotal + shipping_cost
        
        # Assert
        assert shipping_cost == 150.0  # < 5000
        assert total == 3149.0
    
    def test_calculate_order_totals_with_free_shipping(self):
        """Test calculating order totals with free shipping"""
        # Arrange
        subtotal = 5500.0
        shipping_cost = calculate_shipping_cost(subtotal)
        
        # Act
        total = subtotal + shipping_cost
        
        # Assert
        assert shipping_cost == 0.0  # >= 5000
        assert total == 5500.0


# Integration fixtures
@pytest.fixture
def sample_product_with_skus(db_session: Session):
    """Create a sample product with SKUs for testing"""
    from src.app_01.models.products.brand import Brand
    from src.app_01.models.products.category import Category, Subcategory
    
    # Clean up
    db_session.query(SKU).delete()
    db_session.query(Product).delete()
    db_session.query(Subcategory).delete()
    db_session.query(Category).delete()
    db_session.query(Brand).delete()
    db_session.commit()
    
    # Create brand
    brand = Brand(name="Test Brand", slug="test-brand")
    db_session.add(brand)
    db_session.commit()
    
    # Create category
    category = Category(name="Test Category", slug="test-category", sort_order=1)
    db_session.add(category)
    db_session.commit()
    
    # Create subcategory
    subcategory = Subcategory(
        name="Test Subcategory",
        slug="test-subcategory",
        category_id=category.id,
        sort_order=1
    )
    db_session.add(subcategory)
    db_session.commit()
    
    # Create product
    product = Product(
        title="Test Product",
        slug="test-product",
        sku_code="TEST-SKU",
        description="Test description",
        brand_id=brand.id,
        category_id=category.id,
        subcategory_id=subcategory.id,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Create SKUs
    skus = [
        SKU(
            product_id=product.id,
            sku_code="TEST-M-BLACK",
            size="M",
            color="Black",
            price=2999.0,
            stock=10,
            is_active=True
        ),
        SKU(
            product_id=product.id,
            sku_code="TEST-L-BLACK",
            size="L",
            color="Black",
            price=2999.0,
            stock=5,
            is_active=True
        )
    ]
    for sku in skus:
        db_session.add(sku)
    db_session.commit()
    
    for sku in skus:
        db_session.refresh(sku)
    
    return product, skus

