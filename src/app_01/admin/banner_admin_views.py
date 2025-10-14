"""
Banner Management Admin Views
SQLAdmin interface for managing homepage banners
"""

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField

from ..models.banners.banner import Banner, BannerType


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

