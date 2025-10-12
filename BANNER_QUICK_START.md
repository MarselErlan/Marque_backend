# 🎨 Banner System Quick Start Guide

## ✅ System Status

**All banner features are working correctly!**

- ✅ Database structure is correct
- ✅ Banners save to database properly
- ✅ Admin panel has full banner management

---

## 📊 Current State

### Database

- **Banners in Database**: 3 sample banners
- **Tables**: `banners` table exists with all columns
- **Enum Type**: Fixed (hero, promo, category)

### Sample Banners

1. **Summer Sale 2025** (hero) - Active, Order: 1
2. **New Arrivals** (promo) - Active, Order: 2
3. **Accessories** (category) - Active, Order: 3

---

## 🚀 Quick Start

### 1. Start the Main API Server

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 -m uvicorn src.app_01.main:app --reload --port 8000
```

### 2. Start the Admin Panel (Separate Terminal)

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 main_admin.py
```

---

## 🔌 API Endpoints

### Public Endpoints (No Auth)

#### Get All Banners (Grouped by Type)

```bash
curl http://localhost:8000/api/v1/banners/
```

**Response:**

```json
{
  "hero_banners": [...],
  "promo_banners": [...],
  "category_banners": [...],
  "total": 3
}
```

#### Get Hero Banners Only

```bash
curl http://localhost:8000/api/v1/banners/hero
```

#### Get Promo Banners Only

```bash
curl http://localhost:8000/api/v1/banners/promo
```

#### Get Category Banners Only

```bash
curl http://localhost:8000/api/v1/banners/category
```

### Admin Endpoints (Require Auth)

#### Get All Banners (Including Inactive)

```bash
curl http://localhost:8000/api/v1/banners/admin/all \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Create Banner

```bash
curl -X POST http://localhost:8000/api/v1/banners/admin/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Banner",
    "subtitle": "Subtitle here",
    "image_url": "https://example.com/banner.jpg",
    "banner_type": "hero",
    "cta_text": "Shop Now",
    "cta_url": "/products",
    "is_active": true,
    "display_order": 1
  }'
```

---

## 🎛️ Admin Panel

### Access

```
http://localhost:8001/admin
```

### Default Credentials

```
Username: admin
Password: admin123
```

### Banner Management

1. Navigate to: **Баннеры** (under "🎨 Контент" section)
2. Click **Create** to add new banner
3. Fill in the form:

   - ✅ **Title** (required)
   - ✅ **Image URL** (required)
   - ✅ **Banner Type** (required): hero, promo, or category
   - Optional: Subtitle, Description, CTA, Dates, Display Order

4. **Edit**: Click on any banner to modify
5. **Delete**: Click delete button on any banner

---

## 📝 Banner Fields Explained

| Field              | Type     | Required | Description                       |
| ------------------ | -------- | -------- | --------------------------------- |
| `title`            | string   | ✅       | Main banner title                 |
| `subtitle`         | string   | ❌       | Secondary text                    |
| `description`      | string   | ❌       | Full description                  |
| `image_url`        | string   | ✅       | Desktop image URL                 |
| `mobile_image_url` | string   | ❌       | Mobile-optimized image            |
| `banner_type`      | enum     | ✅       | hero/promo/category               |
| `cta_text`         | string   | ❌       | Button text ("Shop Now")          |
| `cta_url`          | string   | ❌       | Button link URL                   |
| `is_active`        | boolean  | ❌       | Show/hide banner (default: true)  |
| `display_order`    | integer  | ❌       | Order (lower = first, default: 0) |
| `start_date`       | datetime | ❌       | When to start showing             |
| `end_date`         | datetime | ❌       | When to stop showing              |

---

## 🎯 Banner Types

### Hero Banners

- **Purpose**: Main carousel on homepage
- **Type**: `hero`
- **Typical Size**: 1920x600px
- **Example**: Large promotional banners

### Promo Banners

- **Purpose**: Promotional sections
- **Type**: `promo`
- **Typical Size**: 1200x400px
- **Example**: Sale announcements, special offers

### Category Banners

- **Purpose**: Category showcases
- **Type**: `category`
- **Typical Size**: 800x600px
- **Example**: Collection highlights, category features

---

## 🔒 Authentication

### Get Admin Token

1. **Login to admin panel** at http://localhost:8001/admin
2. Or **use API authentication**:

```bash
# For admin endpoints, you need to authenticate first
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone": "+996XXXXXXXXX"}'
```

---

## ✅ Verification Checklist

- [x] Database table exists
- [x] All columns present
- [x] Enum type fixed (lowercase)
- [x] CRUD operations work
- [x] API endpoints accessible
- [x] Admin panel integrated
- [x] Sample banners added
- [x] Filtering works
- [x] Date-based activation works

---

## 🐛 Troubleshooting

### Issue: "enum type mismatch"

**Solution**: Already fixed! Run `python3 fix_banner_enum.py` if needed.

### Issue: "No banners showing"

**Checklist**:

- Banner is `is_active = true`
- No `start_date` in the future
- No `end_date` in the past
- API endpoint is correct

### Issue: "Admin panel not loading"

**Solution**:

```bash
# Make sure admin panel is running on port 8001
python3 main_admin.py
```

### Issue: "Cannot create banner"

**Checklist**:

- All required fields provided (title, image_url, banner_type)
- Valid banner_type: "hero", "promo", or "category"
- Valid image URL format

---

## 📚 Additional Resources

- **Full Documentation**: `BANNER_API_GUIDE.md`
- **Audit Report**: `BANNER_SYSTEM_AUDIT_REPORT.md`
- **Test Script**: `test_banner_system.py`
- **Fix Script**: `fix_banner_enum.py`

---

## 🎉 Success!

Your banner system is **fully functional** and ready to use!

**Next Steps**:

1. ✅ Upload real banner images
2. ✅ Create production banners
3. ✅ Test with frontend
4. ✅ Set up scheduled campaigns

---

**Last Updated**: October 12, 2025  
**Status**: ✅ Production Ready
