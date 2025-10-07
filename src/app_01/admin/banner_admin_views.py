"""
Banner Management Admin Views
SQLAdmin interface for managing homepage banners
"""

from sqladmin import ModelView
from starlette.requests import Request

from ..models.banners.banner import Banner, BannerType


class BannerAdmin(ModelView, model=Banner):
    """Banner management interface for homepage promotions"""
    
    # Display settings
    name = "Баннеры"
    name_plural = "Баннеры"
    icon = "fa-solid fa-image"
    
    # Column configuration
    column_list = [
        "id", "title", "banner_type", "is_active", 
        "display_order", "start_date", "end_date"
    ]
    
    column_details_list = [
        "id", "title", "description", "image_url", "banner_type",
        "link_url", "is_active", "display_order",
        "start_date", "end_date", "created_at", "updated_at"
    ]
    
    # Form configuration
    form_columns = [
        "title", "description", "image_url", "banner_type",
        "link_url", "is_active", "display_order",
        "start_date", "end_date"
    ]
    
    # Search and filters
    column_searchable_list = ["title", "description"]
    column_sortable_list = ["id", "title", "display_order", "created_at"]
    column_filters = ["banner_type", "is_active", "start_date", "end_date"]
    
    # Default sorting (by display order)
    column_default_sort = [("display_order", False)]
    
    # Column labels (Russian)
    column_labels = {
        "id": "ID",
        "title": "Заголовок",
        "description": "Описание",
        "image_url": "URL изображения",
        "banner_type": "Тип баннера",
        "link_url": "Ссылка",
        "is_active": "Активен",
        "display_order": "Порядок отображения",
        "start_date": "Дата начала",
        "end_date": "Дата окончания",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    # Form labels
    form_label = "Баннер"
    form_columns_labels = {
        "title": "Заголовок баннера",
        "description": "Описание (опционально)",
        "image_url": "URL изображения баннера",
        "banner_type": "Тип (sale/model)",
        "link_url": "Ссылка при клике (опционально)",
        "is_active": "Показывать на сайте",
        "display_order": "Порядок (0 = первый)",
        "start_date": "Начать показ (опционально)",
        "end_date": "Закончить показ (опционально)"
    }
    
    # Custom formatting
    column_formatters = {
        "image_url": lambda model, _: f"...{model.image_url[-50:]}" if len(model.image_url) > 50 else model.image_url,
        "banner_type": lambda model, _: "Акция" if model.banner_type == BannerType.SALE else "Модель",
        "is_active": lambda model, _: "✅" if model.is_active else "❌"
    }
    
    # Permissions
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = False
    
    # Page size
    page_size = 25
    page_size_options = [10, 25, 50]
    
    # Help text
    form_widget_args = {
        "image_url": {
            "placeholder": "https://example.com/banner-image.jpg"
        },
        "link_url": {
            "placeholder": "https://example.com/products/sale"
        },
        "display_order": {
            "placeholder": "0 (первый), 1 (второй), и т.д."
        }
    }

