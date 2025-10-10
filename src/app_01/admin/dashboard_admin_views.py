"""
Dashboard Admin Views - Business Intelligence and Analytics

Provides real-time insights into:
- Sales performance (today, week, month)
- Revenue tracking
- Order statistics
- Inventory alerts
- Popular products
- User analytics
"""

from sqladmin import BaseView
from starlette.requests import Request
from starlette.responses import HTMLResponse
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta
from decimal import Decimal

from ..models.orders.order import Order, OrderStatus
from ..models.orders.order_item import OrderItem
from ..models.products.product import Product
from ..models.products.sku import SKU
from ..models.users.user import User
from ..db.market_db import db_manager, Market


class DashboardView(BaseView):
    """
    Main Dashboard - Business Intelligence Center
    
    Shows key metrics and recent activity for quick business overview
    """
    
    name = "Dashboard"
    icon = "fa-solid fa-chart-line"
    identity = "dashboard"  # Unique identifier for routing
    
    async def index(self, request: Request) -> HTMLResponse:
        """
        Render dashboard with real-time business metrics
        """
        # Get database session (KG market by default)
        db = next(db_manager.get_db_session(Market.KG))
        
        try:
            # Calculate date ranges
            today = datetime.utcnow().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            # ==================================================================
            # 📊 SALES METRICS
            # ==================================================================
            
            # Orders today
            orders_today = db.query(func.count(Order.id)).filter(
                func.date(Order.order_date) == today
            ).scalar() or 0
            
            # Orders this week
            orders_week = db.query(func.count(Order.id)).filter(
                Order.order_date >= week_ago
            ).scalar() or 0
            
            # Orders this month
            orders_month = db.query(func.count(Order.id)).filter(
                Order.order_date >= month_ago
            ).scalar() or 0
            
            # ==================================================================
            # 💰 REVENUE METRICS
            # ==================================================================
            
            # Revenue today
            revenue_today = db.query(func.sum(Order.total_amount)).filter(
                func.date(Order.order_date) == today,
                Order.status != OrderStatus.CANCELLED
            ).scalar() or Decimal('0.00')
            
            # Revenue this week
            revenue_week = db.query(func.sum(Order.total_amount)).filter(
                Order.order_date >= week_ago,
                Order.status != OrderStatus.CANCELLED
            ).scalar() or Decimal('0.00')
            
            # Revenue this month
            revenue_month = db.query(func.sum(Order.total_amount)).filter(
                Order.order_date >= month_ago,
                Order.status != OrderStatus.CANCELLED
            ).scalar() or Decimal('0.00')
            
            # Average order value
            avg_order_value = db.query(func.avg(Order.total_amount)).filter(
                Order.status != OrderStatus.CANCELLED
            ).scalar() or Decimal('0.00')
            
            # ==================================================================
            # 📦 ORDER STATUS BREAKDOWN
            # ==================================================================
            
            orders_pending = db.query(func.count(Order.id)).filter(
                Order.status == OrderStatus.PENDING
            ).scalar() or 0
            
            orders_confirmed = db.query(func.count(Order.id)).filter(
                Order.status == OrderStatus.CONFIRMED
            ).scalar() or 0
            
            orders_shipped = db.query(func.count(Order.id)).filter(
                Order.status == OrderStatus.SHIPPED
            ).scalar() or 0
            
            orders_delivered = db.query(func.count(Order.id)).filter(
                Order.status == OrderStatus.DELIVERED
            ).scalar() or 0
            
            # ==================================================================
            # 🛍️ PRODUCT METRICS
            # ==================================================================
            
            # Total products
            total_products = db.query(func.count(Product.id)).filter(
                Product.is_active == True
            ).scalar() or 0
            
            # Low stock products (< 10 items)
            low_stock_products = db.query(
                Product.id, Product.title, func.sum(SKU.stock).label('total_stock')
            ).join(
                SKU, Product.id == SKU.product_id
            ).group_by(
                Product.id, Product.title
            ).having(
                func.sum(SKU.stock) < 10
            ).limit(10).all()
            
            low_stock_count = len(low_stock_products)
            
            # Out of stock products
            out_of_stock_count = db.query(func.count(Product.id)).filter(
                Product.id.in_(
                    db.query(SKU.product_id).filter(
                        SKU.stock == 0
                    ).distinct()
                )
            ).scalar() or 0
            
            # ==================================================================
            # 🔥 TOP PRODUCTS
            # ==================================================================
            
            # Most popular products (by sold count)
            popular_products = db.query(
                Product.id, Product.title, Product.sold_count
            ).filter(
                Product.is_active == True
            ).order_by(
                Product.sold_count.desc()
            ).limit(5).all()
            
            # ==================================================================
            # 👥 USER METRICS
            # ==================================================================
            
            # Total users
            total_users = db.query(func.count(User.id)).scalar() or 0
            
            # New users today
            users_today = db.query(func.count(User.id)).filter(
                func.date(User.created_at) == today
            ).scalar() or 0
            
            # New users this week
            users_week = db.query(func.count(User.id)).filter(
                User.created_at >= week_ago
            ).scalar() or 0
            
            # New users this month
            users_month = db.query(func.count(User.id)).filter(
                User.created_at >= month_ago
            ).scalar() or 0
            
            # ==================================================================
            # 📋 RECENT ORDERS
            # ==================================================================
            
            recent_orders = db.query(Order).order_by(
                Order.order_date.desc()
            ).limit(10).all()
            
            # ==================================================================
            # RENDER HTML
            # ==================================================================
            
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Marque Admin</title>
    <link rel="stylesheet" href="/admin/statics/css/tabler.min.css">
    <link rel="stylesheet" href="/admin/statics/css/fontawesome.min.css">
    <style>
        .metric-card {{
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: bold;
            color: #206bc4;
        }}
        .metric-label {{
            font-size: 0.875rem;
            color: #666;
            text-transform: uppercase;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 600;
        }}
        .badge-pending {{ background: #ffc107; color: #000; }}
        .badge-confirmed {{ background: #17a2b8; color: #fff; }}
        .badge-shipped {{ background: #6f42c1; color: #fff; }}
        .badge-delivered {{ background: #28a745; color: #fff; }}
        .table-compact {{ font-size: 0.875rem; }}
        .alert-low-stock {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 12px; margin-bottom: 8px; }}
        .alert-out-stock {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 12px; margin-bottom: 8px; }}
    </style>
</head>
<body>
    <div class="container-fluid p-4">
        <h1 class="mb-4">📊 Бизнес Панель</h1>
        
        <!-- Sales Overview -->
        <div class="row mb-4">
            <div class="col-md-12">
                <h2 class="mb-3">💰 Продажи</h2>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Заказов Сегодня</div>
                    <div class="metric-value">{orders_today}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Заказов За Неделю</div>
                    <div class="metric-value">{orders_week}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Заказов За Месяц</div>
                    <div class="metric-value">{orders_month}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Средний Чек</div>
                    <div class="metric-value">{float(avg_order_value):,.0f} ₸</div>
                </div>
            </div>
        </div>
        
        <!-- Revenue Overview -->
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                    <div class="metric-label" style="color: rgba(255,255,255,0.8);">Выручка Сегодня</div>
                    <div class="metric-value" style="color: white;">{float(revenue_today):,.0f} ₸</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white;">
                    <div class="metric-label" style="color: rgba(255,255,255,0.8);">Выручка За Неделю</div>
                    <div class="metric-value" style="color: white;">{float(revenue_week):,.0f} ₸</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white;">
                    <div class="metric-label" style="color: rgba(255,255,255,0.8);">Выручка За Месяц</div>
                    <div class="metric-value" style="color: white;">{float(revenue_month):,.0f} ₸</div>
                </div>
            </div>
        </div>
        
        <!-- Order Status Breakdown -->
        <div class="row mb-4">
            <div class="col-md-12">
                <h2 class="mb-3">📦 Статус Заказов</h2>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <span class="status-badge badge-pending">⏳ Ожидают</span>
                    <div class="metric-value mt-2">{orders_pending}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <span class="status-badge badge-confirmed">✅ Подтверждены</span>
                    <div class="metric-value mt-2">{orders_confirmed}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <span class="status-badge badge-shipped">🚚 Отправлены</span>
                    <div class="metric-value mt-2">{orders_shipped}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <span class="status-badge badge-delivered">✅ Доставлены</span>
                    <div class="metric-value mt-2">{orders_delivered}</div>
                </div>
            </div>
        </div>
        
        <!-- Inventory & Products -->
        <div class="row mb-4">
            <div class="col-md-6">
                <h2 class="mb-3">📦 Товары & Склад</h2>
                <div class="metric-card">
                    <div class="metric-label">Всего Товаров</div>
                    <div class="metric-value">{total_products}</div>
                </div>
                
                {f'''
                <div class="alert-low-stock mt-3">
                    <strong>⚠️ Мало на складе:</strong> {low_stock_count} товаров
                </div>
                ''' if low_stock_count > 0 else ''}
                
                {f'''
                <div class="alert-out-stock mt-2">
                    <strong>❌ Нет в наличии:</strong> {out_of_stock_count} товаров
                </div>
                ''' if out_of_stock_count > 0 else ''}
                
                {f'''
                <div class="mt-3">
                    <h4>Товары с низким остатком:</h4>
                    <table class="table table-sm table-compact">
                        <thead>
                            <tr>
                                <th>Товар</th>
                                <th>Остаток</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join([f'<tr><td>{p.title}</td><td><span class="badge badge-warning">{int(p.total_stock)}</span></td></tr>' for p in low_stock_products[:5]])}
                        </tbody>
                    </table>
                </div>
                ''' if low_stock_products else ''}
            </div>
            
            <div class="col-md-6">
                <h2 class="mb-3">🔥 Популярные Товары</h2>
                <table class="table table-striped table-compact">
                    <thead>
                        <tr>
                            <th>Товар</th>
                            <th>Продано</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([f'<tr><td>{p.title}</td><td><strong>{p.sold_count}</strong></td></tr>' for p in popular_products]) if popular_products else '<tr><td colspan="2" class="text-center text-muted">Нет данных</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- User Analytics -->
        <div class="row mb-4">
            <div class="col-md-12">
                <h2 class="mb-3">👥 Пользователи</h2>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Всего Пользователей</div>
                    <div class="metric-value">{total_users}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Новых Сегодня</div>
                    <div class="metric-value">{users_today}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Новых За Неделю</div>
                    <div class="metric-value">{users_week}</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-label">Новых За Месяц</div>
                    <div class="metric-value">{users_month}</div>
                </div>
            </div>
        </div>
        
        <!-- Recent Orders -->
        <div class="row mb-4">
            <div class="col-md-12">
                <h2 class="mb-3">📋 Последние Заказы</h2>
                <table class="table table-striped table-hover table-compact">
                    <thead>
                        <tr>
                            <th>№ Заказа</th>
                            <th>Клиент</th>
                            <th>Сумма</th>
                            <th>Статус</th>
                            <th>Дата</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join([
                            f'''<tr>
                                <td><a href="/admin/order/details/{o.id}">{o.order_number}</a></td>
                                <td>{o.customer_name}</td>
                                <td>{float(o.total_amount):,.0f} {o.currency}</td>
                                <td>{_format_status_badge(o.status)}</td>
                                <td>{o.order_date.strftime("%d.%m.%Y %H:%M") if o.order_date else "-"}</td>
                            </tr>'''
                            for o in recent_orders
                        ]) if recent_orders else '<tr><td colspan="5" class="text-center text-muted">Нет заказов</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script src="/admin/statics/js/jquery.min.js"></script>
    <script src="/admin/statics/js/tabler.min.js"></script>
</body>
</html>
            """
            
            return HTMLResponse(content=html)
            
        except Exception as e:
            return HTMLResponse(content=f"<h1>Error loading dashboard: {str(e)}</h1>", status_code=500)
        finally:
            db.close()


def _format_status_badge(status):
    """Helper to format status badges"""
    status_map = {
        OrderStatus.PENDING: '<span class="status-badge badge-pending">⏳ Ожидает</span>',
        OrderStatus.CONFIRMED: '<span class="status-badge badge-confirmed">✅ Подтвержден</span>',
        OrderStatus.SHIPPED: '<span class="status-badge badge-shipped">🚚 Отправлен</span>',
        OrderStatus.DELIVERED: '<span class="status-badge badge-delivered">✅ Доставлен</span>',
        OrderStatus.CANCELLED: '<span class="badge badge-danger">❌ Отменен</span>',
    }
    return status_map.get(status, str(status.value))

