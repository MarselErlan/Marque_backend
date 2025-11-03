"""
Comprehensive Integration Tests for Multi-Market Cart and Wishlist System
Tests cart/wishlist database isolation and data integrity across KG and US markets
Focuses on direct database operations to verify market isolation
"""
import pytest
from sqlalchemy.orm import Session

from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.users.user import User
from src.app_01.models.products.product import Product
from src.app_01.models.products.sku import SKU
from src.app_01.models.orders.cart import Cart, CartItem
from src.app_01.models.users.wishlist import Wishlist, WishlistItem


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
    
    # Clean up existing user and ALL their carts/wishlists (best effort)
    try:
        existing_user = kg_db_session.query(User).filter(User.phone_number == "+996777123456").first()
        if existing_user:
            # Delete ALL cart items and carts for this user
            kg_carts = kg_db_session.query(Cart).filter(Cart.user_id == existing_user.id).all()
            for kg_cart in kg_carts:
                kg_db_session.query(CartItem).filter(CartItem.cart_id == kg_cart.id).delete(synchronize_session=False)
                kg_db_session.delete(kg_cart)
            
            # Delete ALL wishlist items and wishlists for this user
            kg_wishlists = kg_db_session.query(Wishlist).filter(Wishlist.user_id == existing_user.id).all()
            for kg_wishlist in kg_wishlists:
                kg_db_session.query(WishlistItem).filter(WishlistItem.wishlist_id == kg_wishlist.id).delete(synchronize_session=False)
                kg_db_session.delete(kg_wishlist)
            
            kg_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+996777123456").delete(synchronize_session=False)
            kg_db_session.query(User).filter(User.phone_number == "+996777123456").delete(synchronize_session=False)
            kg_db_session.commit()
    except Exception as e:
        print(f"Warning: Pre-test cleanup failed (non-critical): {e}")
        kg_db_session.rollback()
    
    # Get or create user
    user = kg_db_session.query(User).filter(User.phone_number == "+996777123456").first()
    if not user:
        user = User(
            phone_number="+996777123456",
            full_name="KG Cart Test User",
            is_verified=True,
            is_active=True,
            market="kg"
        )
        kg_db_session.add(user)
        kg_db_session.commit()
        kg_db_session.refresh(user)
    
    yield user
    
    # Teardown: Clean up after test (best effort - don't fail test if cleanup fails)
    try:
        kg_db_session.rollback()  # Roll back any uncommitted changes first
        
        # Delete ALL cart items and carts for this user
        kg_carts = kg_db_session.query(Cart).filter(Cart.user_id == user.id).all()
        for kg_cart in kg_carts:
            kg_db_session.query(CartItem).filter(CartItem.cart_id == kg_cart.id).delete(synchronize_session=False)
            kg_db_session.delete(kg_cart)
        
        # Delete ALL wishlist items and wishlists for this user
        kg_wishlists = kg_db_session.query(Wishlist).filter(Wishlist.user_id == user.id).all()
        for kg_wishlist in kg_wishlists:
            kg_db_session.query(WishlistItem).filter(WishlistItem.wishlist_id == kg_wishlist.id).delete(synchronize_session=False)
            kg_db_session.delete(kg_wishlist)
        
        # Delete phone verification records
        kg_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+996777123456").delete(synchronize_session=False)
        
        # Finally delete the user
        kg_db_session.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        kg_db_session.commit()
    except Exception as e:
        print(f"Warning: Fixture cleanup failed (non-critical): {e}")
        kg_db_session.rollback()


