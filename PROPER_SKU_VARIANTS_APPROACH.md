# ✅ Proper E-Commerce Product Variants System

**Date**: October 19, 2025  
**Approach**: SKU Variants (Industry Standard)  
**Status**: ✅ IMPLEMENTED

---

## 🎯 **The Right Way: Two-Level System**

### **Product** (Main Entity)

- Basic product information
- Title, Description, Images
- Brand, Category, Subcategory
- NO price, NO stock, NO single SKU

### **SKU** (Variants)

- Specific combinations (Size + Color)
- Each variant has own SKU code, price, stock
- Flexible pricing per variant
- Independent stock tracking

---

## 📊 **Database Structure**

### **products** table:

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    brand_id INTEGER,
    category_id INTEGER,
    subcategory_id INTEGER,
    title VARCHAR(255),          -- "Футболка Nike"
    slug VARCHAR(255),           -- "futbolka-nike"
    description TEXT,
    main_image VARCHAR(500),
    additional_images JSON,
    season_id INTEGER,
    material_id INTEGER,
    style_id INTEGER,
    is_active BOOLEAN,
    is_featured BOOLEAN,
    attributes JSON,
    created_at TIMESTAMP
);
```

### **skus** table:

```sql
CREATE TABLE skus (
    id INTEGER PRIMARY KEY,
    product_id INTEGER,           -- Links to product
    sku_code VARCHAR(50) UNIQUE,  -- "NIKE-001-42-BLACK"
    size VARCHAR(20),             -- "42"
    color VARCHAR(50),            -- "Черный"
    price FLOAT,                  -- 8500.0
    original_price FLOAT,         -- 10000.0 (for discounts)
    stock INTEGER,                -- 5
    is_active BOOLEAN
);
```

---

## 🎨 **Admin Panel Workflow**

### **Step 1: Create Main Product**

```
Go to: Товары → + New Product

Fill in:
┌────────────────────────────────────┐
│ Title: "Футболка Nike"             │
│ Slug: "futbolka-nike"              │
│ Description: "Спортивная футболка" │
│ Brand: Nike                        │
│ Category: Одежда                   │
│ Subcategory: Футболки              │
│ Main Image: [Upload]              │
│ Additional Images: [Upload 5]     │
│ Season: Мульти                     │
│ Is Active: ✓                       │
└────────────────────────────────────┘

Save ✅  (Product created, ID = 286)
```

### **Step 2: Add Size/Color Variants**

```
Go to: Варианты товаров (Размеры/Цвета) → + New Variant

Variant 1:
┌────────────────────────────────────┐
│ Product: "Футболка Nike" (286)     │
│ SKU код: "NIKE-001-42-BLACK"       │
│ Размер: "42"                       │
│ Цвет: "Черный"                     │
│ Цена: 8500.0                       │
│ Оригинальная цена: 10000.0        │
│ Количество на складе: 10           │
│ Активен: ✓                         │
└────────────────────────────────────┘
Save ✅

Variant 2:
┌────────────────────────────────────┐
│ Product: "Футболка Nike" (286)     │
│ SKU код: "NIKE-001-44-BLACK"       │
│ Размер: "44"                       │
│ Цвет: "Черный"                     │
│ Цена: 8500.0                       │
│ Количество на складе: 15           │
│ Активен: ✓                         │
└────────────────────────────────────┘
Save ✅

Variant 3:
┌────────────────────────────────────┐
│ Product: "Футболка Nike" (286)     │
│ SKU код: "NIKE-001-42-WHITE"       │
│ Размер: "42"                       │
│ Цвет: "Белый"                      │
│ Цена: 9000.0  (Different price!)   │
│ Количество на складе: 5            │
│ Активен: ✓                         │
└────────────────────────────────────┘
Save ✅
```

---

## 💡 **Why This is Better**

### **Flexible Pricing:**

```
Size 42, Черный: 8500 сом
Size 44, Черный: 8500 сом
Size 42, Белый: 9000 сом  (Different!)
Size 46, Красный: 7500 сом  (On sale!)
```

### **Independent Stock:**

```
Size 42, Черный: 10 units
Size 44, Черный: 15 units
Size 42, Белый: 5 units
Size 46, Красный: 0 units (Out of stock, but variant exists)
```

### **Easy Management:**

- Add new sizes anytime
- Add new colors anytime
- Adjust prices per variant
- Track stock per variant
- Deactivate specific variants

---

## 🛒 **Customer Experience**

### **Product Page:**

```html
┌─────────────────────────────────────────┐ │ Футболка Nike │ │ ⭐⭐⭐⭐⭐ (32
отзыва) │ │ │ │ [Image Gallery] │ │ │ │ Цена: от 7500 сом │ │ │ │ Размер: │ │ ○
RUS 40 ○ RUS 42 ○ RUS 44 ⊗ RUS 46│ │ │ │ Цвет: │ │ ● Черный ○ Белый ⊗ Красный │
│ │ │ Выбрано: RUS 42, Черный │ │ Цена: 8500 сом │ │ В наличии: 10 шт. │ │ │ │
[Добавить в корзину] │ └─────────────────────────────────────────┘ Legend: ○ =
Available ● = Selected ⊗ = Out of stock
```

---

## 🔍 **Database Query Examples**

### **Get Product with All Variants:**

```python
product = db.query(Product).filter_by(id=286).first()
variants = db.query(SKU).filter_by(product_id=286, is_active=True).all()

