"""
Banner Management Admin Views
SQLAdmin interface for managing homepage banners
"""

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField, MultipleFileField
from wtforms.validators import Optional as OptionalValidator

from ..models.banners.banner import Banner, BannerType
from .image_upload_mixin import ImageUploadMixin


class BannerAdmin(ImageUploadMixin, ModelView, model=Banner):
    """
    Enhanced Banner Management Interface, now with standardized image uploads.
    """
    
    name = "Баннеры"
    name_plural = "Баннеры"
    icon = "fa-solid fa-rectangle-ad"
    category = "🎨 Контент"

    # Image Upload Configuration
    image_fields = ["image_url", "mobile_image_url"]
    
    column_list = [
        "id", "image_url", "title", "banner_type", "is_active", 
        "display_order", "start_date", "end_date"
    ]
    
    column_details_list = [
        "id", "title", "subtitle", "description", "image_url", "mobile_image_url",
        "banner_type", "cta_text", "cta_url", "is_active", "display_order",
        "start_date", "end_date", "created_at", "updated_at"
    ]
    
    form_columns = [
        "title", "subtitle", "description",
        "banner_type", "cta_text", "cta_url", "is_active", "display_order",
        "start_date", "end_date"
    ]

    column_searchable_list = ["title", "subtitle", "description"]
    column_sortable_list = ["id", "title", "display_order", "banner_type", "created_at"]
    column_filters = ["banner_type", "is_active"]
    column_default_sort = [("display_order", False), ("created_at", True)]
    
    column_labels = {
        "id": "ID",
        "title": "Заголовок",
        "subtitle": "Подзаголовок",
        "description": "Описание",
        "image_url": "Фото (PC)",
        "mobile_image_url": "Фото (моб.)",
        "banner_type": "Тип баннера",
        "cta_text": "Текст кнопки",
        "cta_url": "Ссылка кнопки",
        "is_active": "Активен",
        "display_order": "Порядок",
        "start_date": "Начало показа",
        "end_date": "Конец показа",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_label = "Баннер"
    
    column_formatters = {
        "is_active": lambda m, _: (
            '<span class="badge badge-success">✅ Активен</span>' if m.is_active 
            else '<span class="badge badge-secondary">❌ Неактивен</span>'
        ),
        "banner_type": lambda m, _: {
            BannerType.HERO: '<span class="badge badge-primary">🎬 Hero</span>',
            BannerType.PROMO: '<span class="badge badge-warning">🏷️ Promo</span>',
            BannerType.CATEGORY: '<span class="badge badge-info">📂 Category</span>'
        }.get(m.banner_type, str(m.banner_type)),
        "image_url": lambda m, _: (
            f'<img src="{m.image_url}" style="width: 120px; height: 50px; object-fit: cover; border-radius: 4px;">' 
            if m.image_url else "-"
        ),
        "mobile_image_url": lambda m, _: (
            f'<img src="{m.mobile_image_url}" style="width: 50px; height: 80px; object-fit: cover; border-radius: 4px;">' 
            if m.mobile_image_url else "-"
        ),
    }
    
    page_size = 20
    page_size_options = [10, 20, 50]

