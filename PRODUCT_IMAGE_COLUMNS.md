# Product Image Columns - Pillow Integration

## 🎯 Overview

The Product model now has **direct image columns** instead of relying only on the ProductAsset relationship. Images are processed with **Pillow** and stored directly in the Product table.

---

## 📊 New Database Columns

### 1. `main_image` (String, 500 chars)

- **Purpose:** Stores the URL of the main product image
- **Type:** `VARCHAR(500)`
- **Nullable:** Yes
- **Usage:** Primary product image shown first everywhere

### 2. `additional_images` (JSON Array)

- **Purpose:** Stores an array of additional product image URLs
- **Type:** `JSON`
- **Nullable:** Yes
- **Usage:** Secondary product images (up to 5 recommended)
- **Format:** `["url1.jpg", "url2.jpg", "url3.jpg"]`

---

## 🗄️ Database Migration

**Migration file:** `alembic/versions/8f7297e45fcb_add_product_image_columns.py`

**Applied to:**

- ✅ Local database (KG)
- ⏳ Production database (will apply on next Railway deployment)

**SQL:**

```sql
-- Add columns
ALTER TABLE products ADD COLUMN main_image VARCHAR(500);
ALTER TABLE products ADD COLUMN additional_images JSON;
```

---

## 📝 Admin Panel Form

### Upload Fields:

1. **"Главное изображение" (Main Image)**

   - Single file upload
   - Replaces existing main image
   - Processed with Pillow (resized to 500x500px, optimized)
   - Saved to `/uploads/products/`
   - URL stored in `Product.main_image`

2. **"Дополнительные изображения" (Additional Images)**
   - Multiple file upload (up to 5 images)
   - Appends to existing additional images
   - Each processed with Pillow
   - URLs stored as JSON array in `Product.additional_images`

---

## 📸 How It Works

### Product Creation Flow:

```
1. User fills product form
   ↓
2. User uploads main image (JPEG/PNG)
   ↓
3. User uploads additional images (up to 5)
   ↓
4. Click "Save"
   ↓
5. Pillow validates each image
   ↓
6. Images resized to 500x500px
   ↓
7. Images optimized for web
   ↓
8. Images saved to /uploads/products/
   ↓
9. Image URLs saved to Product columns:
   - main_image: "/uploads/products/abc123.jpg"
   - additional_images: ["/uploads/products/def456.jpg", "/uploads/products/ghi789.jpg"]
   ↓
10. Product saved to database ✅
```

### Product Update Flow:

```
1. Edit existing product
   ↓
2. Upload new main image (optional)
   → Replaces old main_image
   ↓
3. Upload new additional images (optional)
   → Appends to existing additional_images array
   ↓
4. Click "Save"
   ↓
5. Images processed with Pillow
   ↓
6. Product.main_image updated (if new image uploaded)
7. Product.additional_images appended (if new images uploaded)
   ↓
8. Changes saved to database ✅
```

---

## 🎨 Admin Panel Display

### List View (Products Table):

```
┌────┬────────────┬─────────────────┬─────────┬──────────┐
│ ID │ [Thumbnail]│ Title           │ Brand   │ Category │
├────┼────────────┼─────────────────┼─────────┼──────────┤
│ 1  │   [IMG]    │ Nike Air Max    │ Nike    │ Shoes    │
│ 2  │ Нет фото   │ Adidas Jacket   │ Adidas  │ Jackets  │
└────┴────────────┴─────────────────┴─────────┴──────────┘
```

- Shows 80x80px thumbnail from `main_image`
- Shows "Нет фото" badge if no main image

### Detail View (Product Details):

**Main Image Section:**

- Displays large preview of `main_image`
- Shows "Нет фото" if empty

**Additional Images Section:**

- Grid of all images from `additional_images` array
- Each image shown at 150x150px
- Numbered: "Изображение 1", "Изображение 2", etc.
- Shows "Нет дополнительных изображений" if array is empty

---

## 💾 Data Structure

### Example Product Record:

```json
{
  "id": 123,
  "title": "Nike Running Shoes",
  "slug": "nike-running-shoes",
  "brand_id": 5,
  "category_id": 10,
  "subcategory_id": 25,
  "main_image": "/uploads/products/a1b2c3d4.jpg",
  "additional_images": [
    "/uploads/products/e5f6g7h8.jpg",
    "/uploads/products/i9j0k1l2.jpg",
    "/uploads/products/m3n4o5p6.jpg"
  ],
  "price": 149.99,
  "is_active": true,
  ...
}
```

### Database Storage:

**`main_image` column:**

```
/uploads/products/a1b2c3d4.jpg
```

**`additional_images` column:**

```json
[
  "/uploads/products/e5f6g7h8.jpg",
  "/uploads/products/i9j0k1l2.jpg",
  "/uploads/products/m3n4o5p6.jpg"
]
```

---

## 🔧 Image Processing (Pillow)

### Validation:

- ✅ Checks if file is a valid image
- ✅ Uses `PIL.Image.open()` and `verify()`
- ❌ Rejects corrupted or non-image files

### Resizing:

- **Target size:** 500x500px (medium preset)
- **Maintains aspect ratio:** No
- **Crop:** Centered crop if needed

### Optimization:

- **JPEG quality:** 85%
- **Format:** JPEG (smaller file size)
- **Progressive:** Yes
- **Result:** Typically 50-70% file size reduction

### Unique Filenames:

- Generated by `image_uploader`
- Format: `{random_hash}.jpg`
- Example: `a1b2c3d4e5f6g7h8.jpg`

---

## 📂 File Storage