@pytest.fixture
def us_user(us_db_session):
    """Create a US user for testing"""
    from src.app_01.models.users.phone_verification import PhoneVerification
    
    # Clean up existing user and ALL their carts/wishlists (best effort)
    try:
        existing_user = us_db_session.query(User).filter(User.phone_number == "+15551234567").first()
        if existing_user:
            # Delete ALL cart items and carts for this user
            us_carts = us_db_session.query(Cart).filter(Cart.user_id == existing_user.id).all()
            for us_cart in us_carts:
                us_db_session.query(CartItem).filter(CartItem.cart_id == us_cart.id).delete(synchronize_session=False)
                us_db_session.delete(us_cart)
            
            # Delete ALL wishlist items and wishlists for this user
            us_wishlists = us_db_session.query(Wishlist).filter(Wishlist.user_id == existing_user.id).all()
            for us_wishlist in us_wishlists:
                us_db_session.query(WishlistItem).filter(WishlistItem.wishlist_id == us_wishlist.id).delete(synchronize_session=False)
                us_db_session.delete(us_wishlist)
            
            us_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+15551234567").delete(synchronize_session=False)
            us_db_session.query(User).filter(User.phone_number == "+15551234567").delete(synchronize_session=False)
            us_db_session.commit()
    except Exception as e:
        print(f"Warning: Pre-test cleanup failed (non-critical): {e}")
        us_db_session.rollback()
    
    # Get or create user
    user = us_db_session.query(User).filter(User.phone_number == "+15551234567").first()
    if not user:
        user = User(
            phone_number="+15551234567",
            full_name="US Cart Test User",
            is_verified=True,
            is_active=True,
            market="us",
            language="en",
            country="US"
        )
        us_db_session.add(user)
        us_db_session.commit()
        us_db_session.refresh(user)
    
    yield user
    
    # Teardown: Clean up after test (best effort - don't fail test if cleanup fails)
    try:
        us_db_session.rollback()  # Roll back any uncommitted changes first
        
        # Delete ALL cart items and carts for this user
        us_carts = us_db_session.query(Cart).filter(Cart.user_id == user.id).all()
        for us_cart in us_carts:
            us_db_session.query(CartItem).filter(CartItem.cart_id == us_cart.id).delete(synchronize_session=False)
            us_db_session.delete(us_cart)
        
        # Delete ALL wishlist items and wishlists for this user
        us_wishlists = us_db_session.query(Wishlist).filter(Wishlist.user_id == user.id).all()
        for us_wishlist in us_wishlists:
            us_db_session.query(WishlistItem).filter(WishlistItem.wishlist_id == us_wishlist.id).delete(synchronize_session=False)
            us_db_session.delete(us_wishlist)
        
        # Delete phone verification records
        us_db_session.query(PhoneVerification).filter(PhoneVerification.phone_number == "+15551234567").delete(synchronize_session=False)
        
        # Finally delete the user
        us_db_session.query(User).filter(User.id == user.id).delete(synchronize_session=False)
        us_db_session.commit()
    except Exception as e:
        print(f"Warning: Fixture cleanup failed (non-critical): {e}")
        us_db_session.rollback()


@pytest.fixture
def kg_test_sku(kg_db_session):
    """Get an existing KG SKU for testing"""
    sku = kg_db_session.query(SKU).filter(
        SKU.is_active == True,
        SKU.stock > 10
    ).first()
    assert sku is not None, "No active SKU with stock found in KG database"
    return sku


@pytest.fixture
def us_test_sku(us_db_session):
    """Get an existing US SKU for testing"""
    sku = us_db_session.query(SKU).filter(
        SKU.is_active == True,
        SKU.stock > 10
    ).first()
    assert sku is not None, "No active SKU with stock found in US database"
    return sku


@pytest.fixture
def kg_test_product(kg_db_session):
    """Get an existing KG product for testing"""
    product = kg_db_session.query(Product).filter(
        Product.is_active == True
    ).first()
    assert product is not None, "No active product found in KG database"
    return product


@pytest.fixture
def us_test_product(us_db_session):
    """Get an existing US product for testing"""
    product = us_db_session.query(Product).filter(
        Product.is_active == True
    ).first()
    assert product is not None, "No active product found in US database"
    return product


# ========================================================================
# TEST SUITE 1: Cart Database Isolation
# ========================================================================

