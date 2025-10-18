"""
Enhanced Admin Views for New Model Features

This file contains updated admin views for all enhanced models with new fields:
- Product (view_count, is_new, is_trending, SEO, analytics)
- Review (moderation, helpfulness, admin responses)
- ProductAsset (dimensions, primary image, file info)
- ProductAttribute (featured, usage tracking)
- Brand, Category, Subcategory (featured flags)
- ProductFilter, Season, Material, Style (popularity, featured)
- ProductSearch (result count)
"""

from sqladmin import ModelView
from starlette.requests import Request
from wtforms import FileField, MultipleFileField, TextAreaField, IntegerField, BooleanField
from wtforms.validators import Optional as OptionalValidator
from datetime import datetime
import logging

from ..models import (
    Product, Review, ProductAsset, ProductAttribute, Brand,
    Category, Subcategory, ProductFilter, ProductSeason,
    ProductMaterial, ProductStyle, ProductSearch
)

logger = logging.getLogger(__name__)


class EnhancedProductAdmin(ModelView, model=Product):
    """Enhanced Product Admin with all new fields"""
    
    name = "Товар"
    name_plural = "Товары"
    icon = "fa-solid fa-box"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "main_image", "title", "brand", "category",
        "is_active", "is_featured", "is_new", "is_trending",
        "view_count", "sold_count"
    ]
    
    column_details_list = [
        "id", "title", "slug", "description",
        "brand", "category", "subcategory",
        "season", "material", "style",
        # Status flags
        "is_active", "is_featured", "is_new", "is_trending",
        # Analytics
        "view_count", "sold_count", "rating_avg", "rating_count",
        # Stock
        "low_stock_threshold",
        # SEO
        "meta_title", "meta_description", "meta_keywords",
        # Additional
        "tags",
        # Dates
        "created_at", "updated_at",
        # Relations
        "main_image", "additional_images", "skus", "reviews"
    ]
    
    form_columns = [
        "title", "slug", "description",
        "brand", "category", "subcategory",
        "season", "material", "style",
        # Status flags
        "is_active", "is_featured", "is_new", "is_trending",
        # Stock settings
        "low_stock_threshold",
        # SEO fields
        "meta_title", "meta_description", "meta_keywords",
        # Additional
        "tags", "attributes"
    ]
    
    column_searchable_list = [
        "title", "description", "slug", "meta_title", "meta_description",
        "brand.name", "category.name", "subcategory.name"
    ]
    
    column_sortable_list = [
        "id", "title", "brand", "category", "is_active", "is_featured",
        "is_new", "is_trending", "view_count", "sold_count", "rating_avg",
        "created_at", "updated_at"
    ]
    
    column_filters = [
        "is_active", "is_featured", "is_new", "is_trending",
        "brand", "category", "subcategory",
        "season", "material", "style"
    ]
    
    column_labels = {
        "id": "ID",
        "title": "Название",
        "slug": "URL",
        "description": "Описание",
        "brand": "Бренд",
        "category": "Категория",
        "subcategory": "Подкатегория",
        "season": "Сезон",
        "material": "Материал",
        "style": "Стиль",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "is_new": "Новинка",
        "is_trending": "В тренде",
        "view_count": "Просмотры",
        "sold_count": "Продано",
        "rating_avg": "Рейтинг",
        "rating_count": "Кол-во отзывов",
        "low_stock_threshold": "Минимальный остаток",
        "meta_title": "SEO Заголовок",
        "meta_description": "SEO Описание",
        "meta_keywords": "SEO Ключевые слова",
        "tags": "Теги (JSON)",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "main_image": "Главное фото",
        "additional_images": "Доп. фото",
        "skus": "SKU (Размеры/Цвета)",
        "reviews": "Отзывы",
        "attributes": "Атрибуты (JSON)"
    }
    
    form_widget_args = {
        "meta_title": {"rows": 2},
        "meta_description": {"rows": 3},
        "meta_keywords": {"rows": 2},
        "tags": {"rows": 2},
        "description": {"rows": 5}
    }


