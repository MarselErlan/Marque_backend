# Pillow Image Upload System

## 🎯 Overview

The product admin panel now includes **direct image upload** using **Pillow** for image processing. You can upload the main product image and up to 5 additional images directly when creating or editing a product.

---

## 🗑️ Old Image URLs Removed

**✅ All 25 old product asset URLs have been deleted from the database.**

The old system with external URLs (Unsplash links) has been replaced with a proper upload system that:

- Uses **Pillow** for image validation and processing
- **Resizes** images automatically to 500x500px (medium size)
- **Optimizes** images for web performance
- **Stores** images in `/uploads/products/` directory
- Assigns proper **display order** (main image = 0, additional = 1, 2, 3...)

---

## 🆕 New Features

### 1. **Main Image Upload Field**

- **Field Name:** "Главное изображение"
- **Purpose:** The primary product image shown first on the website
- **Display Order:** Always set to `0`
- **Format:** JPEG, PNG
- **Processing:**
  - Validated with Pillow
  - Resized to 500x500px
  - Optimized for web

### 2. **Additional Images Upload Field**

- **Field Name:** "Дополнительные изображения"
- **Purpose:** Secondary product images (up to 5)
- **Display Order:** Numbered sequentially (1, 2, 3, 4, 5)
- **Format:** JPEG, PNG
- **Multiple Upload:** Yes, select up to 5 images at once

---

## 📝 How to Use

### Creating a New Product with Images:

1. **Navigate to Admin Panel:**

   - Go to `Каталог` → `Товары`
   - Click `+ New Товары`

2. **Fill in Product Details:**

   - Title, Slug, Description
   - Brand, Category, Subcategory
   - Season, Material, Style (optional)
   - Active status, Featured status

3. **Upload Main Image:**

   - Scroll to **"Главное изображение"** field
   - Click "Choose File"
   - Select your main product image (JPEG or PNG)

4. **Upload Additional Images (Optional):**

   - Scroll to **"Дополнительные изображения"** field
   - Click "Choose Files"
   - Select up to 5 additional images
   - You can select multiple files at once

5. **Save Product:**
   - Click "Save"
   - Images will be uploaded, processed with Pillow, and saved automatically

**Result:**

- Main image saved with `order = 0`
- Additional images saved with `order = 1, 2, 3, 4, 5`
- All images stored in `/uploads/products/`
- Thumbnails shown in product list
- Full gallery shown in product detail view

---

### Updating an Existing Product:

1. **Navigate to Product:**

   - Go to `Каталог` → `Товары`
   - Click on the product you want to edit

2. **Update Main Image (Optional):**

   - If you upload a new main image, it will **replace** the old one
   - The old main image (order=0) is automatically deleted

3. **Add More Images:**

   - Upload additional images
   - They will be added to existing images with incremented order numbers

4. **Save Changes:**
   - Click "Save"
   - New images are processed and added

---

## 🖼️ Image Processing Flow

```
User uploads image
        ↓
File validated by Pillow (format, size, validity)
        ↓
Image read into memory
        ↓
Passed to image_uploader.save_image()
        ↓
Pillow processes image:
  - Resizes to 500x500px (medium preset)
  - Optimizes quality
  - Converts format if needed
        ↓
Saved to /uploads/products/{unique_filename}.jpg
        ↓
ProductAsset record created in database:
  - product_id: linked to product
  - url: /uploads/products/image.jpg
  - type: "image"
  - alt_text: "Product Name - Image X"
  - order: 0 for main, 1+ for additional
        ↓
Image displayed in admin panel and frontend
```

---

## 🔧 Technical Details

### File Upload Fields

**Form Configuration:**

```python
form_extra_fields = {
    "main_image": FileField(
        "Главное изображение",
        validators=[OptionalValidator()],
        description="Загрузите главное изображение товара (JPEG, PNG)"
    ),
    "additional_images": MultipleFileField(
        "Дополнительные изображения",
        validators=[OptionalValidator()],
        description="Загрузите дополнительные изображения товара (до 5 шт.)"
    )
}
```

### Custom Save Logic

**insert_model method:**

- Extracts image fields from form data
- Creates product first
- Uploads and saves main image (order=0)
- Uploads and saves additional images (order=1, 2, 3...)
- Creates ProductAsset records for each image

**update_model method:**

- Extracts image fields
- Updates product details
- If new main image: deletes old main image, saves new one
- If additional images: appends to existing images with incremented order

**\_save_product_image method:**

- Validates image with Pillow (`Image.open()` + `verify()`)
- Creates FastAPI UploadFile object
- Calls `image_uploader.save_image()` with:
  - `category="products"`
  - `resize_to="medium"` (500x500px)
  - `optimize=True`
- Returns the saved image URL

---

## 📁 File Storage Structure

```
/uploads/
  └── products/
      ├── abc123def456.jpg  (main image, order=0)
      ├── ghi789jkl012.jpg  (additional image, order=1)
      ├── mno345pqr678.jpg  (additional image, order=2)
      └── ...
```

Each file gets a unique filename (generated by image_uploader).

---

## 📊 Database Schema

### ProductAsset Table

