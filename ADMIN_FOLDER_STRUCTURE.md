# Marque Admin System - Separate Folder Structure

## Overview

The admin system is now organized into separate folders for each admin type, providing clear separation of concerns and better maintainability.

## Folder Structure

```
src/app_01/models/admins/
├── __init__.py                           # Main admin imports
├── admin.py                              # Core Admin model
├── admin_log.py                          # Admin activity logging
├── order_management/                     # Order Management Admin models
│   ├── __init__.py
│   ├── order_admin_stats.py              # Daily order statistics
│   └── order_management_admin.py         # Order management permissions & settings
└── website_content/                      # Website Content Admin models
    ├── __init__.py
    ├── content_admin_settings.py         # Content admin settings
    └── website_content_admin.py          # Content management permissions & settings
```

## 📦 Order Management Admin Folder

### Purpose

Handles all order-related administrative functions including order processing, status management, and daily business statistics.

### Models

#### `OrderAdminStats`

**Purpose**: Daily statistics and analytics for order management

**Key Features**:

- Today's orders count and breakdown by status
- Sales totals and revenue tracking
- Performance metrics (completion rate, average order value)
- Russian status labels for UI display

**Example Usage**:

```python
# Get today's statistics
stats = OrderAdminStats.query.filter_by(date=date.today()).first()
print(f"Today's Orders: {stats.today_orders_count}")
print(f"Sales Total: {stats.formatted_sales_total}")
print(f"Orders by Status: {stats.orders_status_summary}")
```

#### `OrderManagementAdmin`

**Purpose**: Order management admin permissions and settings

**Key Features**:

- Order processing permissions (export, bulk update, cancel, refund)
- Dashboard preferences (refresh interval, notifications)
- Order workflow configuration (auto-confirm, manual confirmation)
- Notification settings for order events

**Example Usage**:

```python
# Setup order management admin
order_admin = OrderManagementAdmin(admin_id=admin.id)
order_admin.enable_full_order_management()
order_admin.setup_dashboard_preferences(refresh_interval=30)
order_admin.configure_order_processing(auto_confirm=False)
```

### Key Capabilities

- ✅ View and manage all orders
- ✅ Change order status (pending → processing → shipped → delivered)
- ✅ Export order data
- ✅ Bulk order operations
- ✅ Daily statistics and analytics
- ✅ Order cancellation and refunds
- ✅ Dashboard customization
- ✅ Notification management

## 🌐 Website Content Admin Folder

### Purpose

Handles all website content management including products, media, attributes, and content settings.

### Models

#### `ContentAdminSettings`

**Purpose**: Global content management settings and configurations

**Key Features**:

- Default currency and language settings
- Product attribute management (sizes, colors)
- Media upload settings and limits
- Review moderation settings
- SEO and notification preferences

**Example Usage**:

```python
# Setup content admin settings
settings = ContentAdminSettings(admin_id=admin.id)
settings.default_currency = "KGS"
settings.available_sizes = ["RUS 40", "RUS 42", "RUS 44", "RUS 46"]
settings.available_colors = ["black", "white", "red", "blue"]
settings.setup_review_settings(auto_approve=False)
```

#### `WebsiteContentAdmin`

**Purpose**: Website content admin permissions and capabilities

**Key Features**:

- Product management permissions (create, edit, delete)
- Media management (upload images/videos, file size limits, formats)
- Review moderation capabilities
- SEO and content management permissions
- Category and taxonomy management

**Example Usage**:

```python
# Setup website content admin
content_admin = WebsiteContentAdmin(admin_id=admin.id)
content_admin.enable_full_content_management()
content_admin.setup_media_settings(max_size_mb=10)
content_admin.setup_seo_settings(auto_generate_slugs=True)
```

### Key Capabilities

- ✅ Create, edit, and delete products
- ✅ Manage product attributes (sizes, colors, categories, brands)
- ✅ Upload and manage product media (images/videos)
- ✅ Moderate product reviews
- ✅ Manage SEO settings and meta descriptions
- ✅ Create and manage categories
- ✅ Configure website settings
- ✅ Set up notification preferences

## 🔧 Import Structure

### Main Admin Imports

