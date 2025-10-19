from sqladmin import ModelView
from src.app_01.admin.multi_market_admin_views import MarketAwareModelView
from src.app_01.models.orders.order import Order, OrderStatus
from src.app_01.models.orders.order_item import OrderItem
from src.app_01.models.orders.order_status_history import OrderStatusHistory
from markupsafe import Markup


class OrderAdmin(MarketAwareModelView, model=Order):
    name = "Заказы"
    name_plural = "Заказы"
    icon = "fa-solid fa-shopping-cart"
    category = "🛍️ Продажи"
    
    column_list = [
        "id", "order_number", "customer_name", "phone_number",
        "status", "total_amount", "order_date", "shipping_city",
    ]
    
    column_formatters = {
        "status": lambda m, a: Markup(
            f'<span class="badge badge-{"warning" if m.status == OrderStatus.PENDING else "success"}">{m.status.value.title()}</span>'
        )
    }

class OrderItemAdmin(MarketAwareModelView, model=OrderItem):
    name = "Товары в заказах"
    name_plural = "Товары в заказах"
    icon = "fa-solid fa-box"
    category = "🛍️ Продажи"

class OrderStatusHistoryAdmin(MarketAwareModelView, model=OrderStatusHistory):
    name = "История заказов"
    name_plural = "История заказов"
    icon = "fa-solid fa-history"
    category = "🛍️ Продажи"
