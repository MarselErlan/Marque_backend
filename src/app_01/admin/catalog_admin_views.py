from datetime import datetime
from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField
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
    
    form_extra_fields = {
        "image_url": FileField("Изображение", description="Загрузите фото для подкатегории")
    }

    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]

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
            return url
        except Exception as e:
            logger.error(f"Failed to save subcategory image: {e}")
            return None

    async def on_model_change(
        self, data: dict, model: any, is_created: bool, request: Request
    ) -> None:
        """
        Handle image upload after model is created/updated.
        """
        image_file = data.pop("image_url", None)

        if image_file and hasattr(image_file, "filename") and image_file.filename:
            image_url = await self._save_image(image_file)
            model.image_url = image_url

        await super().on_model_change(data, model, is_created, request)


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
