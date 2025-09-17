# SQLAdmin Setup for Website Content Management

## Overview

SQLAdmin provides a beautiful, modern admin interface for managing website content. It's perfect for website content admins who need to manage products, attributes, media files, and reviews.

## Features

### 🎨 **Beautiful Modern Interface**

- Clean, responsive design
- Russian language interface
- FontAwesome icons
- Custom branding support

### 🛍️ **Product Management**

- Create, edit, and delete products
- Manage product information (brand, title, description)
- Set product attributes and metadata
- Bulk operations support

### 🏷️ **SKU Management**

- Create product variants with different sizes and colors
- Set individual prices and stock levels
- Manage product availability
- Bulk SKU operations

### 🖼️ **Media Management**

- Upload and manage product images
- Support for videos and other media
- Alt text for accessibility
- Order management for media display

### 📝 **Attribute Management**

- Manage product sizes (RUS 40, 42, 44, 46, etc.)
- Manage product colors (черный, белый, красный, etc.)
- Manage product brands (H&M, Zara, etc.)
- Manage product categories
- Sort order and display names

### ⭐ **Review Management**

- Moderate customer reviews
- Approve/reject reviews
- Manage review ratings
- Review analytics

### 👥 **User Management**

- View and manage user accounts
- User profile information
- Account status management
- User activity tracking

### 📊 **Activity Logging**

- Complete audit trail of admin actions
- IP address tracking
- Action descriptions in Russian
- Timestamp logging

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Sample Data

```bash
python SQLADMIN_EXAMPLES.py
```

### 3. Run Admin Interface

```bash
python main_admin.py
```

### 4. Access Interface

- URL: http://localhost:8001/admin
- Username: `content_admin`
- Password: `admin123`

## Admin Sections

### 🛍️ **Товары (Products)**

**Purpose**: Manage product catalog

**Features**:

- Product creation and editing
- Brand and title management
- Description and metadata
- Product attributes configuration
- Search and filtering

**Columns**:

- ID, Бренд, Название, URL-адрес, Продано, Рейтинг, Отзывов, Создано

### 🏷️ **Артикулы (SKUs)**

**Purpose**: Manage product variants

**Features**:

- Size and color variants
- Price and stock management
- SKU code generation
- Availability control

**Columns**:

- ID, Код артикула, Размер, Цвет, Цена, Остаток, Активен

### 🖼️ **Медиа файлы (Product Assets)**

**Purpose**: Manage product media

**Features**:

- Image and video uploads
- Alt text for accessibility
- Display order management
- Media type filtering

**Columns**:

- ID, ID товара, Тип, URL файла, Альтернативный текст, Порядок

### 📝 **Атрибуты товаров (Product Attributes)**

**Purpose**: Manage product attributes

**Features**:

- Size management (RUS 40, 42, 44, 46)
- Color management (черный, белый, красный)
- Brand management (H&M, Zara)
- Category management
- Sort order configuration

**Columns**:

- ID, Тип атрибута, Значение, Отображаемое имя, Порядок сортировки, Активен

### ⭐ **Отзывы (Reviews)**

**Purpose**: Moderate customer reviews

**Features**:

- Review approval/rejection
- Rating management
- Review text moderation
- User and product linking

**Columns**:

- ID, ID товара, ID пользователя, Оценка, Создано

### 👥 **Пользователи (Users)**

**Purpose**: Manage user accounts

**Features**:

- User profile management
- Account status control
- Email verification
- User activity tracking

**Columns**:

- ID, Имя пользователя, Email, Полное имя, Активен, Подтвержден, Создан

### 📊 **Журнал действий (Admin Log)**

**Purpose**: Audit admin activities

**Features**:

- Complete action history
- IP address tracking
- Action descriptions
- Timestamp logging

**Columns**:

- ID, ID администратора, Действие, Тип объекта, ID объекта, Время

## Authentication

### Default Credentials

- **Username**: `content_admin`
- **Password**: `admin123`

### Custom Authentication

The authentication system can be customized in `website_content_admin.py`:

```python
class WebsiteContentAuthenticationBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        # Custom login logic
        # Verify credentials against database
        # Check admin permissions
        pass
```

## Customization

### Branding

- Logo: Replace `/static/logo.png`
- Favicon: Replace `/static/favicon.ico`
- Title: Modify in `admin_app.py`

### Permissions

- Role-based access control
- Granular permissions per admin type
- Custom permission checks

### Styling

- Custom CSS support
- Theme customization
- Icon management

## API Integration

### Database Models

All models are automatically available through SQLAdmin:

- `Product`, `SKU`, `ProductAsset`
- `ProductAttribute`, `Review`, `User`
- `Admin`, `AdminLog`

### Custom Views

Create custom dashboard views:

```python
class CustomDashboard(BaseView, name="Панель управления"):
    name = "Панель управления"
    icon = "fa-solid fa-chart-pie"

    async def index(self, request: Request):
        # Custom dashboard logic
        pass
```

## Security Features

### Authentication

- Session-based authentication
- Secure token generation
- Login/logout functionality

### Authorization

- Role-based access control
- Permission-based features
- Admin activity logging

### Data Protection

- SQL injection protection
- XSS protection
- CSRF protection

## Usage Examples

### Managing Products

1. Go to "Товары" section
2. Click "Создать" to add new product
3. Fill in product information
4. Set attributes and metadata
5. Save product

### Managing Attributes

1. Go to "Атрибуты товаров" section
2. Add new sizes: "RUS 48", "RUS 50"
3. Add new colors: "Розовый", "Серый"
4. Set display names and sort order
5. Activate/deactivate attributes

### Managing SKUs

1. Go to "Артикулы" section
2. Create new SKU for product
3. Set size, color, price, stock
4. Generate SKU code
5. Set availability status

### Moderating Reviews

1. Go to "Отзывы" section
2. View pending reviews
3. Approve/reject reviews
4. Check review content
5. Manage ratings

## Benefits

### 🎯 **Perfect for Website Content Admins**

- Intuitive interface for non-technical users
- Russian language support
- Visual product management

### 🚀 **Fast and Efficient**

- Quick product creation
- Bulk operations
- Search and filtering
- Responsive design

### 🔒 **Secure and Reliable**

- Role-based access control
- Activity logging
- Data validation
- Error handling

### 📱 **Modern and User-Friendly**

- Clean interface design
- Mobile responsive
- Easy navigation
- Helpful tooltips

This SQLAdmin interface provides everything a website content admin needs to manage the Marque e-commerce platform effectively!
