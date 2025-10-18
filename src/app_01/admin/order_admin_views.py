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
from .multi_market_admin_views import MarketAwareModelView


class OrderAdmin(MarketAwareModelView, model=Order):
    """
    Enhanced Order Management Interface with TDD improvements
    
    Features:
    - Visual status badges with colors
    - Better column formatting with currency
    - Enhanced search and filters
    - Export functionality
    - Quick filters (today's orders, pending, etc.)
    """
    
    # Display settings
    name = "Заказы"
    name_plural = "Заказы"
    icon = "fa-solid fa-shopping-cart"
    category = "🛒 Продажи"  # Group in sidebar
    
    # Role-based access control
    required_roles = ["order_management", "super_admin"]
    required_permissions = {
        "list": None,
        "create": "manage_orders",
        "edit": "manage_orders",
        "delete": "delete_orders",
        "export": "export_orders"
    }
    
    # Column configuration - show most important info
    column_list = [
        "id", "order_number", "customer_name", "customer_phone",
        "status", "total_amount", "order_date", "delivery_city"
    ]
    
    # Detailed view shows everything
    column_details_list = [
        "id", "order_number", "user_id", "status",
        "customer_name", "customer_phone", "customer_email",
        "delivery_address", "delivery_city", "delivery_notes",
        "subtotal", "shipping_cost", "total_amount", "currency",
        "order_date", "confirmed_date", "shipped_date", "delivered_date", "cancelled_date",
        "notes", "created_at", "updated_at",
        "order_items", "status_history"
    ]
    
    # Form configuration
    form_columns = [
        "order_number", "user_id", "status",
        "customer_name", "customer_phone", "customer_email",
        "delivery_address", "delivery_city", "delivery_notes",
        "subtotal", "shipping_cost", "total_amount", "currency",
        "notes"
    ]
    
    # Enhanced search - search by multiple fields
    column_searchable_list = [
        "order_number", 
        "customer_name", 
        "customer_phone", 
        "customer_email",
        "delivery_city"
    ]
    
    # Sortable columns
    column_sortable_list = [
        "id", "order_number", "total_amount", 
        "order_date", "status", "customer_name"
    ]
    
    # Enhanced filters for better order management
    column_filters = [
        "status",          # Filter by order status
        "order_date",      # Filter by date range
        "delivery_city",   # Filter by city
        "currency",        # Filter by currency (KGS/USD)
        "total_amount",    # Filter by order value
        "created_at"       # Filter by creation date
    ]
    
    # Default sorting (newest first for quick access to recent orders)
    column_default_sort = [("order_date", True)]  # Descending
    
    # Russian labels for better UX
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
        "shipping_cost": "Доставка",
        "total_amount": "Итого",
        "currency": "Валюта",
        "order_date": "Дата заказа",
        "confirmed_date": "Подтвержден",
        "shipped_date": "Отправлен",
        "delivered_date": "Доставлен",
        "cancelled_date": "Отменен",
        "notes": "Примечания",
        "created_at": "Создан",
        "updated_at": "Обновлен",
        "order_items": "Товары",
        "status_history": "История"
    }
    
    # Form labels with hints
    form_label = "Заказ"
    form_columns_labels = {
        "order_number": "Номер заказа",
        "user_id": "ID пользователя",
        "status": "Статус заказа",
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
        "notes": "Примечания администратора"
    }
    
    # Enhanced formatters for better display
    column_formatters = {
        # Format money with thousand separators and currency
        "total_amount": lambda model, _: f"{model.total_amount:,.2f} {model.currency}" if model.total_amount else "0.00",
        "subtotal": lambda model, _: f"{model.subtotal:,.2f}" if model.subtotal else "0.00",
        "shipping_cost": lambda model, _: f"{model.shipping_cost:,.2f}" if model.shipping_cost else "0.00",
        
        # Format status with visual indicators
        "status": lambda model, _: _format_order_status(model.status),
        
        # Format dates in Russian format
        "order_date": lambda model, _: model.order_date.strftime("%d.%m.%Y %H:%M") if model.order_date else "-",
        "confirmed_date": lambda model, _: model.confirmed_date.strftime("%d.%m.%Y %H:%M") if model.confirmed_date else "-",
        "shipped_date": lambda model, _: model.shipped_date.strftime("%d.%m.%Y %H:%M") if model.shipped_date else "-",
        "delivered_date": lambda model, _: model.delivered_date.strftime("%d.%m.%Y %H:%M") if model.delivered_date else "-",
        
        # Format phone with better display
        "customer_phone": lambda model, _: model.customer_phone or "-"
    }
    
    # Permissions - allow editing and viewing but not deletion
    can_create = True     # Allow creating manual orders
    can_edit = True       # Allow editing order details
    can_delete = False    # Never delete orders (for audit trail)
    can_view_details = True
    can_export = True     # Enable CSV export
    
    # Pagination settings
    page_size = 50
    page_size_options = [25, 50, 100, 200]
    
    # Description for admins
    column_descriptions = {
        "status": "Статус заказа: PENDING (ожидает подтверждения) → CONFIRMED (подтвержден) → SHIPPED (отправлен) → DELIVERED (доставлен)",
        "total_amount": "Итоговая сумма заказа (товары + доставка)",
        "notes": "Внутренние примечания администратора (не видны клиенту)"
    }