class EnhancedReviewAdmin(ModelView, model=Review):
    """Enhanced Review Admin with moderation and helpfulness"""
    
    name = "Отзыв"
    name_plural = "Отзывы"
    icon = "fa-solid fa-star"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "product", "user", "rating",
        "is_approved", "is_featured", "is_verified_purchase",
        "helpful_count", "unhelpful_count", "created_at"
    ]
    
    column_details_list = [
        "id", "product", "user", "rating", "comment",
        "is_approved", "is_featured", "is_verified_purchase",
        "helpful_count", "unhelpful_count",
        "admin_response", "admin_response_date", "updated_at",
        "created_at"
    ]
    
    form_columns = [
        "product", "user", "rating", "comment",
        "is_approved", "is_featured", "is_verified_purchase",
        "admin_response"
    ]
    
    column_searchable_list = ["comment", "product.title", "user.full_name"]
    column_sortable_list = [
        "id", "rating", "is_approved", "is_featured", "helpful_count",
        "unhelpful_count", "created_at", "updated_at"
    ]
    column_filters = [
        "is_approved", "is_featured", "is_verified_purchase", "rating"
    ]
    
    column_labels = {
        "id": "ID",
        "product": "Товар",
        "user": "Пользователь",
        "rating": "Рейтинг",
        "comment": "Комментарий",
        "is_approved": "Одобрен",
        "is_featured": "В избранном",
        "is_verified_purchase": "Подтвержденная покупка",
        "helpful_count": "Полезно",
        "unhelpful_count": "Бесполезно",
        "admin_response": "Ответ администратора",
        "admin_response_date": "Дата ответа",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_widget_args = {
        "comment": {"rows": 5},
        "admin_response": {"rows": 4}
    }


class EnhancedProductAssetAdmin(ModelView, model=ProductAsset):
    """Enhanced Product Asset Admin with dimensions and status"""
    
    name = "Изображение товара"
    name_plural = "Изображения товаров"
    icon = "fa-solid fa-image"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "product", "type", "is_primary", "is_active",
        "width", "height", "file_size", "order"
    ]
    
    column_details_list = [
        "id", "product", "url", "type", "alt_text",
        "is_primary", "is_active", "order",
        "width", "height", "file_size",
        "created_at", "updated_at"
    ]
    
    form_columns = [
        "product", "url", "type", "alt_text", "order",
        "is_primary", "is_active",
        "width", "height", "file_size"
    ]
    
    column_searchable_list = ["product.title", "type", "alt_text"]
    column_sortable_list = [
        "id", "product", "type", "is_primary", "is_active",
        "order", "width", "height", "file_size", "created_at"
    ]
    column_filters = ["type", "is_primary", "is_active"]
    
    column_labels = {
        "id": "ID",
        "product": "Товар",
        "url": "URL изображения",
        "type": "Тип (image/video)",
        "alt_text": "Alt текст",
        "is_primary": "Главное",
        "is_active": "Активно",
        "order": "Порядок",
        "width": "Ширина (px)",
        "height": "Высота (px)",
        "file_size": "Размер файла (bytes)",
        "created_at": "Создано",
        "updated_at": "Обновлено"
    }
    
    column_formatters = {
        "url": lambda m, a: f'<img src="{m.url}" width="50">' if m.url and m.type == "image" else m.url,
        "file_size": lambda m, a: f"{m.file_size / 1024:.2f} KB" if m.file_size else "N/A"
    }


