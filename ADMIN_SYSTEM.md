# Marque Admin System - Two Admin Types

## Overview

The Marque e-commerce platform supports two distinct admin types, each with specific responsibilities and permissions:

1. **Order Management Admin** - Manages orders, status changes, daily statistics
2. **Website Content Admin** - Manages products, sizes, colors, website content

## Admin Types

### 📦 **Order Management Admin** (`order_management`)

**Purpose**: Handles order processing, status management, and daily business statistics

**Key Responsibilities**:

- View and manage all orders
- Change order status (preparing → delivery → completed)
- Monitor daily order statistics
- Track sales and revenue
- Manage order fulfillment process

**Default Permissions**:

- `orders.view` - View all orders
- `orders.update` - Update order information
- `orders.status_change` - Change order status
- `orders.export` - Export order data

**Key Features**:

- **Daily Statistics Dashboard**: Today's orders count, sales total, order status breakdown
- **Order Status Management**: Pending → Confirmed → Processing → Shipped → Delivered
- **Russian Status Labels**: "В обработке", "Подтвержден", "Доставлен", etc.
- **Revenue Tracking**: Daily sales totals, average order value, completion rates
- **Activity Logging**: Track all admin actions for audit trails

### 🌐 **Website Content Admin** (`website_content`)

**Purpose**: Manages website content, products, and catalog management

**Key Responsibilities**:

- Add/edit/delete products
- Manage product sizes and colors
- Upload product images and videos
- Moderate product reviews
- Configure website settings

**Default Permissions**:

- `products.create` - Create new products
- `products.update` - Update existing products
- `products.delete` - Delete products
- `products.assets` - Manage product images/videos
- `reviews.moderate` - Moderate product reviews

**Key Features**:

- **Product Management**: Full CRUD operations for products
- **Attribute Management**: Add/edit sizes, colors, categories, brands
- **Media Management**: Upload and organize product images/videos
- **Review Moderation**: Approve/reject customer reviews
- **Settings Configuration**: Currency, language, notification settings

## Database Models

### Core Admin Models

```python
# Admin user with role-based access
class Admin:
    admin_role: "order_management" | "website_content" | "super_admin"
    permissions: str  # Comma-separated permissions
    is_active: bool
    last_login: datetime

# Activity logging for audit trails
class AdminLog:
    admin_id: int
    action: str  # create, update, delete, login, etc.
    entity_type: str  # order, product, user, etc.
    entity_id: int
    description: str
    ip_address: str
```

### Order Management Models

```python
# Daily statistics for order admins
class OrderAdminStats:
    date: date
    today_orders_count: int
    today_orders_pending: int
    today_orders_processing: int
    today_orders_shipped: int
    today_orders_delivered: int
    today_orders_cancelled: int
    today_sales_total: float
    avg_order_value: float
    completion_rate: float
```

### Content Management Models

```python
# Settings for content admins
class ContentAdminSettings:
    admin_id: int
    default_currency: str  # "KGS"
    default_language: str  # "ru"
    available_sizes: List[str]
    available_colors: List[str]
    auto_generate_sku: bool
    require_product_images: bool
    notify_on_new_orders: bool

# Product attributes management
class ProductAttribute:
    attribute_type: str  # size, color, category, brand
    attribute_value: str
    display_name: str
    is_active: bool
    created_by_admin_id: int
```

## Usage Examples

### Creating Admin Users

```python
# Create Order Management Admin
order_admin = Admin(
    user_id=user.id,
    admin_role="order_management"
)
order_admin.setup_default_permissions()

# Create Website Content Admin
content_admin = Admin(
    user_id=user.id,
    admin_role="website_content"
)
content_admin.setup_default_permissions()
```

### Order Management Admin Functions

```python
# Check permissions
if order_admin.can_manage_orders():
    # View today's statistics
    stats = OrderAdminStats.query.filter_by(date=date.today()).first()
    print(f"Today's Orders: {stats.today_orders_count}")
    print(f"Sales Total: {stats.formatted_sales_total}")

    # Change order status
    order.status = OrderStatus.PROCESSING
    order.confirm_order()

    # Log activity
    AdminLog.create(
        admin_id=order_admin.id,
        action="status_change",
        entity_type="order",
        entity_id=order.id,
        description="Changed status to processing"
    )
```

### Website Content Admin Functions

```python
# Check permissions
if content_admin.can_manage_products():
    # Add new product attributes
    new_size = ProductAttribute.add_size(
        size_value="RUS 52",
        display_name="RUS 52",
        admin_id=content_admin.id
    )

    # Create new product
    product = Product(
        brand="H&M",
        title="Футболка спорт. из хлопка",
        slug="hm-sport-cotton-tshirt"
    )

    # Create SKUs with different attributes
    sku = SKU(
        product_id=product.id,
        size="RUS 48",
        color="black",
        price=2999.0
    )

    # Log activity
    AdminLog.create(
        admin_id=content_admin.id,
        action="create",
        entity_type="product",
        entity_id=product.id,
        description="Created new product"
    )
```

## Perfect Match with Admin Panel Design

This admin system perfectly supports the admin panel functionality:

### 🏠 **Главная (Dashboard)**

- Order Management Admin: Today's orders count, sales totals, revenue charts
- Website Content Admin: Product statistics, review counts, media uploads

### 📦 **Сегодняшние заказы (Today's Orders)**

- Order Management Admin: View all today's orders with status management
- Filter by status: "В обработке", "Доставлено", "Отменено"

### ⚙️ **Управление заказами (Order Management)**

- Order Management Admin: Advanced order filtering, search, date ranges
- Bulk status updates, export functionality

### 📋 **Страница заказа (Order Page)**

- Order Management Admin: Complete order details, customer info, status changes
- Order history tracking, admin notes

### 💰 **Доходы (Revenue)**

- Order Management Admin: Financial reports, sales analytics, profit tracking

### 🛍️ **Настройки (Settings)**

- Website Content Admin: Product attributes, sizes, colors, website configuration
- Order Management Admin: Order settings, notification preferences

## Role-Based Access Control

### Permission System

```python
# Check specific permissions
if admin.has_permission("orders.status_change"):
    # Allow status change

if admin.has_permission("products.create"):
    # Allow product creation

# Check role-based access
if admin.can_manage_orders():
    # Order management functions

if admin.can_manage_products():
    # Product management functions
```

### Activity Logging

All admin actions are automatically logged:

- Who performed the action
- What action was performed
- Which entity was affected
- When the action occurred
- IP address and user agent

## Benefits

1. **Clear Separation**: Each admin type has specific responsibilities
2. **Security**: Role-based permissions prevent unauthorized access
3. **Audit Trail**: Complete logging of all admin activities
4. **Scalability**: Easy to add new permissions or admin types
5. **User-Friendly**: Russian language support throughout
6. **Flexible**: Super admin can manage everything

This admin system provides a solid foundation for building the admin panel interface that matches your design requirements perfectly!