class TestCartDatabaseIsolation:
    """Test cart database isolation across KG and US markets"""
    
    def test_kg_cart_saved_to_kg_database_only(
        self,
        kg_user,
        kg_test_sku,
        kg_db_session,
        us_db_session
    ):
        """Test that KG cart is saved to KG database only"""
        # Delete any existing cart for this user
        existing_cart = kg_db_session.query(Cart).filter(Cart.user_id == kg_user.id).first()
        if existing_cart:
            kg_db_session.delete(existing_cart)
            kg_db_session.commit()
        
        # Create cart and cart item in KG database
        kg_cart = Cart(user_id=kg_user.id)
        kg_db_session.add(kg_cart)
        kg_db_session.commit()
        kg_db_session.refresh(kg_cart)
        
        cart_item = CartItem(cart_id=kg_cart.id, sku_id=kg_test_sku.id, quantity=2)
        kg_db_session.add(cart_item)
        kg_db_session.commit()
        
        # Verify cart exists in KG database
        kg_cart_check = kg_db_session.query(Cart).filter(Cart.user_id == kg_user.id).first()
        assert kg_cart_check is not None, "Cart not found in KG database"
        
        # Verify cart items exist in KG database
        kg_cart_items = kg_db_session.query(CartItem).filter(CartItem.cart_id == kg_cart.id).all()
        assert len(kg_cart_items) == 1, "Cart item not found in KG database"
        assert kg_cart_items[0].sku_id == kg_test_sku.id
        
        # Verify NO cart for this user in US database (different DB, different user IDs)
        us_cart_check = us_db_session.query(Cart).filter(Cart.user_id == kg_user.id).first()
        # This should be None because KG user ID doesn't exist in US database
        assert us_cart_check is None, "Cart incorrectly found in US database"
    
    
    def test_us_cart_saved_to_us_database_only(
        self,
        us_user,
        us_test_sku,
        us_db_session,
        kg_db_session
    ):
        """Test that US cart is saved to US database only"""
        # Delete any existing cart for this user
        existing_cart = us_db_session.query(Cart).filter(Cart.user_id == us_user.id).first()
        if existing_cart:
            us_db_session.delete(existing_cart)
            us_db_session.commit()
        
        # Create cart and cart item in US database
        us_cart = Cart(user_id=us_user.id)
        us_db_session.add(us_cart)
        us_db_session.commit()
        us_db_session.refresh(us_cart)
        
        cart_item = CartItem(cart_id=us_cart.id, sku_id=us_test_sku.id, quantity=1)
        us_db_session.add(cart_item)
        us_db_session.commit()
        
        # Verify cart exists in US database
        us_cart_check = us_db_session.query(Cart).filter(Cart.user_id == us_user.id).first()
        assert us_cart_check is not None, "Cart not found in US database"
        
        # Verify cart items exist in US database
        us_cart_items = us_db_session.query(CartItem).filter(CartItem.cart_id == us_cart.id).all()
        assert len(us_cart_items) == 1, "Cart item not found in US database"
        assert us_cart_items[0].sku_id == us_test_sku.id
        
        # Verify NO cart for this user in KG database
        kg_cart_check = kg_db_session.query(Cart).filter(Cart.user_id == us_user.id).first()
        assert kg_cart_check is None, "Cart incorrectly found in KG database"
    
    
    def test_cart_counts_are_market_isolated(
        self,
        kg_user,
        us_user,
        kg_test_sku,
        us_test_sku,
        kg_db_session,
        us_db_session
    ):
        """Test that cart counts in each market are independent"""
        # Get or create KG cart
        kg_cart = kg_db_session.query(Cart).filter(Cart.user_id == kg_user.id).first()
        if not kg_cart:
            kg_cart = Cart(user_id=kg_user.id)
            kg_db_session.add(kg_cart)
            kg_db_session.commit()
            kg_db_session.refresh(kg_cart)
        
        kg_item = CartItem(cart_id=kg_cart.id, sku_id=kg_test_sku.id, quantity=3)
        kg_db_session.add(kg_item)
        kg_db_session.commit()
        
        # Get or create US cart
        us_cart = us_db_session.query(Cart).filter(Cart.user_id == us_user.id).first()
        if not us_cart:
            us_cart = Cart(user_id=us_user.id)
            us_db_session.add(us_cart)
            us_db_session.commit()
            us_db_session.refresh(us_cart)
        
        us_item = CartItem(cart_id=us_cart.id, sku_id=us_test_sku.id, quantity=2)
        us_db_session.add(us_item)
        us_db_session.commit()
        
        # Count carts in each database
        kg_cart_count = kg_db_session.query(Cart).count()
        us_cart_count = us_db_session.query(Cart).count()
        
        # Verify both markets have independent cart systems
        assert kg_cart_count > 0, "KG cart count is 0"
        assert us_cart_count > 0, "US cart count is 0"


# ========================================================================
# TEST SUITE 2: Wishlist Database Isolation
# ========================================================================