class EnhancedProductAttributeAdmin(ModelView, model=ProductAttribute):
    """Enhanced Product Attribute Admin with featured and usage tracking"""
    
    name = "Атрибут товара"
    name_plural = "Атрибуты товаров"
    icon = "fa-solid fa-tags"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "attribute_type", "attribute_value", "display_name",
        "is_active", "is_featured", "usage_count", "sort_order"
    ]
    
    column_details_list = [
        "id", "attribute_type", "attribute_value", "display_name",
        "description", "is_active", "is_featured", "usage_count",
        "sort_order", "created_by_admin_id", "created_at", "updated_at"
    ]
    
    form_columns = [
        "attribute_type", "attribute_value", "display_name", "description",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = [
        "attribute_type", "attribute_value", "display_name", "description"
    ]
    column_sortable_list = [
        "id", "attribute_type", "attribute_value", "is_active",
        "is_featured", "usage_count", "sort_order", "created_at"
    ]
    column_filters = ["attribute_type", "is_active", "is_featured"]
    
    column_labels = {
        "id": "ID",
        "attribute_type": "Тип атрибута",
        "attribute_value": "Значение",
        "display_name": "Отображаемое имя",
        "description": "Описание",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "usage_count": "Использований",
        "sort_order": "Порядок",
        "created_by_admin_id": "Создан админом",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    form_widget_args = {
        "description": {"rows": 3}
    }


class EnhancedBrandAdmin(ModelView, model=Brand):
    """Enhanced Brand Admin with featured flag"""
    
    name = "Бренд"
    name_plural = "Бренды"
    icon = "fa-solid fa-copyright"
    category = "🛍️ Каталог"
    
    column_list = [
        "id", "logo_url", "name", "slug", "country",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_details_list = [
        "id", "name", "slug", "description", "country",
        "logo_url", "is_active", "is_featured", "sort_order",
        "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description", "country",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = ["name", "slug", "description", "country"]
    column_sortable_list = [
        "id", "name", "country", "is_active", "is_featured",
        "sort_order", "created_at"
    ]
    column_filters = ["is_active", "is_featured", "country"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL",
        "description": "Описание",
        "country": "Страна",
        "logo_url": "Логотип",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }
    
    column_formatters = {
        "logo_url": lambda m, a: f'<img src="{m.logo_url}" width="40">' if m.logo_url else ""
    }


# Enhanced Filter Admin Views
class EnhancedProductFilterAdmin(ModelView, model=ProductFilter):
    """Enhanced ProductFilter with usage tracking"""
    
    name = "Фильтр товаров"
    name_plural = "Фильтры товаров"
    icon = "fa-solid fa-filter"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "filter_type", "filter_value", "display_name",
        "usage_count", "is_active", "sort_order"
    ]
    
    column_details_list = [
        "id", "filter_type", "filter_value", "display_name",
        "usage_count", "is_active", "sort_order",
        "created_at", "updated_at"
    ]
    
    form_columns = [
        "filter_type", "filter_value", "display_name",
        "is_active", "sort_order"
    ]
    
    column_searchable_list = ["filter_type", "filter_value", "display_name"]
    column_sortable_list = [
        "id", "filter_type", "usage_count", "is_active",
        "sort_order", "created_at"
    ]
    column_filters = ["filter_type", "is_active"]
    
    column_labels = {
        "id": "ID",
        "filter_type": "Тип фильтра",
        "filter_value": "Значение",
        "display_name": "Отображаемое имя",
        "usage_count": "Использований",
        "is_active": "Активен",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }


class EnhancedProductSeasonAdmin(ModelView, model=ProductSeason):
    """Enhanced Season with product count and featured"""
    
    name = "Сезон"
    name_plural = "Сезоны"
    icon = "fa-solid fa-calendar"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "name", "slug", "product_count",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_details_list = [
        "id", "name", "slug", "description",
        "product_count", "is_active", "is_featured", "sort_order",
        "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = [
        "id", "name", "product_count", "is_active",
        "is_featured", "sort_order", "created_at"
    ]
    column_filters = ["is_active", "is_featured"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL",
        "description": "Описание",
        "product_count": "Товаров",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }


class EnhancedProductMaterialAdmin(ModelView, model=ProductMaterial):
    """Enhanced Material with product count and featured"""
    
    name = "Материал"
    name_plural = "Материалы"
    icon = "fa-solid fa-cut"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "name", "slug", "product_count",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_details_list = [
        "id", "name", "slug", "description",
        "product_count", "is_active", "is_featured", "sort_order",
        "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = [
        "id", "name", "product_count", "is_active",
        "is_featured", "sort_order", "created_at"
    ]
    column_filters = ["is_active", "is_featured"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL",
        "description": "Описание",
        "product_count": "Товаров",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }


class EnhancedProductStyleAdmin(ModelView, model=ProductStyle):
    """Enhanced Style with product count and featured"""
    
    name = "Стиль"
    name_plural = "Стили"
    icon = "fa-solid fa-palette"
    category = "🎯 Фильтры"
    
    column_list = [
        "id", "name", "slug", "product_count",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_details_list = [
        "id", "name", "slug", "description",
        "product_count", "is_active", "is_featured", "sort_order",
        "created_at", "updated_at"
    ]
    
    form_columns = [
        "name", "slug", "description",
        "is_active", "is_featured", "sort_order"
    ]
    
    column_searchable_list = ["name", "slug", "description"]
    column_sortable_list = [
        "id", "name", "product_count", "is_active",
        "is_featured", "sort_order", "created_at"
    ]
    column_filters = ["is_active", "is_featured"]
    
    column_labels = {
        "id": "ID",
        "name": "Название",
        "slug": "URL",
        "description": "Описание",
        "product_count": "Товаров",
        "is_active": "Активен",
        "is_featured": "В избранном",
        "sort_order": "Порядок",
        "created_at": "Создан",
        "updated_at": "Обновлен"
    }


class EnhancedProductSearchAdmin(ModelView, model=ProductSearch):
    """Enhanced Search with result count"""
    
    name = "Поиск товаров"
    name_plural = "Поиск товаров"
    icon = "fa-solid fa-search"
    category = "📊 Аналитика"
    
    column_list = [
        "id", "search_term", "search_count", "result_count",
        "last_searched"
    ]
    
    column_details_list = [
        "id", "search_term", "search_count", "result_count",
        "last_searched", "created_at"
    ]
    
    # Read-only for analytics
    can_create = False
    can_edit = False
    can_delete = True
    
    column_searchable_list = ["search_term"]
    column_sortable_list = [
        "id", "search_term", "search_count", "result_count",
        "last_searched", "created_at"
    ]
    column_filters = ["search_term"]
    
    column_labels = {
        "id": "ID",
        "search_term": "Поисковый запрос",
        "search_count": "Количество поисков",
        "result_count": "Результатов",
        "last_searched": "Последний поиск",
        "created_at": "Создан"
    }
    
    column_default_sort = ("search_count", True)  # Sort by most popular

