from sqladmin import BaseView, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from typing import Optional
import secrets
import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from ..models import (
    Product, SKU, ProductAsset, Review, ProductAttribute,
    User, Admin, AdminLog
)
from ..db.market_db import db_manager, Market

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class WebsiteContentAuthenticationBackend(AuthenticationBackend):
    """Custom authentication for website content admin"""
    
    async def login(self, request: Request) -> bool:
        """Authenticate admin user - checks BOTH KG and US databases"""
        logger.info("="*70)
        logger.info("🔐 ADMIN LOGIN ATTEMPT")
        logger.info("="*70)
        
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        
        logger.info(f"📝 Received credentials:")
        logger.info(f"   Username: '{username}'")
        logger.info(f"   Password length: {len(password) if password else 0} chars")
        
        if not username or not password:
            logger.error("❌ Missing username or password")
            return False
        
        # Bcrypt limitation: passwords must be <= 72 bytes
        original_length = len(password.encode('utf-8'))
        if original_length > 72:
            logger.warning(f"⚠️  Password too long ({original_length} bytes), truncating to 72 bytes")
            password = password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
        
        # Try both databases (KG first, then US)
        for market in [Market.KG, Market.US]:
            logger.info(f"\n{'─'*70}")
            logger.info(f"🔍 Checking {market.value.upper()} database...")
            logger.info(f"{'─'*70}")
            
            db = next(db_manager.get_db_session(market))
            
            try:
                # Find admin by username
                logger.debug(f"   🔎 Searching for admin with username: '{username}'")
                admin = db.query(Admin).filter(Admin.username == username).first()
                
                if not admin:
                    logger.warning(f"   ⚠️  Admin '{username}' not found in {market.value} database")
                    continue  # Try next database
                
                logger.info(f"   ✅ Found admin: ID={admin.id}, Username='{admin.username}'")
                
                # Check if admin is active
                if not admin.is_active:
                    logger.warning(f"   ❌ Admin is INACTIVE (is_active={admin.is_active})")
                    continue  # Try next database
                
                logger.info(f"   ✅ Admin is active")
                
                # Verify password
                if not admin.hashed_password:
                    logger.error(f"   ❌ Admin has NO password hash stored!")
                    continue  # Try next database
                
                logger.info(f"   🔐 Password hash found (length: {len(admin.hashed_password)} chars)")
                logger.debug(f"   🔐 Hash preview: {admin.hashed_password[:30]}...")
                
                # Use bcrypt directly for verification
                logger.debug(f"   🔓 Verifying password with bcrypt...")
                password_bytes = password.encode('utf-8')
                hash_bytes = admin.hashed_password.encode('utf-8')
                
                logger.debug(f"   📊 Password bytes length: {len(password_bytes)}")
                logger.debug(f"   📊 Hash bytes length: {len(hash_bytes)}")
                    
                if not bcrypt.checkpw(password_bytes, hash_bytes):
                    logger.error(f"   ❌ Password verification FAILED!")
                    continue  # Try next database
                
                logger.info(f"   ✅ Password verification SUCCESS!")
                
                # ✅ Authentication successful!
                logger.info(f"\n{'='*70}")
                logger.info(f"✅ AUTHENTICATION SUCCESSFUL!")
                logger.info(f"{'='*70}")
                logger.info(f"   User: {admin.username}")
                logger.info(f"   ID: {admin.id}")
                logger.info(f"   Database: {market.value}")
                logger.info(f"   Super Admin: {admin.is_super_admin}")
                
                # Update last login
                admin.last_login = datetime.utcnow()
                db.commit()
                logger.debug(f"   ✅ Updated last_login timestamp")
                
                # Create session
                token = secrets.token_urlsafe(32)
                request.session.update({
                    "token": token,
                    "admin_id": admin.id,
                    "admin_username": admin.username,
                    "is_super_admin": admin.is_super_admin,
                    "admin_market": market.value  # Store which database the admin is in
                })
                
                logger.info(f"   ✅ Session created with token: {token[:16]}...")
                logger.info(f"{'='*70}\n")
                
                return True
                
            except Exception as e:
                logger.error(f"   ❌ EXCEPTION in {market.value} database: {type(e).__name__}: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
            finally:
                db.close()
                logger.debug(f"   🔒 Database connection closed")
        
        # No valid admin found in any database
        logger.error(f"\n{'='*70}")
        logger.error(f"❌ LOGIN FAILED")
        logger.error(f"{'='*70}")
        logger.error(f"   Username: '{username}'")
        logger.error(f"   Reason: Not found in any database OR password mismatch")
        logger.error(f"{'='*70}\n")
        return False
    
    async def logout(self, request: Request) -> bool:
        """Logout admin user"""
        request.session.clear()
        return True
    
    async def authenticate(self, request: Request) -> bool:
        """Check if user is authenticated - checks the correct database"""
        logger.debug("🔍 Checking authentication status...")
        
        token = request.session.get("token")
        admin_id = request.session.get("admin_id")
        admin_market = request.session.get("admin_market", "kg")  # Default to KG for backward compatibility
        
        logger.debug(f"   Session data: token={'✓' if token else '✗'}, admin_id={admin_id}, market={admin_market}")
        
        if not token or not admin_id:
            logger.debug("   ❌ No token or admin_id in session")
            return False
        
        # Get the market from session (or try both if not set)
        try:
            market = Market.KG if admin_market == "kg" else Market.US
            logger.debug(f"   📊 Using {market.value.upper()} database")
        except:
            market = Market.KG
            logger.warning(f"   ⚠️  Error determining market, defaulting to KG")
        
        # Check admin exists and is active in the correct database
        db = next(db_manager.get_db_session(market))
        try:
            admin = db.query(Admin).filter(Admin.id == admin_id).first()
            if not admin:
                logger.warning(f"   ❌ Admin ID {admin_id} not found in {market.value} database")
                return False
            if not admin.is_active:
                logger.warning(f"   ❌ Admin {admin.username} is inactive")
                return False
            
            logger.debug(f"   ✅ Authentication valid for {admin.username} (ID: {admin_id})")
            return True
        except Exception as e:
            logger.error(f"   ❌ Authentication check error: {type(e).__name__}: {e}")
            return False
        finally:
            db.close()


class ProductAdmin(ModelView, model=Product):
    """Product management interface"""
    
    # Display settings
    name = "Товары"
    name_plural = "Товары"
    icon = "fa-solid fa-box"
    
    # Column configuration
    column_list = [
        "id", "brand", "title", "slug", "sold_count", 
        "rating_avg", "rating_count", "created_at"
    ]
    column_details_list = [
        "id", "brand", "title", "slug", "description",
        "sold_count", "rating_avg", "rating_count", 
        "attributes", "created_at", "updated_at"
    ]
    
    # Form configuration
    form_columns = [
        "brand", "title", "slug", "description", "attributes"
    ]
    
    # Search and filters
    column_searchable_list = ["title", "brand", "slug"]
    column_sortable_list = ["id", "brand", "title", "sold_count", "rating_avg", "created_at"]
    column_filters = ["brand", "created_at"]
    
    # Custom labels
    column_labels = {
        "id": "ID",
        "brand": "Бренд",
        "title": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "sold_count": "Продано",
        "rating_avg": "Рейтинг",
        "rating_count": "Отзывов",
        "attributes": "Атрибуты",
        "created_at": "Создано",
        "updated_at": "Обновлено"
    }
    
    # Form labels
    form_label = "Товар"
    form_columns_labels = {
        "brand": "Бренд",
        "title": "Название товара",
        "slug": "URL-адрес (slug)",
        "description": "Описание товара",
        "attributes": "Атрибуты (JSON)"
    }
    
    # Custom methods
    def can_create(self, request: Request) -> bool:
        return True
    
    def can_edit(self, request: Request) -> bool:
        return True
    
    def can_delete(self, request: Request) -> bool:
        return True
    
    def can_view_details(self, request: Request) -> bool:
        return True


class SKUAdmin(ModelView, model=SKU):
    """SKU management interface"""
    
    name = "Артикулы"
    name_plural = "Артикулы"
    icon = "fa-solid fa-tags"
    
    column_list = [
        "id", "sku_code", "size", "color", "price", "stock", "is_active"
    ]
    column_details_list = [
        "id", "product_id", "sku_code", "size", "color", 
        "price", "stock", "is_active"
    ]
    
    form_columns = [
        "product_id", "sku_code", "size", "color", "price", "stock", "is_active"
    ]
    
    column_searchable_list = ["sku_code", "size", "color"]
    column_sortable_list = ["id", "sku_code", "price", "stock", "is_active"]
    column_filters = ["size", "color", "is_active"]
    
    column_labels = {
        "id": "ID",
        "product_id": "ID товара",
        "sku_code": "Код артикула",
        "size": "Размер",
        "color": "Цвет",
        "price": "Цена",
        "stock": "Остаток",
        "is_active": "Активен"
    }
    
    form_label = "Артикул"
    form_columns_labels = {
        "product_id": "ID товара",
        "sku_code": "Код артикула",
        "size": "Размер",
        "color": "Цвет",
        "price": "Цена (сом)",
        "stock": "Количество на складе",
        "is_active": "Активен для продажи"
    }


class ProductAssetAdmin(ModelView, model=ProductAsset):
    """Product assets management interface"""
    
    name = "Медиа файлы"
    name_plural = "Медиа файлы"
    icon = "fa-solid fa-image"
    
    column_list = ["id", "product_id", "type", "url", "alt_text", "order"]
    column_details_list = [
        "id", "product_id", "url", "type", "alt_text", "order"
    ]
    
    form_columns = [
        "product_id", "url", "type", "alt_text", "order"
    ]
    
    column_searchable_list = ["url", "alt_text"]
    column_sortable_list = ["id", "type", "order"]
    column_filters = ["type", "product_id"]
    
    column_labels = {
        "id": "ID",
        "product_id": "ID товара",
        "url": "URL файла",
        "type": "Тип",
        "alt_text": "Альтернативный текст",
        "order": "Порядок"
    }
    
    form_label = "Медиа файл"
    form_columns_labels = {
        "product_id": "ID товара",
        "url": "URL файла",
        "type": "Тип (image/video)",
        "alt_text": "Альтернативный текст",
        "order": "Порядок отображения"
    }


class ProductAttributeAdmin(ModelView, model=ProductAttribute):
    """Product attributes management interface"""
    
    name = "Атрибуты товаров"
    name_plural = "Атрибуты товаров"
    icon = "fa-solid fa-list"
    
    column_list = [
        "id", "attribute_type", "attribute_value", "display_name", 
        "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "attribute_type", "attribute_value", "display_name",
        "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "attribute_type", "attribute_value", "display_name", 
        "sort_order", "is_active"
    ]
    
    column_searchable_list = ["attribute_value", "display_name"]
    column_sortable_list = ["id", "attribute_type", "sort_order", "is_active"]
    column_filters = ["attribute_type", "is_active"]
    
    column_labels = {
        "id": "ID",
        "attribute_type": "Тип атрибута",
        "attribute_value": "Значение",
        "display_name": "Отображаемое имя",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен",
        "created_at": "Создано"
    }
    
    form_label = "Атрибут товара"
    form_columns_labels = {
        "attribute_type": "Тип (size, color, category, brand)",
        "attribute_value": "Значение атрибута",
        "display_name": "Отображаемое имя",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ReviewAdmin(ModelView, model=Review):
    """Product reviews management interface"""
    
    name = "Отзывы"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"
    
    column_list = [
        "id", "product_id", "user_id", "rating", "created_at"
    ]
    column_details_list = [
        "id", "product_id", "user_id", "rating", "text", "created_at"
    ]
    
    form_columns = [
        "product_id", "user_id", "rating", "text"
    ]
    
    column_searchable_list = ["text"]
    column_sortable_list = ["id", "rating", "created_at"]
    column_filters = ["rating", "product_id", "user_id"]
    
    column_labels = {
        "id": "ID",
        "product_id": "ID товара",
        "user_id": "ID пользователя",
        "rating": "Оценка",
        "text": "Текст отзыва",
        "created_at": "Создано"
    }
    
    form_label = "Отзыв"
    form_columns_labels = {
        "product_id": "ID товара",
        "user_id": "ID пользователя",
        "rating": "Оценка (1-5)",
        "text": "Текст отзыва"
    }


class UserAdmin(ModelView, model=User):
    """User management interface"""
    
    name = "Пользователи"
    name_plural = "Пользователи"
    icon = "fa-solid fa-users"
    
    column_list = [
        "id", "username", "email", "full_name", "is_active", "is_verified", "created_at"
    ]
    column_details_list = [
        "id", "username", "email", "full_name", "is_active", 
        "is_verified", "created_at", "updated_at"
    ]
    
    form_columns = [
        "username", "email", "full_name", "is_active", "is_verified"
    ]
    
    column_searchable_list = ["username", "email", "full_name"]
    column_sortable_list = ["id", "username", "email", "created_at"]
    column_filters = ["is_active", "is_verified"]
    
    column_labels = {
        "id": "ID",
        "username": "Имя пользователя",
        "email": "Email",
        "full_name": "Полное имя",
        "is_active": "Активен",
        "is_verified": "Подтвержден",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_label = "Пользователь"
    form_columns_labels = {
        "username": "Имя пользователя",
        "email": "Email адрес",
        "full_name": "Полное имя",
        "is_active": "Активный пользователь",
        "is_verified": "Email подтвержден"
    }


class AdminLogAdmin(ModelView, model=AdminLog):
    """Admin activity log interface"""
    
    name = "Журнал действий"
    name_plural = "Журнал действий"
    icon = "fa-solid fa-clipboard-list"
    
    column_list = [
        "id", "admin_id", "action", "entity_type", "entity_id", "created_at"
    ]
    column_details_list = [
        "id", "admin_id", "action", "entity_type", "entity_id", 
        "description", "ip_address", "user_agent", "created_at"
    ]
    
    # Read-only for security
    can_create = False
    can_edit = False
    can_delete = False
    
    column_searchable_list = ["action", "entity_type", "description"]
    column_sortable_list = ["id", "created_at"]
    column_filters = ["action", "entity_type", "admin_id"]
    
    column_labels = {
        "id": "ID",
        "admin_id": "ID администратора",
        "action": "Действие",
        "entity_type": "Тип объекта",
        "entity_id": "ID объекта",
        "description": "Описание",
        "ip_address": "IP адрес",
        "user_agent": "User Agent",
        "created_at": "Время"
    }


# Custom dashboard view
class WebsiteContentDashboard(BaseView):
    """Custom dashboard for website content admin"""
    
    name = "Панель управления"
    icon = "fa-solid fa-chart-pie"
    
    async def index(self, request: Request):
        # Here you would implement custom dashboard logic
        # For now, we'll return a simple response
        return RedirectResponse(url="/admin/product/list")
