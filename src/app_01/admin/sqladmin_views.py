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
                    "admin_market": market.value,  # Store which database the admin is in
                    "selected_market": market.value  # Set default selected market based on login database
                })
                
                logger.info(f"   ✅ Session created with token: {token[:16]}...")
                logger.info(f"   ✅ Default market set to: {market.value.upper()}")
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
    """Admin interface for managing products."""

    name = "Товар"
    name_plural = f"Товары"
    icon = "fa-solid fa-box"
    category = "🛍️ Каталог"

    column_list = [
        "id", "main_image", "title", "brand", "category",
        "is_active", "is_featured"
    ]

    column_details_list = [
        "id", "title", "slug", "description",
        "brand", "category", "subcategory",
        "season", "material", "style",
        "is_active", "is_featured",
        "created_at", "updated_at",
        "main_image", "additional_images",
        "skus", "reviews"
    ]

    form_columns = [
        "title", "slug", "description",
        "brand", "category", "subcategory",
        "season", "material", "style",
        "is_active", "is_featured", "attributes"
    ]

    async def scaffold_form(self):
        """Override to add image upload fields programmatically"""
        form_class = await super().scaffold_form()
        
        # Add main image upload field
        form_class.main_image = FileField(
            "Главное изображение",
            validators=[OptionalValidator()],
            description="Загрузите главное фото товара (JPEG/PNG)"
        )
        
        # Add multiple additional images upload field
        form_class.additional_images = MultipleFileField(
            "Дополнительные изображения",
            validators=[OptionalValidator()],
            description="Загрузите до 5 дополнительных фото (JPEG/PNG)"
        )
        
        return form_class

    column_searchable_list = [
        "title", "description", "brand.name", "category.name", "subcategory.name"
    ]
    
    column_sortable_list = ["id", "title", "brand", "category", "is_active", "created_at"]
    
    column_filters = [
        "is_active", "is_featured", "brand", "category", "subcategory",
        "season", "material", "style"
    ]

    column_labels = {
        "id": "ID", "title": "Название", "slug": "URL", "description": "Описание",
        "brand": "Бренд", "category": "Категория", "subcategory": "Подкатегория",
        "season": "Сезон", "material": "Материал", "style": "Стиль",
        "is_active": "Активен", "is_featured": "В избранном",
        "created_at": "Создан", "updated_at": "Обновлен",
        "main_image": "Главное фото", "additional_images": "Доп. фото",
        "skus": "SKU (Размеры/Цвета)", "reviews": "Отзывы", "attributes": "Атрибуты (JSON)"
    }
    
    column_formatters = {
        "main_image": lambda m, a: f'<img src="{m.main_image}" width="40">' if m.main_image else ""
    }

    async def _save_single_image(self, file_data, image_type="main"):
        """Save a single product image."""
        from fastapi import UploadFile
        
        logger.info(f"🔍 [PRODUCT {image_type.upper()}] Starting _save_single_image method")
        
        if not file_data:
            logger.warning(f"⚠️ [PRODUCT {image_type.upper()}] No file_data provided")
            return None
            
        if not hasattr(file_data, "filename"):
            logger.warning(f"⚠️ [PRODUCT {image_type.upper()}] file_data has no filename attribute")
            return None
            
        if not file_data.filename:
            logger.warning(f"⚠️ [PRODUCT {image_type.upper()}] filename is empty")
            return None
            
        logger.info(f"📁 [PRODUCT {image_type.upper()}] Processing file: {file_data.filename}")
        
        try:
            # Re-read file bytes for processing
            await file_data.seek(0)
            file_bytes = await file_data.read()
            logger.info(f"📊 [PRODUCT {image_type.upper()}] Read {len(file_bytes)} bytes from uploaded file")
            
            # Validate with Pillow
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
            logger.info(f"✅ [PRODUCT {image_type.upper()}] Pillow validation passed - Image format: {img.format}")
            
            upload_file = UploadFile(filename=file_data.filename, file=io.BytesIO(file_bytes))
            
            logger.info(f"💾 [PRODUCT {image_type.upper()}] Calling image_uploader.save_image...")
            url = await image_uploader.save_image(
                file=upload_file, category="product"
            )
            logger.info(f"✅ [PRODUCT {image_type.upper()}] Image uploaded successfully to: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ [PRODUCT {image_type.upper()}] Failed to save image: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"📋 [PRODUCT {image_type.upper()}] Traceback: {traceback.format_exc()}")
            return None

    async def insert_model(self, request: Request, data: dict) -> any:
        """Handle image uploads when creating a new product."""
        logger.info("🆕 [PRODUCT INSERT] Starting insert_model")
        logger.info(f"📦 [PRODUCT INSERT] Data keys received: {list(data.keys())}")
        
        # Extract main image file
        main_image_file = data.pop("main_image", None)
        logger.info(f"🖼️ [PRODUCT INSERT] Extracted main_image_file: {main_image_file}")
        
        # Extract additional images files (multiple)
        additional_files = data.pop("additional_images", None)
        logger.info(f"📸 [PRODUCT INSERT] Extracted additional_images: {additional_files}")
        
        # Save main image if provided
        if main_image_file and hasattr(main_image_file, "filename") and main_image_file.filename:
            logger.info(f"📤 [PRODUCT INSERT] Uploading main image: {main_image_file.filename}")
            main_url = await self._save_single_image(main_image_file, "main")
            if main_url:
                data["main_image"] = main_url
                logger.info(f"✅ [PRODUCT INSERT] Main image URL set: {main_url}")
            else:
                logger.error("❌ [PRODUCT INSERT] Main image upload failed")
        else:
            logger.info("ℹ️ [PRODUCT INSERT] No main image provided")
        
        # Save additional images if provided (multiple files)
        additional_urls = []
        if additional_files:
            # MultipleFileField returns a list of FileStorage objects
            files_to_process = additional_files if isinstance(additional_files, list) else [additional_files]
            logger.info(f"📸 [PRODUCT INSERT] Processing {len(files_to_process)} additional images")
            
            for idx, file_data in enumerate(files_to_process):
                if file_data and hasattr(file_data, "filename") and file_data.filename:
                    logger.info(f"📤 [PRODUCT INSERT] Uploading additional image {idx+1}: {file_data.filename}")
                    url = await self._save_single_image(file_data, f"additional-{idx+1}")
                    if url:
                        additional_urls.append(url)
                        logger.info(f"✅ [PRODUCT INSERT] Additional image {idx+1} URL: {url}")
                    else:
                        logger.error(f"❌ [PRODUCT INSERT] Additional image {idx+1} upload failed")
            
            if additional_urls:
                data["additional_images"] = additional_urls
                logger.info(f"✅ [PRODUCT INSERT] Set {len(additional_urls)} additional image URLs")
        else:
            logger.info("ℹ️ [PRODUCT INSERT] No additional images provided")
        
        # Call parent to create the model
        logger.info("💾 [PRODUCT INSERT] Calling parent insert_model to save to DB")
        result = await super().insert_model(request, data)
        
        if result:
            logger.info(f"✅ [PRODUCT INSERT] SUCCESS - Product created with ID: {result.id}")
            logger.info(f"🖼️ [PRODUCT INSERT] Main image in DB: {result.main_image}")
            logger.info(f"📸 [PRODUCT INSERT] Additional images in DB: {result.additional_images}")
        else:
            logger.error("❌ [PRODUCT INSERT] Failed to create product")
        
        return result

    async def update_model(self, request: Request, pk: str, data: dict) -> any:
        """Handle image uploads when updating a product."""
        logger.info(f"🔄 [PRODUCT UPDATE] Starting update_model for ID: {pk}")
        logger.info(f"📦 [PRODUCT UPDATE] Data keys received: {list(data.keys())}")
        
        # Extract main image file
        main_image_file = data.pop("main_image", None)
        logger.info(f"🖼️ [PRODUCT UPDATE] Extracted main_image_file: {main_image_file}")
        
        # Extract additional images files (multiple)
        additional_files = data.pop("additional_images", None)
        logger.info(f"📸 [PRODUCT UPDATE] Extracted additional_images: {additional_files}")
        
        # Save main image if provided
        if main_image_file and hasattr(main_image_file, "filename") and main_image_file.filename:
            logger.info(f"📤 [PRODUCT UPDATE] Uploading new main image: {main_image_file.filename}")
            main_url = await self._save_single_image(main_image_file, "main")
            if main_url:
                data["main_image"] = main_url
                logger.info(f"✅ [PRODUCT UPDATE] Main image URL set: {main_url}")
            else:
                logger.error("❌ [PRODUCT UPDATE] Main image upload failed")
        else:
            logger.info("ℹ️ [PRODUCT UPDATE] No new main image, keeping existing")
        
        # Save additional images if provided (multiple files)
        if additional_files:
            additional_urls = []
            files_to_process = additional_files if isinstance(additional_files, list) else [additional_files]
            logger.info(f"📸 [PRODUCT UPDATE] Processing {len(files_to_process)} additional images")
            
            for idx, file_data in enumerate(files_to_process):
                if file_data and hasattr(file_data, "filename") and file_data.filename:
                    logger.info(f"📤 [PRODUCT UPDATE] Uploading additional image {idx+1}: {file_data.filename}")
                    url = await self._save_single_image(file_data, f"additional-{idx+1}")
                    if url:
                        additional_urls.append(url)
                        logger.info(f"✅ [PRODUCT UPDATE] Additional image {idx+1} URL: {url}")
                    else:
                        logger.error(f"❌ [PRODUCT UPDATE] Additional image {idx+1} upload failed")
            
            if additional_urls:
                data["additional_images"] = additional_urls
                logger.info(f"✅ [PRODUCT UPDATE] Set {len(additional_urls)} additional image URLs")
        else:
            logger.info("ℹ️ [PRODUCT UPDATE] No new additional images, keeping existing")
        
        # Call parent to update the model
        logger.info("💾 [PRODUCT UPDATE] Calling parent update_model to save to DB")
        result = await super().update_model(request, pk, data)
        
        if result:
            logger.info(f"✅ [PRODUCT UPDATE] SUCCESS - Product updated with ID: {result.id}")
            logger.info(f"🖼️ [PRODUCT UPDATE] Main image in DB: {result.main_image}")
            logger.info(f"📸 [PRODUCT UPDATE] Additional images in DB: {result.additional_images}")
        else:
            logger.error("❌ [PRODUCT UPDATE] Failed to update product")
        
        return result


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