### Directory Structure:

```
/uploads/
  └── products/
      ├── a1b2c3d4.jpg  (main image)
      ├── e5f6g7h8.jpg  (additional image 1)
      ├── i9j0k1l2.jpg  (additional image 2)
      └── m3n4o5p6.jpg  (additional image 3)
```

### URL Format:

- **Local:** `http://localhost:8000/uploads/products/image.jpg`
- **Production:** `https://marquebackend-production.up.railway.app/uploads/products/image.jpg`

---

## 🔄 Differences from ProductAsset

### Old Approach (ProductAsset):

```python
# Separate table for images
ProductAsset:
  - id
  - product_id (FK)
  - url
  - type
  - alt_text
  - order
```

**Pros:**

- Unlimited images
- Better for complex image metadata
- Separate image management

**Cons:**

- Requires joins to load images
- More complex queries
- Lazy loading issues (DetachedInstanceError)

### New Approach (Product Columns):

```python
# Columns in Product table
Product:
  - id
  - main_image (String)
  - additional_images (JSON Array)
```

**Pros:**

- ✅ No joins needed
- ✅ No lazy loading errors
- ✅ Simpler queries
- ✅ Faster loading
- ✅ Direct access

**Cons:**

- Limited to recommended 5-6 images
- Less metadata per image
- JSON array harder to query individually

---

## 📊 API Response (Frontend)

When fetching products via API, the response now includes:

```json
{
  "id": 123,
  "title": "Nike Running Shoes",
  "slug": "nike-running-shoes",
  "main_image": "/uploads/products/a1b2c3d4.jpg",
  "additional_images": [
    "/uploads/products/e5f6g7h8.jpg",
    "/uploads/products/i9j0k1l2.jpg",
    "/uploads/products/m3n4o5p6.jpg"
  ],
  "price_min": 149.99,
  "brand": {
    "name": "Nike",
    "slug": "nike"
  },
  ...
}
```

### Frontend Usage:

```typescript
// Display main image
<img src={product.main_image} alt={product.title} />;

// Display image gallery
{
  product.additional_images?.map((url, index) => (
    <img key={index} src={url} alt={`${product.title} - ${index + 1}`} />
  ));
}
```

---

## ✅ Benefits

1. **No More DetachedInstanceError** ✅

   - Images are columns, not relationships
   - No lazy loading issues

2. **Faster Queries** ✅

   - No joins needed
   - Direct access to image URLs

3. **Simpler Code** ✅

   - Just access `product.main_image`
   - No need to loop through assets

4. **Better Performance** ✅

   - Less database queries
   - Faster page loads

5. **Pillow Processing** ✅
   - Automatic validation
   - Automatic resizing
   - Automatic optimization

---

## 🚀 Usage Guide

### Creating a Product with Images:

1. **Navigate:** Admin Panel → Каталог → Товары → + New Товары
2. **Fill:** Title, Slug, Description, Brand, Category, Subcategory
3. **Upload Main Image:**
   - Scroll to "Главное изображение"
   - Click "Choose File"
   - Select JPEG or PNG image
4. **Upload Additional Images:**
   - Scroll to "Дополнительные изображения"
   - Click "Choose Files"
   - Select up to 5 JPEG or PNG images
5. **Save:** Click "Save"
6. **Result:**
   - ✅ Images processed with Pillow
   - ✅ Saved to `/uploads/products/`
   - ✅ URLs stored in database
   - ✅ Thumbnails visible in list view
   - ✅ Gallery visible in detail view

### Updating Product Images:

1. **Edit:** Click on product in list
2. **Update Main Image (Optional):**
   - Upload new image → Replaces old one
3. **Add More Images (Optional):**
   - Upload new images → Appends to existing
4. **Save:** Click "Save"

---

## 🔍 Troubleshooting

### Images Not Showing?

**Check:**

1. File format (JPEG/PNG only)
2. File size (< 10MB)
3. `/uploads/products/` directory exists
4. Image URLs correct in database
5. Railway static files serving configured

### Upload Failed?

**Possible causes:**

1. Invalid image file (corrupted)
2. File too large
3. Disk space full
4. Permissions issue

**Solution:**

- Check server logs for detailed error
- Verify image is valid (open in image viewer)
- Try smaller image
- Check Railway storage limits

---

## 📚 Related Files

### Modified:

- `src/app_01/models/products/product.py` - Added columns
- `src/app_01/admin/sqladmin_views.py` - Updated admin logic
- `alembic/versions/8f7297e45fcb_add_product_image_columns.py` - Migration

### Unchanged (Still Available):

- `src/app_01/models/products/product_asset.py` - Still exists for legacy
- `src/app_01/utils/image_upload.py` - Still used for Pillow processing
- `src/app_01/routers/upload_router.py` - Still available for API uploads

---

## 🎉 Summary

**What Changed:**

- ✅ Added `main_image` column to Product
- ✅ Added `additional_images` JSON column to Product
- ✅ Admin form uploads save directly to Product columns
- ✅ Images processed with Pillow (resize, optimize)
- ✅ Thumbnails shown in list view
- ✅ Gallery shown in detail view
- ✅ No more DetachedInstanceError!

**What's Ready:**

- ✅ Local database migrated
- ✅ Admin panel updated
- ✅ Pillow integration working
- ✅ Upload functionality tested
- ✅ All code committed and pushed

**Next Step:**

- ⏳ Wait for Railway to deploy (~2-5 minutes)
- ✅ Test creating a product with images!

---

**🚀 Ready to use!** Go to your admin panel and create your first product with Pillow-processed images!
