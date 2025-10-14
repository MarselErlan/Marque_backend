from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField
from wtforms.validators import Optional as OptionalValidator

from ..models import Category, Subcategory, Brand
from .image_upload_mixin import ImageUploadMixin


class CategoryAdmin(ImageUploadMixin, ModelView, model=Category):
    """Enhanced Category Management Interface"""
    
    name = "Категории"
    name_plural = "Категории"
    icon = "fa-solid fa-folder-tree"
    category = "🛍️ Каталог"
    
    image_fields = ["image_url"]

    column_list = [
        "id", "image_url", "name", "slug", "icon", "is_active", "sort_order"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "icon", "image_url", 
        "sort_order", "is_active", "created_at", "updated_at", "subcategories"
    ]
    
    form_columns = [
        "name", "slug", "description", "icon", "sort_order", "is_active"
    ]

    form_extra_fields = {
        "image_url": FileField("Изображение", validators=[OptionalValidator()])
    }
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active"]
    
    column_labels = {
        "id": "ID", "name": "Название", "slug": "URL-адрес", "description": "Описание",
        "icon": "Иконка", "image_url": "Фото", "sort_order": "Порядок",
        "is_active": "Активна", "created_at": "Создана", "updated_at": "Обновлена",
        "subcategories": "Подкатегории"
    }
    
    form_label = "Категория"
    
    column_formatters = {
        "is_active": lambda m, _: '<span class="badge badge-success">✅</span>' if m.is_active else '<span class="badge badge-secondary">❌</span>',
        "image_url": lambda m, _: f'<img src="{m.image_url}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 4px;">' if m.image_url else "-"
    }


class SubcategoryAdmin(ImageUploadMixin, ModelView, model=Subcategory):
    """Enhanced Subcategory Management Interface"""
    
    name = "Подкатегории"
    name_plural = "Подкатегории"
    icon = "fa-solid fa-layer-group"
    category = "🛍️ Каталог"

    image_fields = ["image_url"]
    
    column_list = [
        "id", "image_url", "category", "name", "slug", "is_active", "sort_order"
    ]
    column_details_list = [
        "id", "category", "name", "slug", "description", 
        "image_url", "sort_order", "is_active", "created_at", "updated_at", "products"
    ]
    
    form_columns = [
        "category", "name", "slug", "description", "sort_order", "is_active"
    ]

    form_extra_fields = {
        "image_url": FileField("Изображение", validators=[OptionalValidator()])
    }
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active", "category"]
    
    column_labels = {
        "id": "ID", "category": "Категория", "name": "Название", "slug": "URL-адрес",
        "description": "Описание", "image_url": "Фото", "sort_order": "Порядок",
        "is_active": "Активна", "created_at": "Создана", "updated_at": "Обновлена",
        "products": "Товары"
    }
    
    form_label = "Подкатегория"
    
    column_formatters = {
        "is_active": lambda m, _: '<span class="badge badge-success">✅</span>' if m.is_active else '<span class="badge badge-secondary">❌</span>',
        "image_url": lambda m, _: f'<img src="{m.image_url}" style="height: 40px; width: 40px; object-fit: cover; border-radius: 4px;">' if m.image_url else "-",
        "category": lambda m, a: m.category.name if m.category else "-"
    }


class BrandAdmin(ImageUploadMixin, ModelView, model=Brand):
    """Brand management interface"""
    
    name = "Бренды"
    name_plural = "Бренды"
    icon = "fa-solid fa-tags"
    category = "🛍️ Каталог"

    image_fields = ["logo_url"]
    
    column_list = [
        "id", "logo_url", "name", "slug", "country", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "logo_url", "website_url", "country", "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "website_url", "country", "sort_order", "is_active"
    ]

    form_extra_fields = {
        "logo_url": FileField("Логотип", validators=[OptionalValidator()])
    }

    column_searchable_list = ["name", "slug", "description", "country"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active", "country"]
    
    column_labels = {
        "id": "ID", "name": "Название", "slug": "URL-адрес", "description": "Описание",
        "logo_url": "Лого", "website_url": "URL сайта", "country": "Страна",
        "sort_order": "Порядок", "is_active": "Активен", "created_at": "Создан"
    }
    
    form_label = "Бренд"

    column_formatters = {
        "is_active": lambda m, _: '<span class="badge badge-success">✅</span>' if m.is_active else '<span class="badge badge-secondary">❌</span>',
        "logo_url": lambda m, _: f'<img src="{m.logo_url}" style="height: 40px; width: 40px; object-fit: contain; border-radius: 4px;">' if m.logo_url else "-"
    }
