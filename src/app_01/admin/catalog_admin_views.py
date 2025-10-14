from datetime import datetime
from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField
from wtforms.validators import Optional as OptionalValidator
from PIL import Image
import io
import logging

from ..models import Category, Subcategory, Brand
from ..utils.image_upload import image_uploader
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class CategoryAdmin(ModelView, model=Category):
    """Enhanced Category Management Interface"""
    
    name = "Категории"
    name_plural = "Категории"
    icon = "fa-solid fa-folder-tree"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "image_url", "name", "slug", "icon", "is_active", "sort_order"
    ]
    column_details_exclude_list = ["products"]
    
    form_columns = [
        "name", "slug", "description", "icon", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]

    async def scaffold_form(self):
        """Override to add the image upload field programmatically"""
        form_class = await super().scaffold_form()
        
        # Add the image upload field
        form_class.image_url = FileField(
            "Изображение категории",
            validators=[OptionalValidator()],
            description="Загрузите фото для категории (JPEG/PNG)"
        )
        
        return form_class

    async def _save_image(self, file_data):
        logger.info("🔍 [CATEGORY IMAGE] Starting _save_image method")
        
        if not file_data:
            logger.warning("⚠️ [CATEGORY IMAGE] No file_data provided")
            return None
            
        if not hasattr(file_data, "filename"):
            logger.warning("⚠️ [CATEGORY IMAGE] file_data has no filename attribute")
            return None
            
        if not file_data.filename:
            logger.warning("⚠️ [CATEGORY IMAGE] filename is empty")
            return None
            
        logger.info(f"📁 [CATEGORY IMAGE] Processing file: {file_data.filename}")
        
        try:
            # Re-read file bytes for processing
            await file_data.seek(0)
            file_bytes = await file_data.read()
            logger.info(f"📊 [CATEGORY IMAGE] Read {len(file_bytes)} bytes from uploaded file")
            
            # Validate with Pillow
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
            logger.info(f"✅ [CATEGORY IMAGE] Pillow validation passed - Image format: {img.format}")
            
            upload_file = UploadFile(filename=file_data.filename, file=io.BytesIO(file_bytes))
            
            logger.info("💾 [CATEGORY IMAGE] Calling image_uploader.save_image...")
            url = await image_uploader.save_image(
                file=upload_file, category="category"
            )
            logger.info(f"✅ [CATEGORY IMAGE] Image uploaded successfully to: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ [CATEGORY IMAGE] Failed to save image: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"📋 [CATEGORY IMAGE] Traceback: {traceback.format_exc()}")
            return None

    async def insert_model(self, request: Request, data: dict) -> any:
        """Handle image upload when creating a new category."""
        logger.info("🆕 [CATEGORY INSERT] Starting insert_model")
        logger.info(f"📦 [CATEGORY INSERT] Data keys received: {list(data.keys())}")
        
        # Extract image file before SQLAlchemy tries to process it
        image_file = data.pop("image_url", None)
        logger.info(f"🖼️ [CATEGORY INSERT] Extracted image_file: {image_file}")
        
        # Save the image if provided
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            logger.info(f"📤 [CATEGORY INSERT] Uploading image: {image_file.filename}")
            image_url = await self._save_image(image_file)
            if image_url:
                data["image_url"] = image_url
                logger.info(f"✅ [CATEGORY INSERT] Image URL set in data: {image_url}")
            else:
                logger.error("❌ [CATEGORY INSERT] Image upload failed, URL is None")
        else:
            logger.info("ℹ️ [CATEGORY INSERT] No valid image file provided")
        
        # Call parent to create the model
        logger.info("💾 [CATEGORY INSERT] Calling parent insert_model to save to DB")
        result = await super().insert_model(request, data)
        
        if result:
            logger.info(f"✅ [CATEGORY INSERT] SUCCESS - Category created with ID: {result.id}")
            logger.info(f"🖼️ [CATEGORY INSERT] Final image_url in DB: {result.image_url}")
        else:
            logger.error("❌ [CATEGORY INSERT] Failed to create category")
        
        return result

    async def update_model(self, request: Request, pk: str, data: dict) -> any:
        """Handle image upload when updating a category."""
        logger.info(f"🔄 [CATEGORY UPDATE] Starting update_model for ID: {pk}")
        logger.info(f"📦 [CATEGORY UPDATE] Data keys received: {list(data.keys())}")
        
        # Extract image file before SQLAlchemy tries to process it
        image_file = data.pop("image_url", None)
        logger.info(f"🖼️ [CATEGORY UPDATE] Extracted image_file: {image_file}")
        
        # Save the image if provided
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            logger.info(f"📤 [CATEGORY UPDATE] Uploading new image: {image_file.filename}")
            image_url = await self._save_image(image_file)
            if image_url:
                data["image_url"] = image_url
                logger.info(f"✅ [CATEGORY UPDATE] Image URL set in data: {image_url}")
            else:
                logger.error("❌ [CATEGORY UPDATE] Image upload failed, URL is None")
        else:
            logger.info("ℹ️ [CATEGORY UPDATE] No new image provided, keeping existing")
        
        # Call parent to update the model
        logger.info("💾 [CATEGORY UPDATE] Calling parent update_model to save to DB")
        result = await super().update_model(request, pk, data)
        
        if result:
            logger.info(f"✅ [CATEGORY UPDATE] SUCCESS - Category updated with ID: {result.id}")
            logger.info(f"🖼️ [CATEGORY UPDATE] Final image_url in DB: {result.image_url}")
        else:
            logger.error("❌ [CATEGORY UPDATE] Failed to update category")
        
        return result


class SubcategoryAdmin(ModelView, model=Subcategory):
    """Enhanced Subcategory Management Interface"""
    
    name = "Подкатегории"
    name_plural = f"Подкатегории"
    icon = "fa-solid fa-folder"
    category = "🛍️ Каталог"
    
    column_list = ["id", "image_url", "name", "slug", "is_active", "sort_order"]
    column_details_exclude_list = ["products"]
    
    form_columns = [
        "category", "name", "slug", "description", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]

    async def scaffold_form(self):
        """Override to add the image upload field programmatically"""
        form_class = await super().scaffold_form()
        
        # Add the image upload field
        form_class.image_url = FileField(
            "Изображение",
            validators=[OptionalValidator()],
            description="Загрузите фото для подкатегории (JPEG/PNG)"
        )
        
        return form_class

    async def _save_image(self, file_data):
        logger.info("🔍 [SUBCATEGORY IMAGE] Starting _save_image method")
        
        if not file_data:
            logger.warning("⚠️ [SUBCATEGORY IMAGE] No file_data provided")
            return None
            
        if not hasattr(file_data, "filename"):
            logger.warning("⚠️ [SUBCATEGORY IMAGE] file_data has no filename attribute")
            return None
            
        if not file_data.filename:
            logger.warning("⚠️ [SUBCATEGORY IMAGE] filename is empty")
            return None
            
        logger.info(f"📁 [SUBCATEGORY IMAGE] Processing file: {file_data.filename}")
        
        try:
            # Re-read file bytes for processing
            await file_data.seek(0)
            file_bytes = await file_data.read()
            logger.info(f"📊 [SUBCATEGORY IMAGE] Read {len(file_bytes)} bytes from uploaded file")
            
            # Validate with Pillow
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
            logger.info(f"✅ [SUBCATEGORY IMAGE] Pillow validation passed - Image format: {img.format}")
            
            upload_file = UploadFile(filename=file_data.filename, file=io.BytesIO(file_bytes))
            
            logger.info("💾 [SUBCATEGORY IMAGE] Calling image_uploader.save_image...")
            url = await image_uploader.save_image(
                file=upload_file, category="subcategory"
            )
            logger.info(f"✅ [SUBCATEGORY IMAGE] Image uploaded successfully to: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ [SUBCATEGORY IMAGE] Failed to save image: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"📋 [SUBCATEGORY IMAGE] Traceback: {traceback.format_exc()}")
            return None

    async def insert_model(self, request: Request, data: dict) -> any:
        """Handle image upload when creating a new subcategory."""
        logger.info("🆕 [SUBCATEGORY INSERT] Starting insert_model")
        logger.info(f"📦 [SUBCATEGORY INSERT] Data keys received: {list(data.keys())}")
        
        # Extract image file before SQLAlchemy tries to process it
        image_file = data.pop("image_url", None)
        logger.info(f"🖼️ [SUBCATEGORY INSERT] Extracted image_file: {image_file}")
        
        # Save the image if provided
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            logger.info(f"📤 [SUBCATEGORY INSERT] Uploading image: {image_file.filename}")
            image_url = await self._save_image(image_file)
            if image_url:
                data["image_url"] = image_url
                logger.info(f"✅ [SUBCATEGORY INSERT] Image URL set in data: {image_url}")
            else:
                logger.error("❌ [SUBCATEGORY INSERT] Image upload failed, URL is None")
        else:
            logger.info("ℹ️ [SUBCATEGORY INSERT] No valid image file provided")
        
        # Call parent to create the model
        logger.info("💾 [SUBCATEGORY INSERT] Calling parent insert_model to save to DB")
        result = await super().insert_model(request, data)
        
        if result:
            logger.info(f"✅ [SUBCATEGORY INSERT] SUCCESS - Subcategory created with ID: {result.id}")
            logger.info(f"🖼️ [SUBCATEGORY INSERT] Final image_url in DB: {result.image_url}")
        else:
            logger.error("❌ [SUBCATEGORY INSERT] Failed to create subcategory")
        
        return result

    async def update_model(self, request: Request, pk: str, data: dict) -> any:
        """Handle image upload when updating a subcategory."""
        logger.info(f"🔄 [SUBCATEGORY UPDATE] Starting update_model for ID: {pk}")
        logger.info(f"📦 [SUBCATEGORY UPDATE] Data keys received: {list(data.keys())}")
        
        # Extract image file before SQLAlchemy tries to process it
        image_file = data.pop("image_url", None)
        logger.info(f"🖼️ [SUBCATEGORY UPDATE] Extracted image_file: {image_file}")
        
        # Save the image if provided
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            logger.info(f"📤 [SUBCATEGORY UPDATE] Uploading new image: {image_file.filename}")
            image_url = await self._save_image(image_file)
            if image_url:
                data["image_url"] = image_url
                logger.info(f"✅ [SUBCATEGORY UPDATE] Image URL set in data: {image_url}")
            else:
                logger.error("❌ [SUBCATEGORY UPDATE] Image upload failed, URL is None")
        else:
            logger.info("ℹ️ [SUBCATEGORY UPDATE] No new image provided, keeping existing")
        
        # Call parent to update the model
        logger.info("💾 [SUBCATEGORY UPDATE] Calling parent update_model to save to DB")
        result = await super().update_model(request, pk, data)
        
        if result:
            logger.info(f"✅ [SUBCATEGORY UPDATE] SUCCESS - Subcategory updated with ID: {result.id}")
            logger.info(f"🖼️ [SUBCATEGORY UPDATE] Final image_url in DB: {result.image_url}")
        else:
            logger.error("❌ [SUBCATEGORY UPDATE] Failed to update subcategory")
        
        return result


class BrandAdmin(ModelView, model=Brand):
    """Enhanced Brand Management Interface"""
    
    name = "Бренды"
    name_plural = "Бренды"
    icon = "fa-solid fa-copyright"
    category = "🛍️ Каталог"

    column_list = ["id", "logo_url", "name", "slug", "is_active", "sort_order"]
    column_details_exclude_list = ["products"]
    
    form_columns = [
        "name", "slug", "description", "website_url", "country", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description", "country"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]

    async def scaffold_form(self):
        """Override to add the logo upload field programmatically"""
        form_class = await super().scaffold_form()
        
        # Add the logo upload field
        form_class.logo_url = FileField(
            "Логотип бренда",
            validators=[OptionalValidator()],
            description="Загрузите логотип бренда (JPEG/PNG)"
        )
        
        return form_class

    async def _save_image(self, file_data):
        logger.info("🔍 [BRAND LOGO] Starting _save_image method")
        
        if not file_data:
            logger.warning("⚠️ [BRAND LOGO] No file_data provided")
            return None
            
        if not hasattr(file_data, "filename"):
            logger.warning("⚠️ [BRAND LOGO] file_data has no filename attribute")
            return None
            
        if not file_data.filename:
            logger.warning("⚠️ [BRAND LOGO] filename is empty")
            return None
            
        logger.info(f"📁 [BRAND LOGO] Processing file: {file_data.filename}")
        
        try:
            # Re-read file bytes for processing
            await file_data.seek(0)
            file_bytes = await file_data.read()
            logger.info(f"📊 [BRAND LOGO] Read {len(file_bytes)} bytes from uploaded file")
            
            # Validate with Pillow
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
            logger.info(f"✅ [BRAND LOGO] Pillow validation passed - Image format: {img.format}")
            
            upload_file = UploadFile(filename=file_data.filename, file=io.BytesIO(file_bytes))
            
            logger.info("💾 [BRAND LOGO] Calling image_uploader.save_image...")
            url = await image_uploader.save_image(
                file=upload_file, category="brand"
            )
            logger.info(f"✅ [BRAND LOGO] Logo uploaded successfully to: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ [BRAND LOGO] Failed to save logo: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"📋 [BRAND LOGO] Traceback: {traceback.format_exc()}")
            return None

    async def insert_model(self, request: Request, data: dict) -> any:
        """Handle logo upload when creating a new brand."""
        logger.info("🆕 [BRAND INSERT] Starting insert_model")
        logger.info(f"📦 [BRAND INSERT] Data keys received: {list(data.keys())}")
        
        # Extract logo file before SQLAlchemy tries to process it
        logo_file = data.pop("logo_url", None)
        logger.info(f"🖼️ [BRAND INSERT] Extracted logo_file: {logo_file}")
        
        # Save the logo if provided
        if logo_file and hasattr(logo_file, "filename") and logo_file.filename:
            logger.info(f"📤 [BRAND INSERT] Uploading logo: {logo_file.filename}")
            logo_url = await self._save_image(logo_file)
            if logo_url:
                data["logo_url"] = logo_url
                logger.info(f"✅ [BRAND INSERT] Logo URL set in data: {logo_url}")
            else:
                logger.error("❌ [BRAND INSERT] Logo upload failed, URL is None")
        else:
            logger.info("ℹ️ [BRAND INSERT] No valid logo file provided")
        
        # Call parent to create the model
        logger.info("💾 [BRAND INSERT] Calling parent insert_model to save to DB")
        result = await super().insert_model(request, data)
        
        if result:
            logger.info(f"✅ [BRAND INSERT] SUCCESS - Brand created with ID: {result.id}")
            logger.info(f"🖼️ [BRAND INSERT] Final logo_url in DB: {result.logo_url}")
        else:
            logger.error("❌ [BRAND INSERT] Failed to create brand")
        
        return result

    async def update_model(self, request: Request, pk: str, data: dict) -> any:
        """Handle logo upload when updating a brand."""
        logger.info(f"🔄 [BRAND UPDATE] Starting update_model for ID: {pk}")
        logger.info(f"📦 [BRAND UPDATE] Data keys received: {list(data.keys())}")
        
        # Extract logo file before SQLAlchemy tries to process it
        logo_file = data.pop("logo_url", None)
        logger.info(f"🖼️ [BRAND UPDATE] Extracted logo_file: {logo_file}")
        
        # Save the logo if provided
        if logo_file and hasattr(logo_file, "filename") and logo_file.filename:
            logger.info(f"📤 [BRAND UPDATE] Uploading new logo: {logo_file.filename}")
            logo_url = await self._save_image(logo_file)
            if logo_url:
                data["logo_url"] = logo_url
                logger.info(f"✅ [BRAND UPDATE] Logo URL set in data: {logo_url}")
            else:
                logger.error("❌ [BRAND UPDATE] Logo upload failed, URL is None")
        else:
            logger.info("ℹ️ [BRAND UPDATE] No new logo provided, keeping existing")
        
        # Call parent to update the model
        logger.info("💾 [BRAND UPDATE] Calling parent update_model to save to DB")
        result = await super().update_model(request, pk, data)
        
        if result:
            logger.info(f"✅ [BRAND UPDATE] SUCCESS - Brand updated with ID: {result.id}")
            logger.info(f"🖼️ [BRAND UPDATE] Final logo_url in DB: {result.logo_url}")
        else:
            logger.error("❌ [BRAND UPDATE] Failed to update brand")
        
        return result
