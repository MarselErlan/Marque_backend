"""
Cart Management Admin Views
SQLAdmin interfaces for managing shopping carts and cart items
"""

from sqladmin import ModelView
from starlette.requests import Request

from ..models.orders.cart import Cart, CartItem


class CartAdmin(ModelView, model=Cart):
    """Shopping cart management interface"""
    
    # Display settings
    name = "Корзины"
    name_plural = "Корзины"
    icon = "fa-solid fa-shopping-basket"
    
    # Column configuration
    column_list = [
        "id", "user_id", "created_at", "updated_at"
    ]
    
    column_details_list = [
        "id", "user_id", "created_at", "updated_at", "items"
    ]
    
    # Form configuration
    form_columns = [
        "user_id"
    ]
    
    # Search and filters
    column_searchable_list = []
    column_sortable_list = ["id", "user_id", "created_at", "updated_at"]
    column_filters = ["created_at", "updated_at"]
    
    # Default sorting (newest first)
    column_default_sort = [("updated_at", True)]
    
    # Column labels (Russian)
    column_labels = {
        "id": "ID",
        "user_id": "ID пользователя",
        "created_at": "Создана",
        "updated_at": "Обновлена",
        "items": "Товары в корзине"
    }
    
    # Form labels
    form_label = "Корзина"
    form_columns_labels = {
        "user_id": "ID пользователя"
    }
    
    # Custom formatting
    column_formatters = {
        "created_at": lambda model, _: model.created_at.strftime("%d.%m.%Y %H:%M") if model.created_at else "",
        "updated_at": lambda model, _: model.updated_at.strftime("%d.%m.%Y %H:%M") if model.updated_at else ""
    }
    
    # Permissions
    can_create = True
    can_edit = False  # Carts are managed by users
    can_delete = True  # Can delete abandoned carts
    can_view_details = True
    can_export = True  # Export for abandoned cart analysis
    
    # Page size
    page_size = 50
    page_size_options = [25, 50, 100]


class CartItemAdmin(ModelView, model=CartItem):
    """Cart items management interface"""
    
    name = "Товары в корзинах"
    name_plural = "Товары в корзинах"
    icon = "fa-solid fa-shopping-bag"
    
    column_list = [
        "id", "cart_id", "sku_id", "quantity"
    ]
    
    column_details_list = [
        "id", "cart_id", "sku_id", "quantity"
    ]
    
    form_columns = [
        "cart_id", "sku_id", "quantity"
    ]
    
    column_searchable_list = []
    column_sortable_list = ["id", "cart_id", "quantity"]
    column_filters = ["cart_id", "sku_id"]
    
    column_labels = {
        "id": "ID",
        "cart_id": "ID корзины",
        "sku_id": "ID артикула",
        "quantity": "Количество"
    }
    
    form_label = "Товар в корзине"
    form_columns_labels = {
        "cart_id": "ID корзины",
        "sku_id": "ID артикула (SKU)",
        "quantity": "Количество"
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    page_size = 50

