from sqladmin import ModelView
from starlette.requests import Request
from ..models import (
    ProductFilter, ProductSeason, ProductMaterial, ProductStyle, 
    ProductDiscount, ProductSearch
)

class ProductFilterAdmin(ModelView, model=ProductFilter):
    """Product filter options management"""
    
    name = "Фильтры товаров"
    name_plural = "Фильтры товаров"
    icon = "fa-solid fa-filter"
    
    column_list = [
        "id", "filter_type", "filter_value", "display_name", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "filter_type", "filter_value", "display_name", "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "filter_type", "filter_value", "display_name", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["filter_type", "filter_value", "display_name"]
    column_sortable_list = ["id", "filter_type", "sort_order", "is_active", "created_at"]
    column_filters = ["filter_type", "is_active"]
    
    column_labels = {
        "id": "ID",
        "filter_type": "Тип фильтра",
        "filter_value": "Значение",
        "display_name": "Отображаемое имя",
        "sort_order": "Порядок",
        "is_active": "Активен",
        "created_at": "Создан"
    }
    
    form_label = "Фильтр товара"
    form_columns_labels = {
        "filter_type": "Тип фильтра (size, color, brand, season, material, style)",
        "filter_value": "Значение фильтра",
        "display_name": "Отображаемое имя для пользователей",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductSeasonAdmin(ModelView, model=ProductSeason):
    """Product seasons management"""
    
    name = "Сезоны"
    name_plural = "Сезоны"
    icon = "fa-solid fa-calendar"
    
    column_list = [
        "id", "name", "slug", "description", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "sort_order": "Порядок",
        "is_active": "Активен",
        "created_at": "Создан"
    }
    
    form_label = "Сезон"
    form_columns_labels = {
        "name": "Название сезона (Лето, Зима, Мульти)",
        "slug": "URL-адрес (summer, winter, multi)",
        "description": "Описание сезона",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductMaterialAdmin(ModelView, model=ProductMaterial):
    """Product materials management"""
    
    name = "Материалы"
    name_plural = "Материалы"
    icon = "fa-solid fa-cut"
    
    column_list = [
        "id", "name", "slug", "description", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "sort_order": "Порядок",
        "is_active": "Активен",
        "created_at": "Создан"
    }
    
    form_label = "Материал"
    form_columns_labels = {
        "name": "Название материала (Хлопок, Полиэстер, Шерсть)",
        "slug": "URL-адрес (cotton, polyester, wool)",
        "description": "Описание материала",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductStyleAdmin(ModelView, model=ProductStyle):
    """Product styles management"""
    
    name = "Стили"
    name_plural = "Стили"
    icon = "fa-solid fa-palette"
    
    column_list = [
        "id", "name", "slug", "description", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "sort_order", "is_active", "created_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "sort_order", "is_active", "created_at"]
    column_filters = ["is_active"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "sort_order": "Порядок",
        "is_active": "Активен",
        "created_at": "Создан"
    }
    
    form_label = "Стиль"
    form_columns_labels = {
        "name": "Название стиля (Спортивный, Классический, Повседневный)",
        "slug": "URL-адрес (sport, classic, casual)",
        "description": "Описание стиля",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductDiscountAdmin(ModelView, model=ProductDiscount):
    """Product discounts management"""
    
    name = "Скидки"
    name_plural = "Скидки"
    icon = "fa-solid fa-percent"
    
    column_list = [
        "id", "product_id", "discount_type", "discount_value", "is_active", "start_date", "end_date"
    ]
    column_details_list = [
        "id", "product_id", "discount_type", "discount_value", "original_price", 
        "start_date", "end_date", "is_active", "created_at"
    ]
    
    form_columns = [
        "product_id", "discount_type", "discount_value", "original_price", 
        "start_date", "end_date", "is_active"
    ]
    
    column_searchable_list = ["discount_type"]
    column_sortable_list = ["id", "discount_value", "start_date", "end_date", "is_active", "created_at"]
    column_filters = ["discount_type", "is_active"]
    
    column_labels = {
        "id": "ID",
        "product_id": "ID товара",
        "discount_type": "Тип скидки",
        "discount_value": "Значение скидки",
        "original_price": "Оригинальная цена",
        "start_date": "Дата начала",
        "end_date": "Дата окончания",
        "is_active": "Активна",
        "created_at": "Создана"
    }
    
    form_label = "Скидка"
    form_columns_labels = {
        "product_id": "ID товара",
        "discount_type": "Тип скидки (percentage или fixed)",
        "discount_value": "Значение скидки (% или сумма в сомах)",
        "original_price": "Оригинальная цена товара",
        "start_date": "Дата начала действия скидки",
        "end_date": "Дата окончания действия скидки",
        "is_active": "Активна"
    }


class ProductSearchAdmin(ModelView, model=ProductSearch):
    """Product search analytics"""
    
    name = "Поиск товаров"
    name_plural = "Поиск товаров"
    icon = "fa-solid fa-search"
    
    column_list = [
        "id", "search_term", "search_count", "last_searched"
    ]
    column_details_list = [
        "id", "search_term", "search_count", "last_searched", "created_at"
    ]
    
    # Read-only view for analytics
    can_create = False
    can_edit = False
    can_delete = True
    
    column_searchable_list = ["search_term"]
    column_sortable_list = ["id", "search_term", "search_count", "last_searched", "created_at"]
    column_filters = ["search_term"]
    
    column_labels = {
        "id": "ID",
        "search_term": "Поисковый запрос",
        "search_count": "Количество поисков",
        "last_searched": "Последний поиск",
        "created_at": "Создан"
    }
    
    form_label = "Поисковый запрос"