def _format_order_status(status):
    """
    Format order status with visual badges
    
    Returns HTML span with colored badge based on status
    """
    status_colors = {
        OrderStatus.PENDING: ("⏳ Ожидает", "warning"),      # Yellow
        OrderStatus.CONFIRMED: ("✅ Подтвержден", "info"),    # Blue
        OrderStatus.SHIPPED: ("🚚 Отправлен", "primary"),     # Purple
        OrderStatus.DELIVERED: ("✅ Доставлен", "success"),   # Green
        OrderStatus.CANCELLED: ("❌ Отменен", "danger"),      # Red
    }
    
    label, color = status_colors.get(status, (status.value, "secondary"))
    return f'<span class="badge badge-{color}">{label}</span>'


class OrderItemAdmin(MarketAwareModelView, model=OrderItem):
    """
    Order Items Management - Enhanced view with better formatting
    
    Shows individual items in orders with full product details
    """
    
    name = "Товары в заказах"
    name_plural = "Товары в заказах"
    icon = "fa-solid fa-box"
    category = "🛒 Продажи"
    
    # Show key info in list view
    column_list = [
        "id", "order_id", "product_name", "size", "color",
        "quantity", "unit_price", "total_price"
    ]
    
    # Full details view
    column_details_list = [
        "id", "order_id", "sku_id", 
        "product_name", "sku_code", "size", "color",
        "quantity", "unit_price", "total_price", "currency"
    ]
    
    # Form for creating/editing
    form_columns = [
        "order_id", "sku_id", "product_name", "sku_code",
        "size", "color", "quantity", "unit_price", "total_price", "currency"
    ]
    
    # Search by product name or SKU code
    column_searchable_list = ["product_name", "sku_code"]
    
    # Sortable columns
    column_sortable_list = ["id", "order_id", "product_name", "quantity", "unit_price", "total_price"]
    
    # Filters
    column_filters = ["order_id", "size", "color", "quantity"]
    
    # Russian labels
    column_labels = {
        "id": "ID",
        "order_id": "Заказ №",
        "sku_id": "SKU ID",
        "product_name": "Товар",
        "sku_code": "Артикул",
        "size": "Размер",
        "color": "Цвет",
        "quantity": "Кол-во",
        "unit_price": "Цена",
        "total_price": "Итого",
        "currency": "Валюта"
    }
    
    # Form labels
    form_label = "Товар в заказе"
    form_columns_labels = {
        "order_id": "Номер заказа",
        "sku_id": "ID артикула",
        "product_name": "Название товара",
        "sku_code": "Код артикула (SKU)",
        "size": "Размер",
        "color": "Цвет",
        "quantity": "Количество",
        "unit_price": "Цена за единицу",
        "total_price": "Итоговая сумма",
        "currency": "Валюта"
    }
    
    # Enhanced formatters
    column_formatters = {
        "total_price": lambda model, _: f"<b>{model.total_price:,.2f} {model.currency}</b>" if model.total_price else "0.00",
        "unit_price": lambda model, _: f"{model.unit_price:,.2f}" if model.unit_price else "0.00",
        "quantity": lambda model, _: f"<b>{model.quantity}x</b>",
        "product_name": lambda model, _: model.product_name or "-"
    }
    
    # Permissions
    can_create = True
    can_edit = True
    can_delete = True  # Allow deletion if needed
    can_view_details = True
    can_export = True
    
    # Pagination
    page_size = 50
    page_size_options = [25, 50, 100]


class OrderStatusHistoryAdmin(MarketAwareModelView, model=OrderStatusHistory):
    """
    Order Status History - Audit Trail for Order Changes
    
    Read-only view to track all status changes for transparency
    """
    
    name = "История заказов"
    name_plural = "История заказов"
    icon = "fa-solid fa-history"
    category = "🛒 Продажи"
    
    # Show key info in list
    column_list = [
        "id", "order_id", "previous_status", "status", 
        "changed_by_admin_id", "created_at"
    ]
    
    # Full details
    column_details_list = [
        "id", "order_id", "status", "previous_status",
        "changed_by_admin_id", "notes", "created_at"
    ]
    
    # Read-only for security and audit integrity
    can_create = False  # History is auto-generated
    can_edit = False    # Never edit history
    can_delete = False  # Never delete history
    can_view_details = True
    can_export = True   # Allow exporting for audits
    
    # Search in notes
    column_searchable_list = ["notes"]
    
    # Sortable columns
    column_sortable_list = ["id", "order_id", "created_at", "status"]
    
    # Filters for audit queries
    column_filters = [
        "status", 
        "previous_status",
        "order_id", 
        "changed_by_admin_id",
        "created_at"
    ]
    
    # Show newest first
    column_default_sort = [("created_at", True)]
    
    # Russian labels
    column_labels = {
        "id": "ID",
        "order_id": "Заказ №",
        "status": "Новый статус",
        "previous_status": "Был",
        "changed_by_admin_id": "Кто изменил",
        "notes": "Примечания",
        "created_at": "Когда"
    }
    
    # Enhanced formatters
    column_formatters = {
        "status": lambda model, _: _format_order_status(model.status),
        "previous_status": lambda model, _: _format_order_status(model.previous_status) if model.previous_status else "-",
        "created_at": lambda model, _: model.created_at.strftime("%d.%m.%Y %H:%M") if model.created_at else "-",
        "notes": lambda model, _: model.notes or "-"
    }
    
    # Show more records per page for history
    page_size = 100
    page_size_options = [50, 100, 200, 500]
    
    # Description
    column_descriptions = {
        "status": "Новый статус заказа после изменения",
        "previous_status": "Статус до изменения",
        "changed_by_admin_id": "ID администратора, который изменил статус",
        "created_at": "Дата и время изменения статуса"
    }

