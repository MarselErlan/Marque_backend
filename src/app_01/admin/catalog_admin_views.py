from sqladmin import ModelView
from starlette.requests import Request
from ..models import Category, Subcategory, Brand

class CategoryAdmin(ModelView, model=Category):
    """
    Enhanced Category Management Interface
    
    Features:
    - Image upload support
    - Subcategory count display
    - Product count display
    - Visual indicators
    """
    
    name = "Категории"
    name_plural = "Категории"
    icon = "fa-solid fa-folder-tree"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "name", "slug", "subcategory_count", "product_count", "is_active"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "icon", "image_url", 
        "sort_order", "is_active", "created_at", "updated_at", "subcategories"
    ]
    
    form_columns = [
        "name", "slug", "description", "icon", "image_url", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "icon": "Иконка",
        "image_url": "Изображение",
        "sort_order": "Порядок",
        "is_active": "Активна",
        "created_at": "Создана",
        "updated_at": "Обновлена",
        "subcategories": "Подкатегории",
        "subcategory_count": "Подкатегорий",
        "product_count": "Товаров"
    }
    
    form_label = "Категория"
    form_columns_labels = {
        "name": "Название категории",
        "slug": "URL-адрес (slug)",
        "description": "Описание категории",
        "icon": "Иконка (FontAwesome класс)",
        "image_url": "URL изображения категории",
        "sort_order": "Порядок сортировки",
        "is_active": "Активна"
    }
    
    # Custom formatters for better display
    column_formatters = {
        "subcategory_count": lambda model, _: (
            f'<span class="badge badge-info">{len(model.subcategories)}</span>'
        ),
        "product_count": lambda model, _: (
            f'<span class="badge badge-success">{model.product_count}</span>'
        ),
        "is_active": lambda model, _: (
            '<span class="badge badge-success">✅ Активна</span>' if model.is_active 
            else '<span class="badge badge-secondary">⏸️ Неактивна</span>'
        ),
        "image_url": lambda model, _: (
            f'<img src="{model.image_url}" style="max-width: 50px; max-height: 50px; border-radius: 4px;">' 
            if model.image_url else "-"
        )
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True
    
    page_size = 50
    page_size_options = [25, 50, 100]
    
    column_descriptions = {
        "image_url": "URL изображения/логотипа для категории (рекомендуемый размер: 200x200px)",
        "subcategory_count": "Количество подкатегорий в этой категории",
        "product_count": "Общее количество товаров в этой категории"
    }


class SubcategoryAdmin(ModelView, model=Subcategory):
    """
    Enhanced Subcategory Management Interface
    
    Features:
    - Image upload support
    - Parent category display
    - Product count display
    - Visual indicators
    """
    
    name = "Подкатегории"
    name_plural = "Подкатегории"
    icon = "fa-solid fa-layer-group"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "category", "name", "slug", "product_count", "is_active"
    ]
    column_details_list = [
        "id", "category_id", "category", "name", "slug", "description", 
        "image_url", "sort_order", "is_active", "created_at", "updated_at", "products"
    ]
    
    form_columns = [
        "category_id", "name", "slug", "description", "image_url", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active", "category_id"]
    
    column_labels = {
        "id": "ID",
        "category": "Категория",
        "category_id": "Категория",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "image_url": "Изображение",
        "sort_order": "Порядок",
        "is_active": "Активна",
        "created_at": "Создана",
        "updated_at": "Обновлена",
        "products": "Товары",
        "product_count": "Товаров"
    }
    
    form_label = "Подкатегория"
    form_columns_labels = {
        "category_id": "Родительская категория",
        "name": "Название подкатегории",
        "slug": "URL-адрес (slug)",
        "description": "Описание подкатегории",
        "image_url": "URL изображения подкатегории",
        "sort_order": "Порядок сортировки",
        "is_active": "Активна"
    }
    
    # Custom formatters for better display
    column_formatters = {
        "category": lambda model, _: (
            f'<span class="badge badge-primary">{model.category.name}</span>' 
            if model.category else "-"
        ),
        "product_count": lambda model, _: (
            f'<span class="badge badge-success">{model.product_count}</span>'
        ),
        "is_active": lambda model, _: (
            '<span class="badge badge-success">✅ Активна</span>' if model.is_active 
            else '<span class="badge badge-secondary">⏸️ Неактивна</span>'
        ),
        "image_url": lambda model, _: (
            f'<img src="{model.image_url}" style="max-width: 50px; max-height: 50px; border-radius: 4px;">' 
            if model.image_url else "-"
        )
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_export = True
    
    page_size = 50
    page_size_options = [25, 50, 100]
    
    column_descriptions = {
        "category_id": "Выберите родительскую категорию (например: Мужчинам, Женщинам)",
        "image_url": "URL изображения для подкатегории (рекомендуемый размер: 200x200px)",
        "product_count": "Количество товаров в этой подкатегории"
    }


class BrandAdmin(ModelView, model=Brand):
    """Brand management interface"""
    
    name = "Бренды"
    name_plural = "Бренды"
    icon = "fa-solid fa-tags"
    
    column_list = [
        "id", "name", "slug", "country", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "logo_url", "website_url", "country", "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "logo_url", "website_url", "country", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description", "country"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active", "country"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "logo_url": "URL логотипа",
        "website_url": "URL сайта",
        "country": "Страна",
        "sort_order": "Порядок",
        "is_active": "Активен",
        "created_at": "Создан"
    }
    
    form_label = "Бренд"
    form_columns_labels = {
        "name": "Название бренда",
        "slug": "URL-адрес (slug)",
        "description": "Описание бренда",
        "logo_url": "URL логотипа бренда",
        "website_url": "URL официального сайта",
        "country": "Страна происхождения",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }
