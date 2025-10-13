# 📦 Product Creation Guide - Admin Panel

## Overview

Complete guide to adding products through the admin panel with proper SKUs, prices, images, and inventory.

## ✅ What's Fixed

### 1. **Search Functionality** - FIXED ✅

- Removed duplicate search endpoint
- Fixed field name mismatches (`price` → `price_min`/`price_max`, `main_image` → `image`, etc.)
- Added missing `brand_slug` field
- Search now works properly!

### 2. **Product Admin Form** - ENHANCED ✅

- Reordered fields for better UX (title, slug, description first)
- Added **"В топе"** (Featured) checkbox for bestsellers
- Added proper field descriptions and hints
- Added attributes field for JSON metadata
- Foreign keys (brand, category, subcategory) now show as proper dropdowns

## 🚀 How to Add a Product

### Step 1: Create the Product

1. Go to **Admin Panel** → **Каталог** → **Товары**
2. Click **"Create"** button
3. Fill in the form:

| Field           | Russian         | Required        | Example                    | Description                              |
| --------------- | --------------- | --------------- | -------------------------- | ---------------------------------------- |
| **Title**       | Название товара | ✅ Yes          | `Nike Air Max 90`          | Product name shown on website            |
| **Slug**        | URL-адрес       | ✅ Yes          | `nike-air-max-90`          | Unique URL (lowercase, use dashes)       |
| **Description** | Описание        | ✅ Yes          | `Classic running shoes...` | Product description for detail page      |
| **Brand**       | Бренд           | ✅ Yes          | Select from dropdown       | Brand (Nike, Adidas, etc.)               |
| **Category**    | Категория       | ✅ Yes          | Select from dropdown       | Main category (Мужчинам, Женщинам, etc.) |
| **Subcategory** | Подкатегория    | ✅ Yes          | Select from dropdown       | Subcategory (Футболки, Обувь, etc.)      |
| **Active**      | Активен         | ⚠️ Default: Yes | ☑️ Checked                 | Show on website?                         |
| **Featured**    | В топе          | ❌ Optional     | ☑️ Checked if bestseller   | Show in "Top Picks"?                     |
| **Attributes**  | Атрибуты (JSON) | ❌ Optional     | `{"gender":"male"}`        | JSON metadata                            |

4. Click **"Save"** to create the product

### Step 2: Add SKUs (Prices, Sizes, Colors, Stock)

⚠️ **IMPORTANT**: A product MUST have at least one SKU to be visible on the website!

1. After creating the product, go to **Каталог** → **SKU (Варианты товаров)**
2. Click **"Create"**
3. Fill in SKU details:

| Field              | Russian     | Required        | Example             | Description             |
| ------------------ | ----------- | --------------- | ------------------- | ----------------------- |
| **Product**        | Товар       | ✅ Yes          | Select your product | Link to product         |
| **SKU Code**       | Код SKU     | ✅ Yes          | `NIKE-AM90-BLK-42`  | Unique SKU identifier   |
| **Size**           | Размер      | ❌ Optional     | `42`, `M`, `L`      | Size variant            |
| **Color**          | Цвет        | ❌ Optional     | `black`, `white`    | Color variant           |
| **Price**          | Цена        | ✅ Yes          | `8500`              | Selling price in сом    |
| **Original Price** | Старая цена | ❌ Optional     | `12000`             | For discount display    |
| **Stock**          | Остаток     | ✅ Yes          | `50`                | Available quantity      |
| **Active**         | Активен     | ⚠️ Default: Yes | ☑️ Checked          | Make variant available? |

4. Click **"Save"**
5. **Repeat** for each size/color combination

**Example SKUs for Nike Air Max 90:**

- `NIKE-AM90-BLK-40` - Black, Size 40, Price 8500, Stock 10
- `NIKE-AM90-BLK-42` - Black, Size 42, Price 8500, Stock 15
- `NIKE-AM90-WHT-40` - White, Size 40, Price 9000, Stock 8
- `NIKE-AM90-WHT-42` - White, Size 42, Price 9000, Stock 12

### Step 3: Add Product Images

⚠️ **IMPORTANT**: Products without images won't look good on the website!

1. Go to **Каталог** → **Изображения товаров**
2. Click **"Create"**
3. Fill in image details:

| Field        | Russian         | Required      | Example                 | Description                |
| ------------ | --------------- | ------------- | ----------------------- | -------------------------- |
| **Product**  | Товар           | ✅ Yes        | Select your product     | Link to product            |
| **URL**      | URL изображения | ✅ Yes        | `https://...image.jpg`  | Full image URL             |
| **Type**     | Тип             | ✅ Yes        | `image`                 | Must be `image` or `video` |
| **Alt Text** | Описание        | ❌ Optional   | `Nike Air Max 90 Black` | For accessibility          |
| **Order**    | Порядок         | ⚠️ Default: 0 | `0`, `1`, `2`           | Display order (0 = main)   |

4. Click **"Save"**
5. **Add at least 3-5 images** per product (different angles, details)

**Image Tips:**

- First image (order=0) is the **main thumbnail**
- Use high-quality images (at least 800x800px)
- Show different angles, close-ups, on-model shots
- Use descriptive alt text for SEO

### Step 4: Verify on Website

1. Go to your frontend website
2. Navigate to the category/subcategory
3. **Check:**
   - ✅ Product appears in product grid
   - ✅ Main image displays correctly
   - ✅ Price shows correctly
   - ✅ Discount badge appears (if original_price set)
   - ✅ Product detail page opens
   - ✅ All images appear in gallery
   - ✅ All sizes/colors are selectable
   - ✅ Stock status is correct

## 📊 Product Checklist

Before launching a product, ensure:

- [ ] **Product created** with title, description, brand, category, subcategory
- [ ] **At least 1 SKU added** with price and stock > 0
- [ ] **At least 1 image added** (order=0 for main image)
- [ ] **Product is active** (checkbox checked)
- [ ] **SKUs are active** (checkbox checked)
- [ ] **Stock quantity** is set correctly
- [ ] **Verified on frontend** - product displays and functions correctly

## 🎯 Best Practices

### Slugs

- Use lowercase letters
- Use dashes instead of spaces
- Keep it short but descriptive
- Make it unique: `nike-air-max-90`, `adidas-stan-smith`

### SKU Codes

- Use a consistent naming pattern
- Include brand, model, color, size
- Example: `BRAND-MODEL-COLOR-SIZE` → `NIKE-AM90-BLK-42`

### Pricing

- Set **original_price** higher than **price** to show discount
- Discount percentage is calculated automatically
- All prices in сом (Kyrgyzstan) or $ (US)

### Images

- **Order 0** = Main thumbnail (shows in grid)
- **Order 1-4** = Additional images (show in detail page gallery)
- Use high-resolution images
- Include lifestyle shots, product details, different angles

### Inventory

- Set realistic stock quantities
- Out of stock products (stock=0) show "Нет в наличии"
- Products with no active SKUs won't be purchasable

## ⚠️ Common Mistakes

### 1. **Product Not Visible**

**Cause**: No active SKUs with stock > 0
**Fix**: Add at least one SKU with active=true and stock>0

### 2. **No Image Showing**

**Cause**: No ProductAsset with type='image'
**Fix**: Add at least one image with order=0

### 3. **Price Shows as "0 сом"**

**Cause**: No SKUs or all SKUs have price=0
**Fix**: Set proper prices in SKUs

### 4. **Discount Not Showing**

**Cause**: original_price not set or original_price ≤ price
**Fix**: Set original_price higher than price

### 5. **Size/Color Not Selectable**

**Cause**: SKU is inactive or stock=0
**Fix**: Set SKU active=true and stock>0

## 🔄 Quick Product Creation Flow

```
1. CREATE PRODUCT
   ↓
2. ADD SKUs (at least 1)
   - Set prices
   - Set stock
   - Set sizes/colors
   ↓
3. ADD IMAGES (at least 1)
   - Main image (order=0)
   - Gallery images (order=1,2,3...)
   ↓
4. VERIFY
   - Check frontend
   - Test add to cart
   - Verify all variants work
   ↓
5. ✅ LAUNCH!
```

## 📝 Example: Complete Product Setup

### Product: "Nike Air Max 90 Black"

**1. Product:**

- Title: `Nike Air Max 90`
- Slug: `nike-air-max-90`
- Description: `Classic running shoes with Air cushioning...`
- Brand: `Nike`
- Category: `Мужчинам`
- Subcategory: `Обувь`
- Active: ✅
- Featured: ✅

**2. SKUs:**
| SKU Code | Size | Color | Price | Original Price | Stock | Active |
|----------|------|-------|-------|----------------|-------|--------|
| NIKE-AM90-BLK-40 | 40 | black | 8500 | 12000 | 10 | ✅ |
| NIKE-AM90-BLK-42 | 42 | black | 8500 | 12000 | 15 | ✅ |
| NIKE-AM90-BLK-44 | 44 | black | 8500 | 12000 | 8 | ✅ |

**3. Images:**
| URL | Type | Order | Alt Text |
|-----|------|-------|----------|
| https://.../nike-am90-main.jpg | image | 0 | Nike Air Max 90 Black |
| https://.../nike-am90-side.jpg | image | 1 | Nike Air Max 90 Side View |
| https://.../nike-am90-back.jpg | image | 2 | Nike Air Max 90 Back View |

**Result:**

- ✅ Product shows in catalog with main image
- ✅ Price: 8500 сом (discount: -29%)
- ✅ 3 sizes available
- ✅ Gallery with 3 images
- ✅ "В топе" badge on frontend

## 🆘 Need Help?

Check the admin logs:

1. Go to **Система** → **Логи активности**
2. Filter by your admin user
3. Look for errors during product/SKU/image creation

---

**Status**: ✅ **Ready to use!**

All admin panel forms are now properly configured for easy product management!
