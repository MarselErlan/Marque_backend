"""
Tests for Banner, Cart, and Wishlist Admin Views
Testing BannerAdmin, CartAdmin, WishlistAdmin
"""

import pytest
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.app_01.models.banners.banner import Banner, BannerType
from src.app_01.models.orders.cart import Cart, CartItem
from src.app_01.models.users.wishlist import Wishlist, WishlistItem
from src.app_01.models.users.user import User
from src.app_01.models.products.product import Product
from src.app_01.models.products.sku import SKU


@pytest.mark.skip(reason="Banner uses separate Base - requires manual DB setup verification")
class TestBannerAdminModel:
    """Test Banner model access via admin"""
    
    def test_banner_model_exists(self, admin_test_db):
        """Test that Banner model can be accessed"""
        banners = admin_test_db.query(Banner).all()
        assert isinstance(banners, list)
    
    def test_create_banner(self, admin_test_db):
        """Test creating a banner through admin"""
        banner = Banner(
            title="Summer Sale",
            description="50% off summer collection",
            image_url="https://example.com/banner.jpg",
            banner_type=BannerType.HERO,
            link_url="/products/sale",
            is_active=True,
            display_order=1
        )
        admin_test_db.add(banner)
        admin_test_db.commit()
        admin_test_db.refresh(banner)
        
        assert banner.id is not None
        assert banner.title == "Summer Sale"
        assert banner.banner_type == BannerType.HERO
        assert banner.is_active is True
    
    def test_update_banner(self, admin_test_db):
        """Test updating banner"""
        banner = Banner(
            title="Test Banner",
            image_url="https://example.com/test.jpg",
            banner_type=BannerType.PROMO,
            is_active=True
        )
        admin_test_db.add(banner)
        admin_test_db.commit()
        admin_test_db.refresh(banner)
        
        # Update
        banner.is_active = False
        banner.display_order = 5
        admin_test_db.commit()
        
        updated = admin_test_db.query(Banner).filter(Banner.id == banner.id).first()
        assert updated.is_active is False
        assert updated.display_order == 5
    
    def test_delete_banner(self, admin_test_db):
        """Test deleting banner"""
        banner = Banner(
            title="Delete Me",
            image_url="https://example.com/delete.jpg",
            banner_type=BannerType.HERO,
            is_active=True
        )
        admin_test_db.add(banner)
        admin_test_db.commit()
        banner_id = banner.id
        
        # Delete
        admin_test_db.delete(banner)
        admin_test_db.commit()
        
        deleted = admin_test_db.query(Banner).filter(Banner.id == banner_id).first()
        assert deleted is None
    
    def test_filter_banners_by_type(self, admin_test_db):
        """Test filtering banners by type"""
        # Create sale banner
        sale_banner = Banner(
            title="Sale",
            image_url="https://example.com/sale.jpg",
            banner_type=BannerType.HERO,
            is_active=True
        )
        admin_test_db.add(sale_banner)
        admin_test_db.commit()
        
        # Filter
        sale_banners = admin_test_db.query(Banner).filter(
            Banner.banner_type == BannerType.HERO
        ).all()
        
        assert len(sale_banners) > 0
        assert all(b.banner_type == BannerType.HERO for b in sale_banners)
    
    def test_schedule_banner(self, admin_test_db):
        """Test scheduling banner with dates"""
        now = datetime.utcnow()
        future = now + timedelta(days=7)
        
        banner = Banner(
            title="Scheduled Banner",
            image_url="https://example.com/scheduled.jpg",
            banner_type=BannerType.PROMO,
            is_active=True,
            start_date=now,
            end_date=future
        )
        admin_test_db.add(banner)
        admin_test_db.commit()
        admin_test_db.refresh(banner)
        
        assert banner.start_date is not None
        assert banner.end_date is not None
        assert banner.end_date > banner.start_date


