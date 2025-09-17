from sqladmin import ModelView
from starlette.requests import Request
from ..models import Category, Subcategory, Brand

class CategoryAdmin(ModelView, model=Category):
    """Category management interface"""
    
    name = "Категории"
    name_plural = "Категории"
    icon = "fa-solid fa-list"
    
    column_list = [
        "id", "name", "slug", "sort_order", "is_active", "created_at"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "icon", "sort_order", "is_active", "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "icon", "sort_order", "is_active"
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
        "sort_order": "Порядок",
        "is_active": "Активна",
        "created_at": "Создана",
        "updated_at": "Обновлена"
    }
    
    form_label = "Категория"
    form_columns_labels = {
        "name": "Название категории",
        "slug": "URL-адрес (slug)",
        "description": "Описание категории",
        "icon": "Иконка (FontAwesome класс)",
        "sort_order": "Порядок сортировки",
        "is_active": "Активна"
    }
    
    def can_create(self, request: Request) -> bool:
        return True
    
    def can_edit(self, request: Request) -> bool:
        return True
    
    def can_delete(self, request: Request) -> bool:
        return True


class SubcategoryAdmin(ModelView, model=Subcategory):
    """Subcategory management interface"""
    
    name = "Подкатегории"
    name_plural = "Подкатегории"
    icon = "fa-solid fa-list-ul"
    
    column_list = [
        "id", "category_id", "name", "slug", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "category_id", "name", "slug", "description", "image_url", "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "category_id", "name", "slug", "description", "image_url", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active", "category_id"]
    
    column_labels = {
        "id": "ID",
        "category_id": "ID категории",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "image_url": "URL изображения",
        "sort_order": "Порядок",
        "is_active": "Активна",
        "created_at": "Создана"
    }
    
    form_label = "Подкатегория"
    form_columns_labels = {
        "category_id": "ID родительской категории",
        "name": "Название подкатегории",
        "slug": "URL-адрес (slug)",
        "description": "Описание подкатегории",
        "image_url": "URL изображения подкатегории",
        "sort_order": "Порядок сортировки",
        "is_active": "Активна"
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
