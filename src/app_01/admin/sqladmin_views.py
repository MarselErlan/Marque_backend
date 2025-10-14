from sqladmin import BaseView, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse
from typing import Optional
from wtforms import FileField, MultipleFileField
from wtforms.validators import Optional as OptionalValidator
import secrets
import bcrypt
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import os
from PIL import Image
import io

from ..models import (
    Product, SKU, ProductAsset, Review, ProductAttribute,
    User, Admin, AdminLog
)
from ..db.market_db import db_manager, Market
from ..utils.image_upload import image_uploader

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
    """
    Enhanced Product Management Interface
    
    Features:
    - Stock status display
    - SKU count
    - Better brand/category display
    - Enhanced search and filters
    - Export functionality
    """
    
    # Display settings
    name = "Товары"
    name_plural = "Товары"
    icon = "fa-solid fa-box"
    category = "🛍️ Каталог"  # Group in sidebar
    
    # Enhanced column configuration
    column_list = [
        "id", "main_image", "title", "brand", "category", "subcategory",
        "season", "material", "style",
        "sold_count", "rating_avg", "is_active", "is_featured"
    ]
    
    column_details_list = [
        "id", "brand", "category", "subcategory", 
        "season", "material", "style",
        "title", "slug", "description",
        "main_image", "additional_images",
        "sold_count", "rating_avg", "rating_count", 
        "is_active", "is_featured", "attributes",
        "created_at", "updated_at",
        "skus", "reviews"
    ]
    
    # Form configuration - Use relationship names for proper dropdowns
    form_columns = [
        "title", "slug", "description", 
        "brand", "category", "subcategory",
        "season", "material", "style",
        "is_active", "is_featured", "attributes",
        "main_image", "additional_images"  # Image upload fields
    ]
    
    # Include relationships for the form
    form_include_pk = False
    
    # Custom form fields for image uploads
    form_extra_fields = {
        "main_image": FileField(
            "Главное изображение",
            validators=[OptionalValidator()],
            description="Загрузите главное фото (JPEG/PNG, автоматически изменится до 500x500px, оптимизируется Pillow)"
        ),
        "additional_images": MultipleFileField(
            "Дополнительные изображения",
            validators=[OptionalValidator()],
            description="Загрузите до 5 фото (автоматически оптимизируются и сохраняются в /uploads/products/)"
        )
    }
    
    # Form arguments to configure widgets
    form_args = {
        "title": {
            "label": "Название товара",
            "description": "Полное название товара (например: 'Nike Air Max 90')"
        },
        "slug": {
            "label": "URL-адрес",
            "description": "Уникальный URL для товара (например: 'nike-air-max-90')"
        },
        "description": {
            "label": "Описание",
            "description": "Подробное описание товара"
        },
        "brand": {
            "label": "Бренд",
            "description": "Выберите бренд товара"
        },
        "category": {
            "label": "Категория",
            "description": "Выберите категорию (Мужчинам, Женщинам и т.д.)"
        },
        "subcategory": {
            "label": "Подкатегория",
            "description": "Выберите подкатегорию (Футболки, Джинсы и т.д.)"
        },
        "season": {
            "label": "Сезон",
            "description": "Сезон (Зима, Лето, Осень, Весна, Всесезонный) - необязательно"
        },
        "material": {
            "label": "Материал",
            "description": "Основной материал (Хлопок, Полиэстер, Шерсть и т.д.) - необязательно"
        },
        "style": {
            "label": "Стиль",
            "description": "Стиль одежды (Casual, Formal, Sport и т.д.) - необязательно"
        },
        "is_active": {
            "label": "Активен",
            "description": "Отображать товар на сайте?"
        },
        "is_featured": {
            "label": "В топе",
            "description": "Показывать в разделе 'Хиты продаж'?"
        },
        "attributes": {
            "label": "Атрибуты (JSON)",
            "description": "Дополнительные характеристики в формате JSON"
        }
    }
    
    # Enhanced search - search by multiple fields
    column_searchable_list = ["title", "slug", "description"]
    
    # Sortable columns
    column_sortable_list = [
        "id", "title", "sold_count", 
        "rating_avg", "created_at", "is_active"
    ]
    
    # Enhanced filters
    column_filters = [
        "brand_id",
        "category_id",
        "subcategory_id",
        "is_active",
        "sold_count",
        "rating_avg",
        "created_at"
    ]
    
    # Default sorting (most popular first)
    column_default_sort = [("sold_count", True)]  # Descending
    
    # Russian labels
    column_labels = {
        "id": "ID",
        "main_image": "Главное фото",
        "additional_images": "Доп. фото",
        "brand": "Бренд",
        "brand_id": "Бренд",
        "category": "Категория",
        "category_id": "Категория",
        "subcategory": "Подкатегория",
        "subcategory_id": "Подкатегория",
        "season": "Сезон",
        "season_id": "Сезон",
        "material": "Материал",
        "material_id": "Материал",
        "style": "Стиль",
        "style_id": "Стиль",
        "title": "Название",
        "slug": "URL",
        "description": "Описание",
        "sold_count": "Продано",
        "rating_avg": "Рейтинг",
        "rating_count": "Отзывов",
        "is_active": "Активен",
        "is_featured": "В топе",
        "attributes": "Атрибуты",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "skus": "Варианты (SKU)",
        "reviews": "Отзывы"
    }
    
    # Form labels (removed - using form_args for labels now)
    form_label = "Товар"
    
    # Enhanced formatters for better display
    column_formatters = {
        # Main image thumbnail (from Product.main_image column)
        "main_image": lambda model, _: (
            f'<img src="{model.main_image}" style="max-width: 80px; max-height: 80px; object-fit: cover; border-radius: 4px;" />'
            if model.main_image
            else '<span class="badge badge-secondary">Нет фото</span>'
        ),
        
        # Additional images gallery (from Product.additional_images JSON column)
        "additional_images": lambda model, _: (
            '<div style="display: flex; flex-wrap: wrap; gap: 10px;">' +
            ''.join([
                f'<div style="position: relative;">'
                f'<img src="{url}" style="max-width: 150px; max-height: 150px; object-fit: cover; border-radius: 8px; border: 2px solid #ddd;" />'
                f'<div style="text-align: center; font-size: 11px; color: #666; margin-top: 4px;">Изображение {idx + 1}</div>'
                f'</div>'
                for idx, url in enumerate(model.additional_images)
            ]) +
            '</div>'
            if model.additional_images and len(model.additional_images) > 0
            else '<span class="badge badge-secondary">Нет дополнительных изображений</span>'
        ),
        
        # Brand name
        "brand": lambda model, _: model.brand.name if model.brand else "-",
        
        # Category/Subcategory
        "category": lambda model, _: model.category.name if model.category else "-",
        "subcategory": lambda model, _: model.subcategory.name if model.subcategory else "-",
        
        # Season, Material, Style
        "season": lambda model, _: model.season.name if model.season else "-",
        "material": lambda model, _: model.material.name if model.material else "-",
        "style": lambda model, _: model.style.name if model.style else "-",
        
        # Rating with stars
        "rating_avg": lambda model, _: f"⭐ {model.rating_avg:.1f}" if model.rating_avg else "-",
        
        # Sold count with badge
        "sold_count": lambda model, _: f"<span class='badge badge-info'>{model.sold_count}</span>",
        
        # Active status with badge
        "is_active": lambda model, _: (
            '<span class="badge badge-success">✅ Активен</span>' if model.is_active 
            else '<span class="badge badge-secondary">⏸️ Неактивен</span>'
        ),
        
        # Featured status with badge
        "is_featured": lambda model, _: (
            '<span class="badge badge-warning">⭐ В топе</span>' if model.is_featured 
            else '<span class="badge badge-light">-</span>'
        ),
        
        # Created date
        "created_at": lambda model, _: model.created_at.strftime("%d.%m.%Y") if model.created_at else "-"
    }
    
    # Permissions
    can_create = True
    can_edit = True
    can_delete = False  # Don't delete products (set inactive instead)
    can_view_details = True
    can_export = True  # Enable CSV export
    
    # Pagination
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    
    # Description hints
    column_descriptions = {
        "title": "Название товара, которое будет отображаться на сайте",
        "slug": "Уникальный URL-адрес (например: 'nike-air-max-90')",
        "description": "Подробное описание товара для карточки товара",
        "is_active": "Активные товары отображаются на сайте. Неактивные скрыты от покупателей.",
        "is_featured": "Товары в топе показываются в разделе 'Хиты продаж' на главной странице",
        "sold_count": "Количество проданных единиц товара (всех вариантов)",
        "rating_avg": "Средний рейтинг из всех отзывов",
        "brand": "Бренд товара (Nike, Adidas и т.д.)",
        "category": "Основная категория (Мужчинам, Женщинам, Детям)",
        "subcategory": "Подкатегория (Футболки, Джинсы, Обувь и т.д.)",
        "season": "Сезон товара (Зима, Лето, Осень, Весна, Всесезонный)",
        "material": "Основной материал (Хлопок, Полиэстер, Шерсть, Кожа и т.д.)",
        "style": "Стиль товара (Casual, Formal, Sport, Street и т.д.)",
        "main_image": "Главное изображение (500x500px, оптимизировано Pillow, хранится в /uploads/products/)",
        "additional_images": "Дополнительные фото (до 5 шт., оптимизированы Pillow, хранятся локально)",
        "attributes": "Дополнительные характеристики в JSON формате"
    }
    
    async def insert_model(self, request: Request, data: dict) -> bool:
        """Custom insert with image upload handling"""
        try:
            # Extract image fields before saving product
            main_image_data = data.pop("main_image", None)
            additional_images_data = data.pop("additional_images", None)
            
            # Handle main image upload
            if main_image_data and hasattr(main_image_data, 'filename') and main_image_data.filename:
                logger.info(f"📸 Uploading main image: {main_image_data.filename}")
                url = await self._save_product_image(main_image_data, 0, order=0)
                if url:
                    data["main_image"] = url
            
            # Handle additional images
            additional_urls = []
            if additional_images_data:
                for idx, image_data in enumerate(additional_images_data, start=1):
                    if hasattr(image_data, 'filename') and image_data.filename:
                        logger.info(f"📸 Uploading additional image {idx}: {image_data.filename}")
                        url = await self._save_product_image(image_data, 0, order=idx)
                        if url:
                            additional_urls.append(url)
            
            if additional_urls:
                data["additional_images"] = additional_urls
            
            # Create the product with image URLs in columns
            result = await super().insert_model(request, data)
            
            if result:
                logger.info(f"✅ Product created with {len(additional_urls) + (1 if data.get('main_image') else 0)} images")
            
            return result
                
        except Exception as e:
            logger.error(f"❌ Error in insert_model: {e}")
            return False
    
    async def update_model(self, request: Request, pk: str, data: dict) -> bool:
        """Custom update with image upload handling"""
        try:
            # Extract image fields
            main_image_data = data.pop("main_image", None)
            additional_images_data = data.pop("additional_images", None)
            
            # Handle main image upload (replaces existing)
            if main_image_data and hasattr(main_image_data, 'filename') and main_image_data.filename:
                logger.info(f"📸 Updating main image: {main_image_data.filename}")
                url = await self._save_product_image(main_image_data, pk, order=0)
                if url:
                    data["main_image"] = url
            
            # Handle additional images (appends to existing)
            if additional_images_data:
                db = self.session_maker()
                try:
                    product = db.query(Product).filter_by(id=pk).first()
                    if product:
                        # Get existing additional images
                        existing_images = product.additional_images if product.additional_images else []
                        
                        # Upload new images
                        new_urls = []
                        for idx, image_data in enumerate(additional_images_data, start=1):
                            if hasattr(image_data, 'filename') and image_data.filename:
                                logger.info(f"📸 Adding additional image {idx}: {image_data.filename}")
                                url = await self._save_product_image(image_data, pk, order=len(existing_images) + idx)
                                if url:
                                    new_urls.append(url)
                        
                        # Merge with existing
                        if new_urls:
                            data["additional_images"] = existing_images + new_urls
                    db.close()
                except Exception as e:
                    logger.error(f"❌ Error processing additional images: {e}")
                    db.close()
            
            # Update the product with new image URLs
            result = await super().update_model(request, pk, data)
            
            if result:
                logger.info(f"✅ Product updated with images")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in update_model: {e}")
            return False
    
    async def _save_product_image(self, file_data, product_id: int, order: int) -> Optional[str]:
        """Save uploaded image using Pillow and image_uploader"""
        try:
            # Read file data
            file_bytes = await file_data.read()
            
            # Validate it's an image using Pillow
            try:
                img = Image.open(io.BytesIO(file_bytes))
                img.verify()
                logger.info(f"✅ Valid image: {img.format}, {img.size}")
            except Exception as e:
                logger.error(f"❌ Invalid image file: {e}")
                return None
            
            # Reset file pointer
            await file_data.seek(0)
            
            # Create a temporary UploadFile-like object for image_uploader
            from fastapi import UploadFile
            upload_file = UploadFile(
                filename=file_data.filename,
                file=io.BytesIO(file_bytes)
            )
            
            # Use image_uploader to save with Pillow processing
            url = await image_uploader.save_image(
                file=upload_file,
                category="products",
                resize_to="medium",  # 500x500px
                optimize=True
            )
            
            logger.info(f"✅ Image saved: {url}")
            return url
            
        except Exception as e:
            logger.error(f"❌ Error saving image: {e}")
            return None