| Field      | Type    | Description                               |
| ---------- | ------- | ----------------------------------------- |
| id         | Integer | Primary key                               |
| product_id | Integer | Foreign key to products                   |
| url        | String  | Path to uploaded image                    |
| type       | String  | "image" (or "video" for future support)   |
| alt_text   | String  | SEO alt text                              |
| order      | Integer | Display order (0 = main, 1+ = additional) |

**Example Records:**

```sql
-- Main image
INSERT INTO product_assets (product_id, url, type, alt_text, order)
VALUES (123, '/uploads/products/abc123.jpg', 'image', 'Nike Shirt - Main Image', 0);

-- Additional images
INSERT INTO product_assets (product_id, url, type, alt_text, order)
VALUES (123, '/uploads/products/def456.jpg', 'image', 'Nike Shirt - Image 2', 1);

INSERT INTO product_assets (product_id, url, type, alt_text, order)
VALUES (123, '/uploads/products/ghi789.jpg', 'image', 'Nike Shirt - Image 3', 2);
```

---

## 🎨 Admin Panel Display

### List View (Products Table)

```
┌────┬────────────┬─────────────────┬─────────┬──────────────┐
│ ID │  [Photo]   │ Title           │ Brand   │ Category     │
├────┼────────────┼─────────────────┼─────────┼──────────────┤
│ 6  │ [Uploaded] │ New Test Product│ Nike    │ Мужчинам     │
│ 7  │ [Uploaded] │ Another Product │ Adidas  │ Женщинам     │
└────┴────────────┴─────────────────┴─────────┴──────────────┘
```

Thumbnails now show uploaded images, not external URLs.

### Detail View (Product Details)

**Изображения Section:**

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Main      │  │  Additional │  │  Additional │
│   Image     │  │   Image 1   │  │   Image 2   │
│  (order 0)  │  │  (order 1)  │  │  (order 2)  │
└─────────────┘  └─────────────┘  └─────────────┘
```

All uploaded images displayed with their order numbers.

---

## ✅ Benefits

1. **No More External URLs:**

   - All images stored locally
   - No dependency on external services (Unsplash)
   - Full control over image hosting

2. **Automatic Image Processing:**

   - Pillow validates all uploads
   - Automatic resizing to optimal size (500x500px)
   - Web optimization for faster loading

3. **Better Admin UX:**

   - Upload images directly in product form
   - No need to use separate "Медиа файлы" section
   - Main image + additional images in one place

4. **Correct Display Order:**

   - Main image always first (order=0)
   - Additional images numbered sequentially
   - Frontend displays images in correct order

5. **Image Management:**
   - Update main image anytime (old one auto-deleted)
   - Add more images without affecting existing ones
   - Clean image replacement workflow

---

## 🚨 Important Notes

### Supported Formats

- ✅ JPEG (.jpg, .jpeg)
- ✅ PNG (.png)
- ❌ GIF, WebP, TIFF (not tested)

### File Size Limits

- **Max upload size:** Depends on server configuration (default: 10MB)
- **Recommended:** Keep images under 5MB for faster uploads

### Image Quality

- **Resize:** All images resized to 500x500px (medium preset)
- **Optimization:** Enabled by default (reduces file size without quality loss)
- **Format:** Saved as JPEG for smaller file size

### Multiple Uploads

- **Additional images:** Up to 5 images per product creation/update
- **Recommendation:** Upload main image first, then additional images

---

## 🔄 Migration from Old System

**Status:** ✅ COMPLETED

1. ✅ Old 25 product assets with external URLs deleted
2. ✅ New Pillow-based upload system implemented
3. ✅ Image upload fields added to product form
4. ✅ Custom save logic implemented
5. ✅ Image processing with Pillow integrated

**Next Steps for Existing Products:**

- Edit each product
- Upload new images using the new system
- Save product

---

## 🧪 Testing

### Test Image Upload:

1. Create a test product
2. Upload a main image (any JPEG or PNG)
3. Upload 2-3 additional images
4. Save product
5. Check:
   - ✅ Thumbnail appears in product list
   - ✅ All images shown in product detail view
   - ✅ Images stored in `/uploads/products/`
   - ✅ Main image has order=0
   - ✅ Additional images have order=1, 2, 3...
   - ✅ Images load correctly on frontend

---

## 📚 Related Files

### Modified Files:

- **`src/app_01/admin/sqladmin_views.py`**
  - Added image upload fields
  - Added `insert_model()` method
  - Added `update_model()` method
  - Added `_save_product_image()` method

### New Files:

- **`cleanup_old_images.py`**
  - Utility to delete old product assets
  - Already executed (deleted 25 records)

### Existing Files (Used):

- **`src/app_01/utils/image_upload.py`**

  - Image upload utility with Pillow
  - `image_uploader.save_image()` method

- **`src/app_01/routers/upload_router.py`**
  - Upload API endpoints
  - Available for standalone uploads if needed

---

## 🎉 Summary

**Before:**

- ❌ External image URLs (Unsplash)
- ❌ Manual "Медиа файлы" section
- ❌ No image processing
- ❌ Inconsistent display order

**After:**

- ✅ Upload images directly in product form
- ✅ Pillow-based validation and processing
- ✅ Automatic resizing and optimization
- ✅ Correct display order (main + additional)
- ✅ Local storage in `/uploads/products/`
- ✅ Clean, professional admin workflow

**Ready to use!** 🚀

Try creating a new product with images right now and see the difference!
