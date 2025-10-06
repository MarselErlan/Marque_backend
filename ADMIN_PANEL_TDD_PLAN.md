# 🛠️ Admin Panel TDD Implementation Plan

## 📊 Sprint 2 Overview

**Goal**: Build complete admin panel for managing the entire product catalog

**Tests**: 32 comprehensive admin tests  
**Time Estimate**: 2-3 hours  
**Approach**: Test-Driven Development (TDD)

---

## 🎯 Features to Build

### 1. Enhanced Product Admin (8 tests)

**Route**: `/admin/product/*`

**Features**:

- ✅ View product details in admin
- ✅ Manage product images (upload, reorder, delete)
- ✅ Set featured products
- ✅ Toggle active/inactive status
- ✅ Bulk activate/deactivate
- ✅ Bulk price adjustment
- ✅ Product image gallery management
- ✅ Product variant overview

### 2. SKU Management (6 tests)

**Route**: `/admin/sku/*`

**Features**:

- ✅ List SKUs for a product
- ✅ Add new SKU to product
- ✅ Edit SKU (price, stock, size, color)
- ✅ Delete SKU
- ✅ Bulk stock update
- ✅ SKU validation

### 3. Category & Subcategory Management (8 tests)

**Route**: `/admin/category/*`, `/admin/subcategory/*`

**Features**:

- ✅ List all categories
- ✅ Create category
- ✅ Edit category
- ✅ Delete category
- ✅ Reorder categories (sort_order)
- ✅ Create subcategory
- ✅ Link subcategory to category
- ✅ Delete subcategory (with products check)

### 4. Brand Management (5 tests)

**Route**: `/admin/brand/*`

**Features**:

- ✅ List brands
- ✅ Create brand
- ✅ Edit brand
- ✅ Delete brand (check for products)
- ✅ Brand slug generation

### 5. Review Management (5 tests)

**Route**: `/admin/review/*`

**Features**:

- ✅ List all reviews
- ✅ Delete review
- ✅ Filter by rating
- ✅ Filter by product
- ✅ View review details

---

## 📁 File Structure

```
tests/admin/
├── conftest.py                      # Admin fixtures (already exists)
├── test_admin_auth.py               # Auth tests (already exists)
├── test_admin_product_enhanced.py   # NEW: Enhanced product features
├── test_admin_sku.py                # NEW: SKU management
├── test_admin_category.py           # NEW: Category management
├── test_admin_brand.py              # NEW: Brand management
└── test_admin_review.py             # NEW: Review management

src/app_01/admin/
├── admin_app.py                     # SQLAdmin setup (exists)
├── sqladmin_views.py                # Auth backend (exists)
├── product_admin_enhanced.py        # NEW: Enhanced product views
├── sku_admin.py                     # NEW: SKU views
├── category_admin.py                # NEW: Category views
├── brand_admin.py                   # NEW: Brand views
└── review_admin.py                  # NEW: Review views
```

---

## 🔴 RED Phase: Write Tests First

### Phase 1: Enhanced Product Admin Tests (8 tests)

```python
class TestEnhancedProductAdmin:
    - test_view_product_details_in_admin
    - test_upload_product_image
    - test_reorder_product_images
    - test_delete_product_image
    - test_set_product_as_featured
    - test_toggle_product_active_status
    - test_bulk_activate_products
    - test_bulk_deactivate_products
```

### Phase 2: SKU Management Tests (6 tests)

```python
class TestSKUManagement:
    - test_list_skus_for_product
    - test_add_sku_to_product
    - test_edit_sku_details
    - test_delete_sku
    - test_bulk_update_stock
    - test_sku_validation
```

### Phase 3: Category Management Tests (8 tests)

```python
class TestCategoryManagement:
    - test_list_categories
    - test_create_category
    - test_edit_category
    - test_delete_category
    - test_reorder_categories
    - test_create_subcategory
    - test_link_subcategory_to_category
    - test_delete_subcategory_with_products_check
```

### Phase 4: Brand Management Tests (5 tests)

```python
class TestBrandManagement:
    - test_list_brands
    - test_create_brand
    - test_edit_brand
    - test_delete_brand
    - test_delete_brand_with_products_fails
```

### Phase 5: Review Management Tests (5 tests)

```python
class TestReviewManagement:
    - test_list_reviews
    - test_delete_review
    - test_filter_reviews_by_rating
    - test_filter_reviews_by_product
    - test_view_review_details
```

---

## 🟢 GREEN Phase: Implementation

### Step 1: Enhanced Product Admin Views

- Create `ProductAdminEnhanced` view
- Add image management actions
- Add featured toggle
- Add bulk operations

### Step 2: SKU Admin Views

- Create `SKUAdmin` view
- Add CRUD operations
- Add bulk stock update
- Add validation

### Step 3: Category Admin Views

- Create `CategoryAdmin` view
- Create `SubcategoryAdmin` view
- Add ordering functionality
- Add delete validation

### Step 4: Brand Admin Views

- Create `BrandAdmin` view
- Add CRUD operations
- Add delete validation
- Auto-generate slugs

### Step 5: Review Admin Views

- Create `ReviewAdmin` view
- Add filtering
- Add moderation actions

---

## 🔵 REFACTOR Phase

- Clean up code
- Add proper error handling
- Optimize queries
- Add admin notifications
- Documentation

---

## ✅ Success Criteria

- **32/32 tests passing**
- **All CRUD operations working**
- **Proper validation**
- **Bulk operations functional**
- **Admin UI responsive**
- **Production ready**

---

## 📊 Progress Tracking

```
Phase 1: Enhanced Product Admin    [  ] 0/8 tests
Phase 2: SKU Management             [  ] 0/6 tests
Phase 3: Category Management        [  ] 0/8 tests
Phase 4: Brand Management           [  ] 0/5 tests
Phase 5: Review Management          [  ] 0/5 tests
─────────────────────────────────────────────────
Total:                              [  ] 0/32 tests
```

---

**Let's start building!** 🚀