```python
from src.app_01.models.admins import (
    Admin, AdminLog,
    OrderAdminStats, OrderManagementAdmin,
    ContentAdminSettings, WebsiteContentAdmin
)
```

### Order Management Specific Imports

```python
from src.app_01.models.admins.order_management import (
    OrderAdminStats, OrderManagementAdmin
)
```

### Website Content Specific Imports

```python
from src.app_01.models.admins.website_content import (
    ContentAdminSettings, WebsiteContentAdmin
)
```

## 📊 Usage Examples

### Creating Order Management Admin

```python
# Create user and admin
user = User(email="order.admin@marque.com", username="order_admin")
admin = Admin(user_id=user.id, admin_role="order_management")

# Setup order management specific settings
order_mgmt_admin = OrderManagementAdmin(admin_id=admin.id)
order_mgmt_admin.enable_full_order_management()
order_mgmt_admin.setup_dashboard_preferences()

# Create daily statistics
stats = OrderAdminStats(
    date=date.today(),
    today_orders_count=25,
    today_sales_total=125000.0
)
```

### Creating Website Content Admin

```python
# Create user and admin
user = User(email="content.admin@marque.com", username="content_admin")
admin = Admin(user_id=user.id, admin_role="website_content")

# Setup content management settings
content_admin = WebsiteContentAdmin(admin_id=admin.id)
content_admin.enable_full_content_management()
content_admin.setup_media_settings(max_size_mb=15)

# Setup global content settings
settings = ContentAdminSettings(admin_id=admin.id)
settings.available_sizes = ["RUS 40", "RUS 42", "RUS 44", "RUS 46", "RUS 48"]
settings.available_colors = ["black", "white", "red", "blue", "green"]
```

### Checking Admin Capabilities

```python
# Order Management Admin
if order_admin.can_manage_orders():
    # View today's statistics
    stats = OrderAdminStats.query.filter_by(date=date.today()).first()

    # Change order status
    order.status = OrderStatus.PROCESSING
    order.confirm_order()

    # Log activity
    AdminLog.create(admin_id=admin.id, action="status_change", ...)

# Website Content Admin
if content_admin.can_manage_products():
    # Create new product
    product = Product(brand="H&M", title="Футболка спорт. из хлопка")

    # Add new size
    new_size = ProductAttribute.add_size(size_value="RUS 50")

    # Upload product image
    asset = ProductAsset(product_id=product.id, url="...", type="image")

    # Log activity
    AdminLog.create(admin_id=admin.id, action="create", ...)
```

## 🎯 Benefits of Separate Folders

### 1. **Clear Separation of Concerns**

- Order management logic is isolated from content management
- Easy to locate and modify specific admin functionality
- Reduced coupling between different admin types

### 2. **Better Maintainability**

- Changes to order management don't affect content management
- Each folder can be developed and tested independently
- Clear ownership of different admin responsibilities

### 3. **Scalability**

- Easy to add new models to specific admin folders
- Can create sub-folders as functionality grows
- Supports team-based development

### 4. **Code Organization**

- Related functionality is grouped together
- Easy to understand admin system structure
- Clear import paths for different admin types

### 5. **Team Collaboration**

- Multiple developers can work on different admin folders
- Clear boundaries for code reviews
- Easy to assign responsibilities

## 🔐 Permission System

Each admin type has specific permissions:

### Order Management Admin Permissions

- `orders.view` - View all orders
- `orders.update` - Update order information
- `orders.status_change` - Change order status
- `orders.export` - Export order data
- `orders.bulk_update` - Bulk order operations
- `orders.cancel` - Cancel orders
- `orders.refund` - Process refunds

### Website Content Admin Permissions

- `products.create` - Create new products
- `products.update` - Update existing products
- `products.delete` - Delete products
- `products.assets` - Manage product media
- `reviews.moderate` - Moderate reviews
- `categories.manage` - Manage categories
- `attributes.manage` - Manage sizes, colors, brands
- `seo.manage` - Manage SEO settings

## 🚀 Perfect Match with Admin Panel

This folder structure perfectly supports the admin panel design:

- **Order Management Folder** → "Сегодняшние заказы", "Управление заказами", "Доходы"
- **Website Content Folder** → Product management, size/color management, content settings

The separate folders make it easy to build dedicated API endpoints and UI components for each admin type while maintaining clean code organization!