# Display
print(f"Product: {product.title}")
print(f"Available variants: {len(variants)}")
for sku in variants:
    print(f"  - Size {sku.size}, {sku.color}: {sku.price} сом ({sku.stock} in stock)")
```

### **Add to Cart (Specific Variant):**

```python
# Customer selects: Size 42, Черный
sku = db.query(SKU).filter_by(
    product_id=286,
    size="42",
    color="Черный",
    is_active=True
).first()

if sku and sku.stock > 0:
    cart_item = CartItem(
        cart_id=cart_id,
        sku_id=sku.id,  # Links to specific variant!
        quantity=1,
        price=sku.price
    )
    db.add(cart_item)
    sku.reduce_stock(1)
    db.commit()
```

---

## 📦 **Migration Applied**

### **Removed from products:**

- ❌ `sku_code` (moved to SKU table)
- ❌ `price` (moved to SKU table)
- ❌ `stock_quantity` (moved to SKU table)

### **Kept in products:**

- ✅ `title`, `slug`, `description`
- ✅ `brand_id`, `category_id`, `subcategory_id`
- ✅ `main_image`, `additional_images`
- ✅ `season_id`, `material_id`, `style_id`
- ✅ `is_active`, `is_featured`, `attributes`

### **SKU table structure:**

- ✅ `product_id` (links to product)
- ✅ `sku_code` (unique variant code)
- ✅ `size` (42, 44, 46, ...)
- ✅ `color` (Черный, Белый, ...)
- ✅ `price` (per variant)
- ✅ `original_price` (for discounts)
- ✅ `stock` (per variant)
- ✅ `is_active` (per variant)

---

## 🎯 **Real-World Examples**

### **Example 1: Simple T-Shirt**

```
Product: "Футболка H&M"
Variants:
  - SKU-001-40-BLACK: Size 40, Черный, 500 сом, 20 шт.
  - SKU-001-42-BLACK: Size 42, Черный, 500 сом, 15 шт.
  - SKU-001-44-BLACK: Size 44, Черный, 500 сом, 10 шт.
  - SKU-001-40-WHITE: Size 40, Белый, 550 сом, 5 шт.
  - SKU-001-42-WHITE: Size 42, Белый, 550 сом, 8 шт.
```

### **Example 2: Shoes**

```
Product: "Кроссовки Nike Air Max"
Variants:
  - NIKE-MAX-39-BLACK: Size 39, Черный, 12000 сом, 2 шт.
  - NIKE-MAX-40-BLACK: Size 40, Черный, 12000 сом, 5 шт.
  - NIKE-MAX-41-BLACK: Size 41, Черный, 12000 сом, 0 шт. (Out of stock)
  - NIKE-MAX-39-WHITE: Size 39, Белый, 13000 сом, 3 шт.
  - NIKE-MAX-40-BLUE: Size 40, Синий, 11000 сом, 10 шт. (On sale!)
```

---

## ✅ **Summary**

### **Before** (Wrong):

```
Product:
  - sku_code: "NIKE-001"
  - price: 8500
  - stock: 50

Problem: How to handle different sizes/colors?
```

### **After** (Correct):

```
Product:
  - title: "Футболка Nike"
  - (no price, no stock)

SKU Variants:
  - NIKE-001-42-BLACK: 8500 сом, 10 шт.
  - NIKE-001-44-BLACK: 8500 сом, 15 шт.
  - NIKE-001-42-WHITE: 9000 сом, 5 шт.

Solution: Each size/color is a separate SKU!
```

---

## 🚀 **After Deployment**

Railway will:

1. ✅ Run migration to remove fields from products table
2. ✅ Keep all existing data
3. ✅ SKU table ready for variants
4. ✅ Admin panel shows both "Товары" and "Варианты товаров"

**Now you have a proper e-commerce product system!** 🎉

### **Your Workflow:**

1. Create product (basic info + images)
2. Add variants (size/color combinations)
3. Manage stock per variant
4. Customers select size + color
5. Cart links to specific SKU variant

**This is how Amazon, Nike, H&M, and all major e-commerce platforms work!** ✅
