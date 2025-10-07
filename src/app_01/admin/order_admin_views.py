"""
Order Management Admin Views
SQLAdmin interfaces for managing orders, order items, and order history
"""

from sqladmin import ModelView
from starlette.requests import Request
from datetime import datetime

from ..models.orders.order import Order, OrderStatus
from ..models.orders.order_item import OrderItem
from ..models.orders.order_status_history import OrderStatusHistory


class OrderAdmin(ModelView, model=Order):
    """Order management interface - CRITICAL for e-commerce operations"""
    
    # Display settings
    name = "Заказы"
    name_plural = "Заказы"
    icon = "fa-solid fa-shopping-cart"
    
    # Column configuration
    column_list = [
        "id", "order_number", "customer_name", "status", 
        "total_amount", "order_date", "delivery_city"
    ]
    
    column_details_list = [
        "id", "order_number", "user_id", "status",
        "customer_name", "customer_phone", "customer_email",
        "delivery_address", "delivery_city", "delivery_notes",
        "subtotal", "shipping_cost", "total_amount", "currency",
        "order_date", "confirmed_date", "shipped_date", "delivered_date",
        "notes", "created_at", "updated_at"
    ]
    
    # Form configuration
    form_columns = [
        "order_number", "user_id", "status",
        "customer_name", "customer_phone", "customer_email",
        "delivery_address", "delivery_city", "delivery_notes",
        "subtotal", "shipping_cost", "total_amount", "currency",
        "notes"
    ]
    
    # Search and filters
    column_searchable_list = ["order_number", "customer_name", "customer_phone", "customer_email"]
    column_sortable_list = ["id", "order_number", "total_amount", "order_date", "status"]
    column_filters = ["status", "order_date", "delivery_city", "currency"]
    
    # Default sorting (newest first)
    column_default_sort = [("order_date", True)]
    
    # Column labels (Russian)
    column_labels = {
        "id": "ID",
        "order_number": "Номер заказа",
        "user_id": "ID пользователя",
        "status": "Статус",
        "customer_name": "Имя клиента",
        "customer_phone": "Телефон",
        "customer_email": "Email",
        "delivery_address": "Адрес доставки",
        "delivery_city": "Город",
        "delivery_notes": "Примечания к доставке",
        "subtotal": "Сумма товаров",
        "shipping_cost": "Стоимость доставки",
        "total_amount": "Итого",
        "currency": "Валюта",
        "order_date": "Дата заказа",
        "confirmed_date": "Дата подтверждения",
        "shipped_date": "Дата отправки",
        "delivered_date": "Дата доставки",
        "cancelled_date": "Дата отмены",
        "notes": "Примечания администратора",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "order_items": "Товары в заказе",
        "status_history": "История статусов"
    }
    
    # Form labels
    form_label = "Заказ"
    form_columns_labels = {
        "order_number": "Номер заказа (#1001)",
        "user_id": "ID пользователя",
        "status": "Статус заказа",
        "customer_name": "Имя клиента",
        "customer_phone": "Телефон клиента",
        "customer_email": "Email клиента (опционально)",
        "delivery_address": "Адрес доставки",
        "delivery_city": "Город доставки",
        "delivery_notes": "Примечания к доставке",
        "subtotal": "Сумма товаров (сом)",
        "shipping_cost": "Стоимость доставки (сом)",
        "total_amount": "Итоговая сумма (сом)",
        "currency": "Валюта (KGS/USD)",
        "notes": "Примечания администратора"
    }
    
    # Custom formatting
    column_formatters = {
        "total_amount": lambda model, _: f"{model.total_amount:,.2f} {model.currency}",
        "status": lambda model, _: model.status_display if hasattr(model, 'status_display') else model.status.value,
        "order_date": lambda model, _: model.order_date.strftime("%d.%m.%Y %H:%M") if model.order_date else ""
    }
    
    # Permissions
    can_create = True
    can_edit = True
    can_delete = False  # Orders should not be deleted, only cancelled
    can_view_details = True
    can_export = True  # Allow exporting orders for accounting
    
    # Page size
    page_size = 50
    page_size_options = [25, 50, 100, 200]


class OrderItemAdmin(ModelView, model=OrderItem):
    """Order items management interface"""
    
    name = "Товары в заказах"
    name_plural = "Товары в заказах"
    icon = "fa-solid fa-box"
    
    column_list = [
        "id", "order_id", "sku_id", "quantity", 
        "unit_price", "total_price"
    ]
    
    column_details_list = [
        "id", "order_id", "sku_id", "product_name",
        "sku_code", "size", "color",
        "quantity", "unit_price", "total_price", "currency"
    ]
    
    form_columns = [
        "order_id", "sku_id", "product_name", "sku_code",
        "size", "color", "quantity", "unit_price", "total_price", "currency"
    ]
    
    column_searchable_list = ["product_name", "sku_code"]
    column_sortable_list = ["id", "order_id", "quantity", "total_price"]
    column_filters = ["order_id", "size", "color"]
    
    column_labels = {
        "id": "ID",
        "order_id": "ID заказа",
        "sku_id": "ID артикула",
        "product_name": "Название товара",
        "sku_code": "Код артикула",
        "size": "Размер",
        "color": "Цвет",
        "quantity": "Количество",
        "unit_price": "Цена за единицу",
        "total_price": "Итого",
        "currency": "Валюта"
    }
    
    form_label = "Товар в заказе"
    form_columns_labels = {
        "order_id": "Номер заказа",
        "sku_id": "ID артикула",
        "product_name": "Название товара",
        "sku_code": "Код артикула (SKU)",
        "size": "Размер",
        "color": "Цвет",
        "quantity": "Количество",
        "unit_price": "Цена за единицу (сом)",
        "total_price": "Итоговая сумма (сом)",
        "currency": "Валюта"
    }
    
    column_formatters = {
        "total_price": lambda model, _: f"{model.total_price:,.2f} {model.currency}",
        "unit_price": lambda model, _: f"{model.unit_price:,.2f}"
    }
    
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True
    
    page_size = 50


class OrderStatusHistoryAdmin(ModelView, model=OrderStatusHistory):
    """Order status history tracking interface"""
    
    name = "История заказов"
    name_plural = "История заказов"
    icon = "fa-solid fa-history"
    
    column_list = [
        "id", "order_id", "status", "changed_by_admin_id", "created_at"
    ]
    
    column_details_list = [
        "id", "order_id", "status", "previous_status",
        "changed_by_admin_id", "notes", "created_at"
    ]
    
    # Read-only for security
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    
    column_searchable_list = ["notes"]
    column_sortable_list = ["id", "order_id", "created_at"]
    column_filters = ["status", "order_id", "changed_by_admin_id"]
    
    column_default_sort = [("created_at", True)]
    
    column_labels = {
        "id": "ID",
        "order_id": "ID заказа",
        "status": "Новый статус",
        "previous_status": "Предыдущий статус",
        "changed_by_admin_id": "Изменил администратор",
        "notes": "Примечания",
        "created_at": "Дата изменения"
    }
    
    column_formatters = {
        "created_at": lambda model, _: model.created_at.strftime("%d.%m.%Y %H:%M") if model.created_at else ""
    }
    
    page_size = 100

