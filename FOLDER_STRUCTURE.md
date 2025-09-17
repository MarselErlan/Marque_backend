# Marque E-commerce Backend - Folder Structure

## Overview

The project is now organized into separate folders for better maintainability and separation of concerns. Each folder contains related models and functionality.

## Folder Structure

```
src/app_01/models/
├── __init__.py                 # Main imports from all folders
├── users/                      # User-related models
│   ├── __init__.py
│   ├── user.py                 # User authentication & management
│   └── interaction.py          # User behavior tracking
├── products/                   # Product catalog models
│   ├── __init__.py
│   ├── product.py              # Main product model
│   ├── sku.py                  # Stock Keeping Units
│   ├── product_asset.py        # Product images/videos
│   └── review.py               # Product reviews & ratings
├── orders/                     # Order management models
│   ├── __init__.py
│   ├── cart_order.py           # Shopping cart items
│   ├── order.py                # Main order model
│   ├── order_item.py           # Individual items in orders
│   └── order_status_history.py # Order status tracking
└── admins/                     # Admin management models
    ├── __init__.py
    ├── admin.py                # Admin user model
    └── admin_log.py            # Admin activity logging
```

## Folder Details

### 📁 **users/** - User Management

**Purpose**: Handle user authentication, profiles, and behavior tracking

**Models**:

- **`User`**: Core user model with authentication fields
- **`Interaction`**: Track user behavior (views, clicks, searches)

**Key Features**:

- User authentication and profile management
- User behavior analytics
- Anonymous user tracking support
- Admin profile relationship

### 📁 **products/** - Product Catalog

**Purpose**: Manage product catalog, variants, media, and reviews

**Models**:

- **`Product`**: Core product information with enhanced methods
- **`SKU`**: Product variants (sizes, colors, prices)
- **`ProductAsset`**: Product images and videos
- **`Review`**: Customer reviews and ratings

**Key Features**:

- Flexible product catalog with variants
- Rich media support (images/videos)
- Review system with Russian text support
- Stock management and pricing
- Product rating calculations

### 📁 **orders/** - Order Management

**Purpose**: Handle shopping cart, orders, and order processing

**Models**:

- **`CartOrder`**: Shopping cart items
- **`Order`**: Main order model with full order lifecycle
- **`OrderItem`**: Individual products in orders
- **`OrderStatusHistory`**: Track order status changes

**Key Features**:

- Complete order lifecycle management
- Status tracking with Russian labels
- Order history and audit trail
- Cart to order conversion
- Admin order management

### 📁 **admins/** - Admin Management

**Purpose**: Admin user management and activity logging

**Models**:

- **`Admin`**: Admin user model with roles and permissions
- **`AdminLog`**: Track admin activities and changes

**Key Features**:

- Role-based admin access (admin, super_admin, manager)
- Permission management system
- Activity logging for audit trails
- Admin profile linked to user accounts

## Benefits of This Structure

### 🎯 **Clear Separation of Concerns**

- Each folder has a specific business domain
- Easy to locate related functionality
- Reduced coupling between different areas

### 🔧 **Maintainability**

- Changes to one area don't affect others
- Easy to add new features to specific domains
- Clear ownership of different parts of the system

### 👥 **Team Collaboration**

- Multiple developers can work on different folders
- Clear boundaries for code reviews
- Easier to assign responsibilities

### 🚀 **Scalability**

- Easy to add new models to appropriate folders
- Can create sub-folders as domains grow
- Supports microservice extraction if needed

## Import Structure

### Main Import

```python
from src.app_01.models import User, Product, Order, Admin
```

### Folder-Specific Imports

```python
# Users
from src.app_01.models.users import User, Interaction

# Products
from src.app_01.models.products import Product, SKU, Review

# Orders
from src.app_01.models.orders import Order, OrderStatus, CartOrder

# Admins
from src.app_01.models.admins import Admin, AdminLog
```

## Model Relationships

### Cross-Folder Relationships

- **User** (users/) ↔ **Review** (products/)
- **User** (users/) ↔ **Order** (orders/)
- **User** (users/) ↔ **Admin** (admins/)
- **Product** (products/) ↔ **OrderItem** (orders/)
- **Admin** (admins/) ↔ **Order** (orders/)

### Internal Relationships

- **Product** ↔ **SKU** ↔ **ProductAsset** ↔ **Review**
- **Order** ↔ **OrderItem** ↔ **OrderStatusHistory**
- **Admin** ↔ **AdminLog**

## Usage Examples

### Creating a Complete Order Flow

```python
from src.app_01.models import User, Product, SKU, Order, OrderItem, OrderStatus

# User places order
user = session.query(User).first()
product = session.query(Product).first()
sku = session.query(SKU).filter(SKU.product_id == product.id).first()

# Create order
order = Order(
    user=user,
    order_number="#1021",
    customer_name=user.full_name,
    customer_phone="+996 700 123 456",
    delivery_address="г. Чуйская, 17",
    subtotal=2999.0,
    total_amount=2999.0
)

# Add order item
order_item = OrderItem.create_from_sku(order.id, sku, quantity=1)
order.order_items.append(order_item)

# Update order status
order.confirm_order()
```

### Admin Activity Tracking

```python
from src.app_01.models import Admin, AdminLog

# Admin performs action
admin = session.query(Admin).first()
admin_log = AdminLog(
    admin=admin,
    action="update",
    entity_type="order",
    entity_id=order.id,
    description="Updated order status to confirmed"
)
```

This folder structure provides a solid foundation for building a scalable e-commerce platform with clear organization and maintainable code.
