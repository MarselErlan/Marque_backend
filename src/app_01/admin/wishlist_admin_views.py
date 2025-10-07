"""
Wishlist Management Admin Views
SQLAdmin interfaces for managing user wishlists
"""

from sqladmin import ModelView
from starlette.requests import Request

from ..models.users.wishlist import Wishlist, WishlistItem


class WishlistAdmin(ModelView, model=Wishlist):
    """Wishlist management interface"""
    
    # Display settings
    name = "Списки желаний"
    name_plural = "Списки желаний"
    icon = "fa-solid fa-heart"
    
    # Column configuration
    column_list = [
        "id", "user_id", "created_at"
    ]
    
    column_details_list = [
        "id", "user_id", "created_at", "items"
    ]
    
    # Form configuration
    form_columns = [
        "user_id"
    ]
    
    # Search and filters
    column_searchable_list = []
    column_sortable_list = ["id", "user_id", "created_at"]
    column_filters = ["created_at"]
    
    # Default sorting (newest first)
    column_default_sort = [("created_at", True)]
    
    # Column labels (Russian)
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "created_at": "Создан",
        "items": "Товары в списке"
    }
    
    # Form labels
    form_label = "Список желаний"
    form_columns_labels = {
        "user_id": "ID пользователя"
    }
    
    # Custom formatting
    column_formatters = {
        "created_at": lambda model, _: model.created_at.strftime("%d.%m.%Y %H:%M") if model.created_at else ""
    }
    
    # Permissions
    can_create = True
    can_edit = False  # Wishlists are managed by users
    can_delete = True  # Can delete if needed
    can_view_details = True
    can_export = True  # Export for product popularity analysis
    
    # Page size
    page_size = 50
    page_size_options = [25, 50, 100]


class WishlistItemAdmin(ModelView, model=WishlistItem):
    """Wishlist items management interface"""
    
    name = "Товары в списках желаний"
    name_plural = "Товары в списках желаний"
    icon = "fa-solid fa-star"
    
    column_list = [
        "id", "wishlist_id", "product_id", "added_at"
    ]
    
    column_details_list = [
        "id", "wishlist_id", "product_id", "added_at"
    ]
    
    form_columns = [
        "wishlist_id", "product_id"
    ]
    
    column_searchable_list = []
    column_sortable_list = ["id", "wishlist_id", "product_id", "added_at"]
    column_filters = ["wishlist_id", "product_id", "added_at"]
    
    # Default sorting (newest first)
    column_default_sort = [("added_at", True)]
    
    column_labels = {
        "id": "ID",
        "wishlist_id": "ID списка",
        "product_id": "ID товара",
        "added_at": "Добавлен"
    }
    
    form_label = "Товар в списке желаний"
    form_columns_labels = {
        "wishlist_id": "ID списка желаний",
        "product_id": "ID товара"
    }
    
    column_formatters = {
        "added_at": lambda model, _: model.added_at.strftime("%d.%m.%Y %H:%M") if model.added_at else ""
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    page_size = 50