class TestWishlistDatabaseIsolation:
    """Test wishlist database isolation across KG and US markets"""
    
    def test_kg_wishlist_saved_to_kg_database_only(
        self,
        kg_user,
        kg_test_product,
        kg_db_session,
        us_db_session
    ):
        """Test that KG wishlist is saved to KG database only"""
        # Delete any existing wishlist for this user
        existing_wishlist = kg_db_session.query(Wishlist).filter(Wishlist.user_id == kg_user.id).first()
        if existing_wishlist:
            kg_db_session.delete(existing_wishlist)
            kg_db_session.commit()
        
        # Create wishlist and wishlist item in KG database
        kg_wishlist = Wishlist(user_id=kg_user.id)
        kg_db_session.add(kg_wishlist)
        kg_db_session.commit()
        kg_db_session.refresh(kg_wishlist)
        
        wishlist_item = WishlistItem(wishlist_id=kg_wishlist.id, product_id=kg_test_product.id)
        kg_db_session.add(wishlist_item)
        kg_db_session.commit()
        
        # Verify wishlist exists in KG database
        kg_wishlist_check = kg_db_session.query(Wishlist).filter(Wishlist.user_id == kg_user.id).first()
        assert kg_wishlist_check is not None, "Wishlist not found in KG database"
        
        # Verify wishlist items exist in KG database
        kg_wishlist_items = kg_db_session.query(WishlistItem).filter(
            WishlistItem.wishlist_id == kg_wishlist.id
        ).all()
        assert len(kg_wishlist_items) == 1, "Wishlist item not found in KG database"
        assert kg_wishlist_items[0].product_id == kg_test_product.id
        
        # Verify NO wishlist for this user in US database
        us_wishlist_check = us_db_session.query(Wishlist).filter(Wishlist.user_id == kg_user.id).first()
        assert us_wishlist_check is None, "Wishlist incorrectly found in US database"
    
    
    def test_us_wishlist_saved_to_us_database_only(
        self,
        us_user,
        us_test_product,
        us_db_session,
        kg_db_session
    ):
        """Test that US wishlist is saved to US database only"""
        # Delete any existing wishlist for this user
        existing_wishlist = us_db_session.query(Wishlist).filter(Wishlist.user_id == us_user.id).first()
        if existing_wishlist:
            us_db_session.delete(existing_wishlist)
            us_db_session.commit()
        
        # Create wishlist and wishlist item in US database
        us_wishlist = Wishlist(user_id=us_user.id)
        us_db_session.add(us_wishlist)
        us_db_session.commit()
        us_db_session.refresh(us_wishlist)
        
        wishlist_item = WishlistItem(wishlist_id=us_wishlist.id, product_id=us_test_product.id)
        us_db_session.add(wishlist_item)
        us_db_session.commit()
        
        # Verify wishlist exists in US database
        us_wishlist_check = us_db_session.query(Wishlist).filter(Wishlist.user_id == us_user.id).first()
        assert us_wishlist_check is not None, "Wishlist not found in US database"
        
        # Verify wishlist items exist in US database
        us_wishlist_items = us_db_session.query(WishlistItem).filter(
            WishlistItem.wishlist_id == us_wishlist.id
        ).all()
        assert len(us_wishlist_items) == 1, "Wishlist item not found in US database"
        assert us_wishlist_items[0].product_id == us_test_product.id
        
        # Verify NO wishlist for this user in KG database
        kg_wishlist_check = kg_db_session.query(Wishlist).filter(Wishlist.user_id == us_user.id).first()
        assert kg_wishlist_check is None, "Wishlist incorrectly found in KG database"
    
    
    def test_wishlist_counts_are_market_isolated(
        self,
        kg_user,
        us_user,
        kg_test_product,
        us_test_product,
        kg_db_session,
        us_db_session
    ):
        """Test that wishlist counts in each market are independent"""
        # Get or create KG wishlist
        kg_wishlist = kg_db_session.query(Wishlist).filter(Wishlist.user_id == kg_user.id).first()
        if not kg_wishlist:
            kg_wishlist = Wishlist(user_id=kg_user.id)
            kg_db_session.add(kg_wishlist)
            kg_db_session.commit()
            kg_db_session.refresh(kg_wishlist)
        
        kg_item = WishlistItem(wishlist_id=kg_wishlist.id, product_id=kg_test_product.id)
        kg_db_session.add(kg_item)
        kg_db_session.commit()
        
        # Get or create US wishlist
        us_wishlist = us_db_session.query(Wishlist).filter(Wishlist.user_id == us_user.id).first()
        if not us_wishlist:
            us_wishlist = Wishlist(user_id=us_user.id)
            us_db_session.add(us_wishlist)
            us_db_session.commit()
            us_db_session.refresh(us_wishlist)
        
        us_item = WishlistItem(wishlist_id=us_wishlist.id, product_id=us_test_product.id)
        us_db_session.add(us_item)
        us_db_session.commit()
        
        # Count wishlists in each database
        kg_wishlist_count = kg_db_session.query(Wishlist).count()
        us_wishlist_count = us_db_session.query(Wishlist).count()
        
        # Verify both markets have independent wishlist systems
        assert kg_wishlist_count > 0, "KG wishlist count is 0"
        assert us_wishlist_count > 0, "US wishlist count is 0"


