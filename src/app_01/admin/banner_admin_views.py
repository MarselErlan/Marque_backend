"""
Banner Management Admin Views
SQLAdmin interface for managing homepage banners
"""

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField
from wtforms.validators import Optional as OptionalValidator
from PIL import Image
import io
import logging

from ..models.banners.banner import Banner, BannerType
from ..utils.image_upload import image_uploader
from fastapi import UploadFile

logger = logging.getLogger(__name__)


class BannerAdmin(ModelView, model=Banner):
    """
    Enhanced Banner Management Interface, now with standardized image uploads.
    """
    
    name = "Баннеры"
    name_plural = "Баннеры"
    icon = "fa-solid fa-rectangle-ad"
    category = "🎨 Контент"
    
    column_list = [
        "id", "image_url", "title", "banner_type", "is_active", 
        "display_order", "start_date", "end_date"
    ]
    
    column_details_list = [
        "id", "title", "subtitle", "description", "image_url", "mobile_image_url",
        "banner_type", "cta_text", "cta_url", "is_active", "display_order",
        "start_date", "end_date", "created_at", "updated_at",
    ]

    form_columns = [
        "title", "subtitle", "description",
        "banner_type", "cta_text", "cta_url", "is_active", "display_order",
        "start_date", "end_date"
    ]

    column_searchable_list = ["title", "subtitle", "description"]
    column_sortable_list = ["id", "title", "display_order", "banner_type", "created_at"]
    column_filters = ["is_active", "banner_type"]

    column_labels = {
        "id": "ID", "title": "Заголовок", "subtitle": "Подзаголовок", 
        "description": "Описание", "image_url": "Фото (десктоп)",
        "mobile_image_url": "Фото (моб.)", "banner_type": "Тип",
        "cta_text": "Текст кнопки", "cta_url": "URL кнопки",
        "is_active": "Активен", "display_order": "Порядок",
        "start_date": "Начало показа", "end_date": "Конец показа",
        "created_at": "Создан", "updated_at": "Обновлен"
    }

    form_label = "Баннер"

    column_formatters = {
        "is_active": lambda m, _: '<span class="badge badge-success">✅</span>' if m.is_active else '<span class="badge badge-secondary">❌</span>',
        "image_url": lambda m, _: f'<img src="{m.image_url}" style="height: 40px;">' if m.image_url else "-",
        "mobile_image_url": lambda m, _: f'<img src="{m.mobile_image_url}" style="height: 40px;">' if m.mobile_image_url else "-",
    }
    
    page_size = 20
    page_size_options = [10, 20, 50]

    async def scaffold_form(self):
        """Override to add image upload fields programmatically"""
        form_class = await super().scaffold_form()
        
        # Add desktop image upload field
        form_class.image_url = FileField(
            "Баннер (Десктоп)",
            validators=[OptionalValidator()],
            description="Загрузите баннер для десктопа (JPEG/PNG, рекомендуется 1920x600)"
        )
        
        # Add mobile image upload field
        form_class.mobile_image_url = FileField(
            "Баннер (Мобильный)",
            validators=[OptionalValidator()],
            description="Загрузите баннер для мобильных устройств (JPEG/PNG, рекомендуется 800x600)"
        )
        
        return form_class

    async def _save_image(self, file_data, image_type="desktop"):
        logger.info(f"🔍 [BANNER {image_type.upper()}] Starting _save_image method")
        
        if not file_data:
            logger.warning(f"⚠️ [BANNER {image_type.upper()}] No file_data provided")
            return None
            
        if not hasattr(file_data, "filename"):
            logger.warning(f"⚠️ [BANNER {image_type.upper()}] file_data has no filename attribute")
            return None
            
        if not file_data.filename:
            logger.warning(f"⚠️ [BANNER {image_type.upper()}] filename is empty")
            return None
            
        logger.info(f"📁 [BANNER {image_type.upper()}] Processing file: {file_data.filename}")
        
        try:
            # Re-read file bytes for processing
            await file_data.seek(0)
            file_bytes = await file_data.read()
            logger.info(f"📊 [BANNER {image_type.upper()}] Read {len(file_bytes)} bytes from uploaded file")
            
            # Validate with Pillow
            img = Image.open(io.BytesIO(file_bytes))
            img.verify()
            logger.info(f"✅ [BANNER {image_type.upper()}] Pillow validation passed - Image format: {img.format}")
            
            upload_file = UploadFile(filename=file_data.filename, file=io.BytesIO(file_bytes))
            
            logger.info(f"💾 [BANNER {image_type.upper()}] Calling image_uploader.save_image...")
            url = await image_uploader.save_image(
                file=upload_file, category="banner"
            )
            logger.info(f"✅ [BANNER {image_type.upper()}] Image uploaded successfully to: {url}")
            return url
        except Exception as e:
            logger.error(f"❌ [BANNER {image_type.upper()}] Failed to save image: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"📋 [BANNER {image_type.upper()}] Traceback: {traceback.format_exc()}")
            return None

    async def insert_model(self, request: Request, data: dict) -> any:
        """Handle image uploads when creating a new banner."""
        logger.info("🆕 [BANNER INSERT] Starting insert_model")
        logger.info(f"📦 [BANNER INSERT] Data keys received: {list(data.keys())}")
        
        # Extract desktop image file
        desktop_file = data.pop("image_url", None)
        logger.info(f"🖼️ [BANNER INSERT] Extracted desktop image_file: {desktop_file}")
        
        # Extract mobile image file
        mobile_file = data.pop("mobile_image_url", None)
        logger.info(f"📱 [BANNER INSERT] Extracted mobile image_file: {mobile_file}")
        
        # Save desktop image if provided
        if desktop_file and hasattr(desktop_file, "filename") and desktop_file.filename:
            logger.info(f"📤 [BANNER INSERT] Uploading desktop image: {desktop_file.filename}")
            desktop_url = await self._save_image(desktop_file, "desktop")
            if desktop_url:
                data["image_url"] = desktop_url
                logger.info(f"✅ [BANNER INSERT] Desktop image URL set: {desktop_url}")
            else:
                logger.error("❌ [BANNER INSERT] Desktop image upload failed")
        else:
            logger.info("ℹ️ [BANNER INSERT] No desktop image provided")
        
        # Save mobile image if provided
        if mobile_file and hasattr(mobile_file, "filename") and mobile_file.filename:
            logger.info(f"📤 [BANNER INSERT] Uploading mobile image: {mobile_file.filename}")
            mobile_url = await self._save_image(mobile_file, "mobile")
            if mobile_url:
                data["mobile_image_url"] = mobile_url
                logger.info(f"✅ [BANNER INSERT] Mobile image URL set: {mobile_url}")
            else:
                logger.error("❌ [BANNER INSERT] Mobile image upload failed")
        else:
            logger.info("ℹ️ [BANNER INSERT] No mobile image provided")
        
        # Call parent to create the model
        logger.info("💾 [BANNER INSERT] Calling parent insert_model to save to DB")
        result = await super().insert_model(request, data)
        
        if result:
            logger.info(f"✅ [BANNER INSERT] SUCCESS - Banner created with ID: {result.id}")
            logger.info(f"🖼️ [BANNER INSERT] Desktop image in DB: {result.image_url}")
            logger.info(f"📱 [BANNER INSERT] Mobile image in DB: {result.mobile_image_url}")
        else:
            logger.error("❌ [BANNER INSERT] Failed to create banner")
        
        return result

    async def update_model(self, request: Request, pk: str, data: dict) -> any:
        """Handle image uploads when updating a banner."""
        logger.info(f"🔄 [BANNER UPDATE] Starting update_model for ID: {pk}")
        logger.info(f"📦 [BANNER UPDATE] Data keys received: {list(data.keys())}")
        
        # Extract desktop image file
        desktop_file = data.pop("image_url", None)
        logger.info(f"🖼️ [BANNER UPDATE] Extracted desktop image_file: {desktop_file}")
        
        # Extract mobile image file
        mobile_file = data.pop("mobile_image_url", None)
        logger.info(f"📱 [BANNER UPDATE] Extracted mobile image_file: {mobile_file}")
        
        # Save desktop image if provided
        if desktop_file and hasattr(desktop_file, "filename") and desktop_file.filename:
            logger.info(f"📤 [BANNER UPDATE] Uploading new desktop image: {desktop_file.filename}")
            desktop_url = await self._save_image(desktop_file, "desktop")
            if desktop_url:
                data["image_url"] = desktop_url
                logger.info(f"✅ [BANNER UPDATE] Desktop image URL set: {desktop_url}")
            else:
                logger.error("❌ [BANNER UPDATE] Desktop image upload failed")
        else:
            logger.info("ℹ️ [BANNER UPDATE] No new desktop image, keeping existing")
        
        # Save mobile image if provided
        if mobile_file and hasattr(mobile_file, "filename") and mobile_file.filename:
            logger.info(f"📤 [BANNER UPDATE] Uploading new mobile image: {mobile_file.filename}")
            mobile_url = await self._save_image(mobile_file, "mobile")
            if mobile_url:
                data["mobile_image_url"] = mobile_url
                logger.info(f"✅ [BANNER UPDATE] Mobile image URL set: {mobile_url}")
            else:
                logger.error("❌ [BANNER UPDATE] Mobile image upload failed")
        else:
            logger.info("ℹ️ [BANNER UPDATE] No new mobile image, keeping existing")
        
        # Call parent to update the model
        logger.info("💾 [BANNER UPDATE] Calling parent update_model to save to DB")
        result = await super().update_model(request, pk, data)
        
        if result:
            logger.info(f"✅ [BANNER UPDATE] SUCCESS - Banner updated with ID: {result.id}")
            logger.info(f"🖼️ [BANNER UPDATE] Desktop image in DB: {result.image_url}")
            logger.info(f"📱 [BANNER UPDATE] Mobile image in DB: {result.mobile_image_url}")
        else:
            logger.error("❌ [BANNER UPDATE] Failed to update banner")
        
        return result