class SKUAdmin(ModelView, model=SKU):
    """
    Enhanced SKU Management Interface
    
    Features:
    - Color-coded stock levels
    - Better price formatting
    - Product relationship display
    - Enhanced search and filters
    """
    
    name = "Артикулы"
    name_plural = "Артикулы"
    icon = "fa-solid fa-tags"
    category = "🛍️ Каталог"
    
    # Enhanced column configuration
    column_list = [
        "id", "product", "sku_code", "size", "color", 
        "price", "stock", "is_active"
    ]
    
    column_details_list = [
        "id", "product_id", "product", "sku_code", 
        "size", "color", "price", "original_price",
        "stock", "is_active"
    ]
    
    # Form configuration
    form_columns = [
        "product_id", "sku_code", "size", "color", 
        "price", "original_price", "stock", "is_active"
    ]
    
    # Enhanced search
    column_searchable_list = ["sku_code", "size", "color"]
    
    # Sortable columns
    column_sortable_list = ["id", "sku_code", "price", "stock", "is_active"]
    
    # Enhanced filters
    column_filters = [
        "product_id",
        "size",
        "color",
        "is_active",
        "stock",
        "price"
    ]
    
    # Default sorting (low stock first for attention)
    column_default_sort = [("stock", False)]  # Ascending
    
    # Russian labels
    column_labels = {
        "id": "ID",
        "product": "Товар",
        "product_id": "Товар",
        "sku_code": "Артикул",
        "size": "Размер",
        "color": "Цвет",
        "price": "Цена",
        "original_price": "Старая цена",
        "stock": "Остаток",
        "is_active": "Активен"
    }
    
    # Form labels
    form_label = "Артикул"
    form_columns_labels = {
        "product_id": "Товар",
        "sku_code": "Код артикула",
        "size": "Размер",
        "color": "Цвет",
        "price": "Цена",
        "original_price": "Старая цена (для скидки)",
        "stock": "Количество на складе",
        "is_active": "Активен"
    }
    
    # Enhanced formatters with stock status
    column_formatters = {
        # Product name
        "product": lambda model, _: model.product.title if model.product else "-",
        
        # Price with currency
        "price": lambda model, _: f"{model.price:,.0f} ₸" if model.price else "0 ₸",
        
        # Original price
        "original_price": lambda model, _: f"{model.original_price:,.0f} ₸" if model.original_price else "-",
        
        # Stock with color-coded badges
        "stock": lambda model, _: _format_stock_badge(model.stock),
        
        # Active status
        "is_active": lambda model, _: (
            '<span class="badge badge-success">✅ Активен</span>' if model.is_active 
            else '<span class="badge badge-secondary">⏸️ Неактивен</span>'
        ),
        
        # Size with badge
        "size": lambda model, _: f'<span class="badge badge-light">{model.size}</span>' if model.size else "-",
        
        # Color with badge (could add color preview)
        "color": lambda model, _: f'<span class="badge badge-light">{model.color}</span>' if model.color else "-"
    }
    
    # Permissions
    can_create = True
    can_edit = True
    can_delete = False  # Don't delete SKUs (set inactive instead)
    can_view_details = True
    can_export = True
    
    # Pagination
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    
    # Description hints
    column_descriptions = {
        "stock": "Остаток на складе. Цвет: Красный (<5), Желтый (<10), Зеленый (>=10)",
        "is_active": "Неактивные артикулы не показываются покупателям",
        "original_price": "Если указана, показывается как зачеркнутая цена (скидка)"
    }


def _format_stock_badge(stock):
    """
    Format stock with color-coded badge
    
    Red: < 5 (critical)
    Yellow: < 10 (low)
    Green: >= 10 (good)
    """
    if stock == 0:
        return '<span class="badge badge-danger">❌ Нет</span>'
    elif stock < 5:
        return f'<span class="badge badge-danger">⚠️ {stock}</span>'
    elif stock < 10:
        return f'<span class="badge badge-warning">🔸 {stock}</span>'
    else:
        return f'<span class="badge badge-success">✅ {stock}</span>'


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