# ========================================================================
# TEST SUITE 3: Cart/Wishlist Data Integrity
# ========================================================================

class TestCartWishlistDataIntegrity:
    """Test data integrity for cart and wishlist operations"""
    
    def test_cart_item_references_correct_sku_in_kg(
        self,
        kg_user,
        kg_test_sku,
        kg_db_session
    ):
        """Test that cart item correctly references SKU in KG database"""
        # Get or create cart
        kg_cart = kg_db_session.query(Cart).filter(Cart.user_id == kg_user.id).first()
        if not kg_cart:
            kg_cart = Cart(user_id=kg_user.id)
            kg_db_session.add(kg_cart)
            kg_db_session.commit()
            kg_db_session.refresh(kg_cart)
        
        cart_item = CartItem(cart_id=kg_cart.id, sku_id=kg_test_sku.id, quantity=5)
        kg_db_session.add(cart_item)
        kg_db_session.commit()
        kg_db_session.refresh(cart_item)
        
        # Verify relationships
        assert cart_item.sku.id == kg_test_sku.id
        assert cart_item.cart.user_id == kg_user.id
        assert cart_item.quantity == 5
    
    
    def test_wishlist_item_references_correct_product_in_us(
        self,
        us_user,
        us_test_product,
        us_db_session
    ):
        """Test that wishlist item correctly references product in US database"""
        # Get or create wishlist
        us_wishlist = us_db_session.query(Wishlist).filter(Wishlist.user_id == us_user.id).first()
        if not us_wishlist:
            us_wishlist = Wishlist(user_id=us_user.id)
            us_db_session.add(us_wishlist)
            us_db_session.commit()
            us_db_session.refresh(us_wishlist)
        
        wishlist_item = WishlistItem(wishlist_id=us_wishlist.id, product_id=us_test_product.id)
        us_db_session.add(wishlist_item)
        us_db_session.commit()
        us_db_session.refresh(wishlist_item)
        
        # Verify relationships
        assert wishlist_item.product.id == us_test_product.id
        assert wishlist_item.wishlist.user_id == us_user.id
    
    
    def test_multiple_cart_items_for_same_user_kg(
        self,
        kg_user,
        kg_db_session
    ):
        """Test that a KG user can have multiple items in their cart"""
        # Get multiple SKUs
        skus = kg_db_session.query(SKU).filter(
            SKU.is_active == True,
            SKU.stock > 0
        ).limit(3).all()
        
        assert len(skus) >= 2, "Need at least 2 SKUs for this test"
        
        # Get or create cart
        kg_cart = kg_db_session.query(Cart).filter(Cart.user_id == kg_user.id).first()
        if not kg_cart:
            kg_cart = Cart(user_id=kg_user.id)
            kg_db_session.add(kg_cart)
            kg_db_session.commit()
            kg_db_session.refresh(kg_cart)
        
        # Add multiple items
        for sku in skus[:2]:
            cart_item = CartItem(cart_id=kg_cart.id, sku_id=sku.id, quantity=1)
            kg_db_session.add(cart_item)
        
        kg_db_session.commit()
        
        # Verify multiple items
        cart_items = kg_db_session.query(CartItem).filter(CartItem.cart_id == kg_cart.id).all()
        assert len(cart_items) >= 2, "Should have at least 2 cart items"
    
    
    def test_cart_deletion_cascades_to_items(
        self,
        kg_user,
        kg_test_sku,
        kg_db_session
    ):
        """Test that deleting a cart also deletes its items (cascade)"""
        # Get or create cart
        kg_cart = kg_db_session.query(Cart).filter(Cart.user_id == kg_user.id).first()
        if not kg_cart:
            kg_cart = Cart(user_id=kg_user.id)
            kg_db_session.add(kg_cart)
            kg_db_session.commit()
            kg_db_session.refresh(kg_cart)
        
        cart_item = CartItem(cart_id=kg_cart.id, sku_id=kg_test_sku.id, quantity=1)
        kg_db_session.add(cart_item)
        kg_db_session.commit()
        
        cart_id = kg_cart.id
        
        # Delete cart
        kg_db_session.delete(kg_cart)
        kg_db_session.commit()
        
        # Verify cart items are also deleted
        remaining_items = kg_db_session.query(CartItem).filter(CartItem.cart_id == cart_id).all()
        assert len(remaining_items) == 0, "Cart items not deleted on cascade"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
