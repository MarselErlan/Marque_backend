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
        if not (file_data and hasattr(file_data, "filename") and file_data.filename):
            return None
        try:
            # Re-read file bytes for processing
            await file_data.seek(0)
            file_bytes = await file_data.read()
            
            # Validate with Pillow
            Image.open(io.BytesIO(file_bytes)).verify()
            
            upload_file = UploadFile(filename=file_data.filename, file=io.BytesIO(file_bytes))
            
            url = await image_uploader.save_image(
                file=upload_file, category="subcategory"
            )
            logger.info(f"✅ Image uploaded successfully: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ Failed to save subcategory image: {e}")
            return None

    async def insert_model(self, request: Request, data: dict) -> any:
        """Handle image upload when creating a new subcategory."""
        # Extract image file before SQLAlchemy tries to process it
        image_file = data.pop("image_url", None)
        
        # Save the image if provided
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            image_url = await self._save_image(image_file)
            if image_url:
                data["image_url"] = image_url
        
        # Call parent to create the model
        return await super().insert_model(request, data)

    async def update_model(self, request: Request, pk: str, data: dict) -> any:
        """Handle image upload when updating a subcategory."""
        # Extract image file before SQLAlchemy tries to process it
        image_file = data.pop("image_url", None)
        
        # Save the image if provided
        if image_file and hasattr(image_file, "filename") and image_file.filename:
            image_url = await self._save_image(image_file)
            if image_url:
                data["image_url"] = image_url
        
        # Call parent to update the model
        return await super().update_model(request, pk, data)


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
