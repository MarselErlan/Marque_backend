from sqladmin import ModelView
from starlette.requests import Request
from ..models import (
    ProductFilter, ProductSeason, ProductMaterial, ProductStyle, 
    ProductDiscount, ProductSearch
)
from .multi_market_admin_views import MarketAwareModelView

class ProductFilterAdmin(MarketAwareModelView, model=ProductFilter):
    """Product filter options management"""
    
    name = "Фильтры товаров"
    name_plural = "Фильтры товаров"
    icon = "fa-solid fa-filter"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "filter_type", "filter_value", "display_name", "usage_count", "sort_order", "is_active"
    ]
    column_details_list = [
        "id", "filter_type", "filter_value", "display_name", "usage_count", 
        "sort_order", "is_active", "created_at", "updated_at"
    ]
    
    form_columns = [
        "filter_type", "filter_value", "display_name", "sort_order", "is_active"
    ]
    
    column_searchable_list = ["filter_type", "filter_value", "display_name"]
    column_sortable_list = ["id", "filter_type", "usage_count", "sort_order", "is_active", "created_at"]
    column_filters = ["filter_type", "is_active"]
    
    column_labels = {
        "id": "ID",
        "filter_type": "Тип фильтра",
        "filter_value": "Значение",
        "display_name": "Отображаемое имя",
        "usage_count": "Использований",
        "sort_order": "Порядок",
        "is_active": "Активен",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_label = "Фильтр товара"
    form_columns_labels = {
        "filter_type": "Тип фильтра (size, color, brand, season, material, style)",
        "filter_value": "Значение фильтра",
        "display_name": "Отображаемое имя для пользователей",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductSeasonAdmin(MarketAwareModelView, model=ProductSeason):
    """Product seasons management"""
    
    name = "Сезоны"
    name_plural = "Сезоны"
    icon = "fa-solid fa-calendar"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "name", "slug", "product_count", "is_active", "is_featured", "sort_order"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "product_count", "is_active", 
        "is_featured", "sort_order", "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "product_count", "is_active", "is_featured", "sort_order", "created_at"]
    column_filters = ["is_active", "is_featured"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "product_count": "Товаров",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_label = "Сезон"
    form_columns_labels = {
        "name": "Название сезона (Лето, Зима, Мульти)",
        "slug": "URL-адрес (summer, winter, multi)",
        "description": "Описание сезона",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductMaterialAdmin(MarketAwareModelView, model=ProductMaterial):
    """Product materials management"""
    
    name = "Материалы"
    name_plural = "Материалы"
    icon = "fa-solid fa-cut"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "name", "slug", "product_count", "is_active", "is_featured", "sort_order"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "product_count", "is_active", 
        "is_featured", "sort_order", "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "product_count", "is_active", "is_featured", "sort_order", "created_at"]
    column_filters = ["is_active", "is_featured"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "product_count": "Товаров",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_label = "Материал"
    form_columns_labels = {
        "name": "Название материала (Хлопок, Полиэстер, Шерсть)",
        "slug": "URL-адрес (cotton, polyester, wool)",
        "description": "Описание материала",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductStyleAdmin(MarketAwareModelView, model=ProductStyle):
    """Product styles management"""
    
    name = "Стили"
    name_plural = "Стили"
    icon = "fa-solid fa-palette"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "name", "slug", "product_count", "is_active", "is_featured", "sort_order"
    ]
    column_details_list = [
        "id", "name", "slug", "description", "product_count", "is_active", 
        "is_featured", "sort_order", "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = ["id", "name", "product_count", "is_active", "is_featured", "sort_order", "created_at"]
    column_filters = ["is_active", "is_featured"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL-адрес",
        "description": "Описание",
        "product_count": "Товаров",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_label = "Стиль"
    form_columns_labels = {
        "name": "Название стиля (Спортивный, Классический, Повседневный)",
        "slug": "URL-адрес (sport, classic, casual)",
        "description": "Описание стиля",
        "sort_order": "Порядок сортировки",
        "is_active": "Активен"
    }


class ProductDiscountAdmin(MarketAwareModelView, model=ProductDiscount):
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


class ProductSearchAdmin(MarketAwareModelView, model=ProductSearch):
    """Product search analytics"""
    
    name = "Поиск товаров"
    name_plural = "Поиск товаров"
    icon = "fa-solid fa-search"
    category = "📊 Аналитика"
    
    column_list = [
        "id", "search_term", "search_count", "result_count", "last_searched"
    ]
    column_details_list = [
        "id", "search_term", "search_count", "result_count", "last_searched", "created_at"
    ]
    
    # Read-only view for analytics
    can_create = False
    can_edit = False
    can_delete = True
    
    column_searchable_list = ["search_term"]
    column_sortable_list = ["id", "search_term", "search_count", "result_count", "last_searched", "created_at"]
    column_filters = ["search_term"]
    column_default_sort = ("search_count", True)  # Sort by most popular
    
    column_labels = {
        "id": "ID",
        "search_term": "Поисковый запрос",
        "search_count": "Количество поисков",
        "result_count": "Результатов",
        "last_searched": "Последний поиск",
        "created_at": "Создан"
    }
    
    form_label = "Поисковый запрос"
