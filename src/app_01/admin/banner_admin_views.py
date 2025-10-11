"""
Banner Management Admin Views
SQLAdmin interface for managing homepage banners
"""

from sqladmin import ModelView
from starlette.requests import Request
from ..models.banners.banner import Banner, BannerType
from .widgets import ImageUploadField


class BannerAdmin(ModelView, model=Banner):
    """
    Enhanced Banner Management Interface
    
    Features:
    - Image upload with Pillow processing
    - Banner type management (hero, promo, category)
    - Scheduling support
    - Display order control
    - CTA (Call-to-Action) configuration
    """
    
    name = "Баннеры"
    name_plural = "Баннеры"
    icon = "fa-solid fa-rectangle-ad"
    category = "🎨 Контент"
    
    column_list = [
        "id", "title", "banner_type", "is_active", 
        "display_order", "start_date", "end_date"
    ]
    
    column_details_list = [
        "id", "title", "subtitle", "description", "image_url", "mobile_image_url",
        "banner_type", "cta_text", "cta_url", "is_active", "display_order",
        "start_date", "end_date", "created_at", "updated_at"
    ]
    
    form_columns = [
        "title", "subtitle", "description", "image_url", "mobile_image_url",
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
        "image_url": "Изображение (десктоп)",
        "mobile_image_url": "Изображение (мобильное)",
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
    form_columns_labels = {
        "title": "Заголовок баннера",
        "subtitle": "Подзаголовок (опционально)",
        "description": "Полное описание (опционально)",
        "image_url": "Изображение баннера (десктоп)",
        "mobile_image_url": "Изображение для мобильных устройств (опционально)",
        "banner_type": "Тип баннера",
        "cta_text": "Текст кнопки призыва (опционально)",
        "cta_url": "URL кнопки призыва (опционально)",
        "is_active": "Показывать на главной странице",
        "display_order": "Порядок отображения (0 = первый)",
        "start_date": "Начать показ с (опционально)",
        "end_date": "Закончить показ (опционально)"
    }
    
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
            f'<img src="{m.image_url}" style="max-width: 100px; max-height: 50px; border-radius: 4px;">' 
            if m.image_url else "-"
        )
    }
    
    column_descriptions = {
        "title": "Основной заголовок баннера (отображается крупным шрифтом)",
        "subtitle": "Дополнительный текст под заголовком",
        "image_url": "Изображение баннера для десктопа (рекомендуемый размер: 1920x600px)",
        "mobile_image_url": "Оптимизированное изображение для мобильных устройств (рекомендуемый размер: 800x1200px)",
        "banner_type": "Hero - главный баннер, Promo - акционный, Category - категория товаров",
        "cta_text": "Текст на кнопке (например: 'Купить сейчас', 'Узнать больше')",
        "cta_url": "Ссылка при клике на баннер или кнопку",
        "display_order": "Порядок показа (меньшее число = выше)",
        "start_date": "Баннер начнет показываться с этой даты",
        "end_date": "Баннер перестанет показываться после этой даты"
    }
    
    # Image upload fields
    form_overrides = {
        "image_url": ImageUploadField,
        "mobile_image_url": ImageUploadField
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    can_export = True
    
    page_size = 20
    page_size_options = [10, 20, 50]

