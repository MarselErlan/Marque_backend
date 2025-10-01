# 🎨 Banner API Guide

## Overview

The Banner API allows you to manage main page banners for your e-commerce platform. There are two types of banners:

- **SALE** - Promotional/discount banners
- **MODEL** - Product/model showcase banners

---

## 📋 Banner Model

```json
{
  "id": 1,
  "title": "Summer Sale - Up to 80% Off",
  "description": "Huge discounts on selected items!",
  "image_url": "https://example.com/banners/summer-sale.jpg",
  "banner_type": "sale",
  "link_url": "/products?category=sale",
  "is_active": true,
  "display_order": 1,
  "start_date": "2024-06-01T00:00:00Z",
  "end_date": "2024-06-30T23:59:59Z",
  "created_at": "2024-05-15T10:00:00Z",
  "updated_at": "2024-05-15T10:00:00Z"
}
```

---

## 🌐 Public Endpoints (No Auth Required)

### 1. Get All Active Banners

```
GET /api/v1/banners/
```

**Response:**

```json
{
  "sale_banners": [...],
  "model_banners": [...],
  "total": 6
}
```

### 2. Get Only Sale Banners

```
GET /api/v1/banners/sale
```

**Response:**

```json
[
  {
    "id": 1,
    "title": "Summer Sale",
    ...
  }
]
```

### 3. Get Only Model Banners

```
GET /api/v1/banners/model
```

**Response:**

```json
[
  {
    "id": 4,
    "title": "Spring Collection 2024",
    ...
  }
]
```

---

## 🔒 Admin Endpoints (Auth Required)

### 4. Get All Banners (Including Inactive)

```
GET /api/v1/banners/admin/all
```

**Headers:**

```
Authorization: Bearer {your_token}
```

### 5. Create New Banner

```
POST /api/v1/banners/admin/create
```

**Headers:**

```
Authorization: Bearer {your_token}
Content-Type: application/json
```

**Body:**

```json
{
  "title": "Black Friday Sale",
  "description": "Amazing deals for Black Friday",
  "image_url": "https://example.com/banners/black-friday.jpg",
  "banner_type": "sale",
  "link_url": "/products?category=black-friday",
  "is_active": true,
  "display_order": 1,
  "start_date": "2024-11-29T00:00:00Z",
  "end_date": "2024-12-01T23:59:59Z"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Banner 'Black Friday Sale' created successfully",
  "banner": {...}
}
```

### 6. Get Banner by ID

```
GET /api/v1/banners/admin/{banner_id}
```

**Headers:**

```
Authorization: Bearer {your_token}
```

### 7. Update Banner

```
PUT /api/v1/banners/admin/{banner_id}
```

**Headers:**

```
Authorization: Bearer {your_token}
Content-Type: application/json
```

**Body:** (all fields optional)

```json
{
  "title": "Updated Title",
  "is_active": false,
  "display_order": 5
}
```

### 8. Delete Banner

```
DELETE /api/v1/banners/admin/{banner_id}
```

**Headers:**

```
Authorization: Bearer {your_token}
```

**Response:**

```json
{
  "success": true,
  "message": "Banner 'Black Friday Sale' deleted successfully",
  "banner": null
}
```

### 9. Toggle Banner Status (Active/Inactive)

```
PATCH /api/v1/banners/admin/{banner_id}/toggle
```

**Headers:**

```
Authorization: Bearer {your_token}
```

**Response:**

```json
{
  "success": true,
  "message": "Banner 'Summer Sale' deactivated successfully",
  "banner": {...}
}
```

---

## 🧪 Testing Examples

### Using cURL

#### Get All Banners (Public)

```bash
curl http://localhost:8000/api/v1/banners/
```

#### Create Banner (Admin)

```bash
curl -X POST http://localhost:8000/api/v1/banners/admin/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Sale Banner",
    "description": "Check out our latest deals",
    "image_url": "https://example.com/banner.jpg",
    "banner_type": "sale",
    "is_active": true,
    "display_order": 1
  }'
```

#### Toggle Banner

```bash
curl -X PATCH http://localhost:8000/api/v1/banners/admin/1/toggle \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔑 Key Features

1. **Auto Date Filtering** - Banners automatically show/hide based on `start_date` and `end_date`
2. **Display Order** - Control banner sequence with `display_order` (lower = first)
3. **Active Status** - Instantly toggle banners on/off with `is_active`
4. **Two Types** - Separate sale promotions from model showcases
5. **Smart Filtering** - Only currently active banners shown to public

---

## 💡 Use Cases

### Sale Banners

- Flash sales
- Seasonal promotions
- Discount campaigns
- Limited-time offers

### Model Banners

- New collection launches
- Product showcases
- Brand campaigns
- Lookbook galleries

---

## 📊 Database Migration

The migration has been created and applied to both KG and US databases:

```bash
alembic/versions/6994966bbf08_add_banners_table_for_main_page.py
```

---

## 🚀 Next Steps

1. **Add banners via API** or admin panel
2. **Upload images** to CDN/storage
3. **Test on frontend** - fetch from `/api/v1/banners/`
4. **Monitor performance** - check which banners get clicks
5. **Schedule campaigns** - use start_date/end_date for automation

---

## 📝 Notes

- Banner images should be optimized (WebP format recommended)
- Recommended banner size: 1920x600px for desktop, 750x1000px for mobile
- Use `link_url` to direct users to specific products/categories
- Lower `display_order` numbers appear first
- Inactive banners won't show even if dates are valid