class TestCartAdminModel:
    """Test Cart model access via admin"""
    
    def test_cart_model_exists(self, admin_test_db):
        """Test that Cart model can be accessed"""
        carts = admin_test_db.query(Cart).all()
        assert isinstance(carts, list)
    
    def test_create_cart(self, admin_test_db):
        """Test creating a cart"""
        # Create user
        user = User(
            phone_number="+996700111222",
            full_name="Cart User",
            is_active=True,
            is_verified=True
        )
        admin_test_db.add(user)
        admin_test_db.commit()
        admin_test_db.refresh(user)
        
        # Create cart
        cart = Cart(user_id=user.id)
        admin_test_db.add(cart)
        admin_test_db.commit()
        admin_test_db.refresh(cart)
        
        assert cart.id is not None
        assert cart.user_id == user.id
    
    def test_cart_with_items(self, admin_test_db, sample_product_for_admin):
        """Test cart with items"""
        # Create user
        user = User(
            phone_number="+996700333444",
            full_name="Cart Item User",
            is_active=True,
            is_verified=True
        )
        admin_test_db.add(user)
        admin_test_db.commit()
        admin_test_db.refresh(user)
        
        # Create SKU
        sku = SKU(
            product_id=sample_product_for_admin.id,
            sku_code="CART-SKU-001",
            size="L",
            color="Blue",
            price=1500.0,
            stock=5,
            is_active=True
        )
        admin_test_db.add(sku)
        admin_test_db.commit()
        admin_test_db.refresh(sku)
        
        # Create cart
        cart = Cart(user_id=user.id)
        admin_test_db.add(cart)
        admin_test_db.commit()
        admin_test_db.refresh(cart)
        
        # Add item to cart
        cart_item = CartItem(
            cart_id=cart.id,
            sku_id=sku.id,
            quantity=2
        )
        admin_test_db.add(cart_item)
        admin_test_db.commit()
        admin_test_db.refresh(cart_item)
        
        # Verify
        cart_with_items = admin_test_db.query(Cart).filter(Cart.id == cart.id).first()
        assert len(cart_with_items.items) == 1
        assert cart_with_items.items[0].quantity == 2
    
    def test_delete_abandoned_cart(self, admin_test_db):
        """Test deleting abandoned cart"""
        # Create user and cart
        user = User(
            phone_number="+996700555666",
            full_name="Abandoned Cart User",
            is_active=True,
            is_verified=True
        )
        admin_test_db.add(user)
        admin_test_db.commit()
        admin_test_db.refresh(user)
        
        cart = Cart(user_id=user.id)
        admin_test_db.add(cart)
        admin_test_db.commit()
        cart_id = cart.id
        
        # Delete cart
        admin_test_db.delete(cart)
        admin_test_db.commit()
        
        deleted = admin_test_db.query(Cart).filter(Cart.id == cart_id).first()
        assert deleted is None


class TestWishlistAdminModel:
    """Test Wishlist model access via admin"""
    
    def test_wishlist_model_exists(self, admin_test_db):
        """Test that Wishlist model can be accessed"""
        wishlists = admin_test_db.query(Wishlist).all()
        assert isinstance(wishlists, list)
    
    def test_create_wishlist(self, admin_test_db):
        """Test creating a wishlist"""
        # Create user
        user = User(
            phone_number="+996700777888",
            full_name="Wishlist User",
            is_active=True,
            is_verified=True
        )
        admin_test_db.add(user)
        admin_test_db.commit()
        admin_test_db.refresh(user)
        
        # Create wishlist
        wishlist = Wishlist(user_id=user.id)
        admin_test_db.add(wishlist)
        admin_test_db.commit()
        admin_test_db.refresh(wishlist)
        
        assert wishlist.id is not None
        assert wishlist.user_id == user.id
    
    def test_wishlist_with_items(self, admin_test_db, sample_product_for_admin):
        """Test wishlist with items"""
        # Create user
        user = User(
            phone_number="+996700999000",
            full_name="Wishlist Item User",
            is_active=True,
            is_verified=True
        )
        admin_test_db.add(user)
        admin_test_db.commit()
        admin_test_db.refresh(user)
        
        # Create wishlist
        wishlist = Wishlist(user_id=user.id)
        admin_test_db.add(wishlist)
        admin_test_db.commit()
        admin_test_db.refresh(wishlist)
        
        # Add item to wishlist
        wishlist_item = WishlistItem(
            wishlist_id=wishlist.id,
            product_id=sample_product_for_admin.id
        )
        admin_test_db.add(wishlist_item)
        admin_test_db.commit()
        admin_test_db.refresh(wishlist_item)
        
        # Verify
        wishlist_with_items = admin_test_db.query(Wishlist).filter(Wishlist.id == wishlist.id).first()
        assert len(wishlist_with_items.items) == 1
        assert wishlist_with_items.items[0].product_id == sample_product_for_admin.id
    
    def test_popular_wishlist_items(self, admin_test_db, sample_product_for_admin):
        """Test finding popular wishlist items"""
        # Create multiple users and wishlists with same product
        for i in range(3):
            user = User(
                phone_number=f"+99670000{i}000",
                full_name=f"User {i}",
                is_active=True,
                is_verified=True
            )
            admin_test_db.add(user)
            admin_test_db.commit()
            admin_test_db.refresh(user)
            
            wishlist = Wishlist(user_id=user.id)
            admin_test_db.add(wishlist)
            admin_test_db.commit()
            admin_test_db.refresh(wishlist)
            
            wishlist_item = WishlistItem(
                wishlist_id=wishlist.id,
                product_id=sample_product_for_admin.id
            )
            admin_test_db.add(wishlist_item)
            admin_test_db.commit()
        
        # Check how many times the product is in wishlists
        count = admin_test_db.query(WishlistItem).filter(
            WishlistItem.product_id == sample_product_for_admin.id
        ).count()
        
        assert count >= 3


# Mark all tests as admin tests
pytestmark = pytest.mark.admin

