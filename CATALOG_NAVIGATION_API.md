# Catalog Navigation API - Complete Guide

This document explains how the API matches your design for catalog navigation:
**Catalog Page** → **Category Page** → **Product Listing**

---

## 🎯 Design Flow

```
┌─────────────────┐
│  Catalog Page   │  ← Shows categories (Мужчинам, Женщинам, etc.)
│   (Screen 1)    │    with images and product counts
└────────┬────────┘
         │ User clicks "Мужчинам"
         ↓
┌─────────────────┐
│  Category Page  │  ← Shows subcategories (Футболки, Джинсы, etc.)
│   (Screen 2)    │    with images and product counts
└────────┬────────┘
         │ User clicks "Футболки и поло"
         ↓
┌─────────────────┐
│ Product Listing │  ← Shows products with filters, sorting, pagination
│   (Screen 3)    │
└─────────────────┘
```

---

## 📱 Screen 1: Catalog Page (Main Categories)

### Design Requirements

- Show all main categories (Мужчинам, Женщинам, Детям, Спорт, Обувь, Аксессуары)
- Each category has an image
- Show product count for each category
- Grid layout: 2 columns on mobile, 3+ on desktop

### API Endpoint

```http
GET /categories
```

### Response Example

```json
{
  "categories": [
    {
      "id": 1,
      "name": "Мужчинам",
      "slug": "men",
      "icon": "fa-male",
      "image_url": "https://cdn.example.com/categories/men.jpg",
      "product_count": 15234,
      "is_active": true,
      "sort_order": 1
    },
    {
      "id": 2,
      "name": "Женщинам",
      "slug": "women",
      "icon": "fa-female",
      "image_url": "https://cdn.example.com/categories/women.jpg",
      "product_count": 18567,
      "is_active": true,
      "sort_order": 2
    },
    {
      "id": 3,
      "name": "Детям",
      "slug": "kids",
      "icon": "fa-child",
      "image_url": "https://cdn.example.com/categories/kids.jpg",
      "product_count": 8934,
      "is_active": true,
      "sort_order": 3
    },
    {
      "id": 4,
      "name": "Спорт",
      "slug": "sport",
      "icon": "fa-running",
      "image_url": "https://cdn.example.com/categories/sport.jpg",
      "product_count": 12456,
      "is_active": true,
      "sort_order": 4
    },
    {
      "id": 5,
      "name": "Обувь",
      "slug": "shoes",
      "icon": "fa-shoe-prints",
      "image_url": "https://cdn.example.com/categories/shoes.jpg",
      "product_count": 6789,
      "is_active": true,
      "sort_order": 5
    },
    {
      "id": 6,
      "name": "Аксессуары",
      "slug": "accessories",
      "icon": "fa-bag",
      "image_url": "https://cdn.example.com/categories/accessories.jpg",
      "product_count": 3456,
      "is_active": true,
      "sort_order": 6
    }
  ]
}
```

### Frontend Implementation

```typescript
// Fetch categories
const response = await fetch(
  "https://marquebackend-production.up.railway.app/categories"
);
const data = await response.json();

// Display in grid
data.categories.forEach((category) => {
  // Create card with:
  // - category.image_url as background/image
  // - category.name as title
  // - category.product_count as subtitle
  // - Navigate to `/catalog/${category.slug}` on click
});
```

---

## 📱 Screen 2: Category Page (Subcategories)

### Design Requirements

- Show "Мужчинам" title with "11 подкатегорий" subtitle
- List subcategories with icons and product counts:
  - Футболки и поло (2352)
  - Рубашки (2375)
  - Свитшоты и худи (8533)
  - Джинсы (1254)
  - etc.
- Each subcategory has an image/icon
- Shows product count for each

### API Endpoint

```http
GET /categories/{category_slug}
```

Example: `GET /categories/men`

### Response Example

```json
{
  "id": 1,
  "name": "Мужчинам",
  "slug": "men",
  "description": "Мужская одежда и аксессуары",
  "icon": "fa-male",
  "image_url": "https://cdn.example.com/categories/men.jpg",
  "product_count": 15234,
  "is_active": true,
  "sort_order": 1,
  "subcategories": [
    {
      "id": 1,
      "name": "Футболки и поло",
      "slug": "tshirts-polo",
      "image_url": "https://cdn.example.com/subcategories/tshirts.jpg",
      "product_count": 2352,
      "is_active": true,
      "sort_order": 1
    },
    {
      "id": 2,
      "name": "Рубашки",
      "slug": "shirts",
      "image_url": "https://cdn.example.com/subcategories/shirts.jpg",
      "product_count": 2375,
      "is_active": true,
      "sort_order": 2
    },
    {
      "id": 3,
      "name": "Свитшоты и худи",
      "slug": "sweatshirts-hoodies",
      "image_url": "https://cdn.example.com/subcategories/hoodies.jpg",
      "product_count": 8533,
      "is_active": true,
      "sort_order": 3
    },
    {
      "id": 4,
      "name": "Джинсы",
      "slug": "jeans",
      "image_url": "https://cdn.example.com/subcategories/jeans.jpg",
      "product_count": 1254,
      "is_active": true,
      "sort_order": 4
    }
    // ... more subcategories
  ]
}
```

### Frontend Implementation

```typescript
// Fetch category with subcategories
const categorySlug = "men"; // From route params
const response = await fetch(
  `https://marquebackend-production.up.railway.app/categories/${categorySlug}`
);
const category = await response.json();

// Display header
document.title = category.name; // "Мужчинам"
document.subtitle = `${category.subcategories.length} подкатегорий`;

// Display subcategory list
category.subcategories.forEach((subcategory) => {
  // Create list item with:
  // - subcategory.image_url as icon/image (left side)
  // - subcategory.name as main text
  // - subcategory.product_count as right side number
  // - Navigate to `/catalog/${categorySlug}/${subcategory.slug}` on click
});
```

---

## 📱 Screen 3: Product Listing Page

### Design Requirements

- Breadcrumb: "Мужчинам > Футболки и поло"
- Title: "Футболки и поло" with "23 239 товаров"
- Filters:
  - Sort by (По популярности, Новинки, Цена ↑/↓, Рейтинг)
  - Category (Мужчинам)
  - Subcategory (Футболки и поло)
  - Size (XS, S, M, L, XL, XXL)
  - Price (от - до)
  - Color (multiple selection)
  - Brand (multiple selection)
- Product cards with:
  - Image
  - Discount badge (%)
  - Brand name (H&M)
  - Product title
  - Price (current and crossed-out original)
  - Sold count (Продано 23)
- Pagination (1, 2, 3, ..., 10)

### API Endpoint

```http
GET /subcategories/{subcategory_slug}/products
```

### Query Parameters

| Parameter   | Type   | Description                                                           | Example               |
| ----------- | ------ | --------------------------------------------------------------------- | --------------------- |
| `page`      | int    | Page number (default: 1)                                              | `?page=2`             |
| `limit`     | int    | Items per page (default: 20, max: 100)                                | `?limit=30`           |
| `sort_by`   | string | Sort option: `newest`, `popular`, `price_asc`, `price_desc`, `rating` | `?sort_by=popular`    |
| `price_min` | float  | Minimum price filter                                                  | `?price_min=1000`     |
| `price_max` | float  | Maximum price filter                                                  | `?price_max=5000`     |
| `sizes`     | string | Comma-separated sizes                                                 | `?sizes=M,L,XL`       |
| `colors`    | string | Comma-separated colors                                                | `?colors=black,white` |
| `brands`    | string | Comma-separated brand slugs                                           | `?brands=nike,adidas` |
| `search`    | string | Search query                                                          | `?search=cotton`      |

### Example Request

```http
GET /subcategories/tshirts-polo/products?page=1&limit=20&sort_by=popular&price_min=1000&price_max=5000&sizes=M,L&colors=black
```

### Response Example

```json
{
  "products": [
    {
      "id": 123,
      "title": "Футболка спорт. из хлопка",
      "slug": "cotton-sport-tshirt",
      "price_min": 2999.0,
      "price_max": 2999.0,
      "original_price_min": 3699.0,
      "discount_percent": 19,
      "image": "https://cdn.example.com/products/tshirt-black-123.jpg",
      "rating_avg": 4.5,
      "rating_count": 156,
      "sold_count": 23,
      "brand_name": "H&M",
      "brand_slug": "hm"
    },
    {
      "id": 124,
      "title": "Футболка спорт. из хлопка",
      "slug": "cotton-sport-tshirt-2",
      "price_min": 2999.0,
      "price_max": 2999.0,
      "original_price_min": 3699.0,
      "discount_percent": 19,
      "image": "https://cdn.example.com/products/tshirt-black-124.jpg",
      "rating_avg": 4.3,
      "rating_count": 89,
      "sold_count": 45,
      "brand_name": "H&M",
      "brand_slug": "hm"
    }
    // ... more products (up to `limit`)
  ],
  "total": 23239,
  "page": 1,
  "limit": 20,
  "total_pages": 1162
}
```

### Frontend Implementation

```typescript
// Build query string
const params = new URLSearchParams({
  page: "1",
  limit: "20",
  sort_by: "popular",
  // Add filters if selected:
  // price_min: '1000',
  // price_max: '5000',
  // sizes: 'M,L,XL',
  // colors: 'black,white',
  // brands: 'nike,adidas'
});

// Fetch products
const subcategorySlug = "tshirts-polo"; // From route params
const response = await fetch(
  `https://marquebackend-production.up.railway.app/subcategories/${subcategorySlug}/products?${params}`
);
const data = await response.json();

// Display header
document.title = `Футболки и поло - ${data.total} товаров`;

// Display products grid
data.products.forEach((product) => {
  // Create product card with:
  // - product.image
  // - Discount badge if product.discount_percent exists
  // - product.brand_name
  // - product.title
  // - product.price_min (main price)
  // - product.original_price_min (crossed out if exists)
  // - `Продано ${product.sold_count}`
  // - Navigate to `/product/${product.slug}` on click
});

// Display pagination
const totalPages = data.total_pages;
const currentPage = data.page;
// Create pagination component (1, 2, 3, ..., 10)
```

---

## 🎨 Complete User Flow Example

### Step 1: User Opens Catalog

```http
GET /categories
```

Response shows 6 categories with images.

User sees:

- Мужчинам (15,234 products)
- Женщинам (18,567 products)
- Детям (8,934 products)
- Спорт (12,456 products)
- Обувь (6,789 products)
- Аксессуары (3,456 products)

### Step 2: User Clicks "Мужчинам"

```http
GET /categories/men
```

Response shows category "Мужчинам" with 11 subcategories.

User sees:

- Футболки и поло (2,352 products)
- Рубашки (2,375 products)
- Свитшоты и худи (8,533 products)
- Джинсы (1,254 products)
- Брюки и шорты (643 products)
- ... and 6 more

### Step 3: User Clicks "Футболки и поло"

```http
GET /subcategories/tshirts-polo/products?page=1&limit=20&sort_by=popular
```

Response shows 20 products, page 1 of 118 (2,352 total products).

User sees:

- Grid of 20 product cards
- Filters available (size, color, price, brand)
- Sorting options
- Pagination

### Step 4: User Applies Filters

```http
GET /subcategories/tshirts-polo/products?page=1&limit=20&sort_by=popular&sizes=M,L&colors=black&price_min=2000&price_max=4000
```

Response shows filtered results (e.g., 450 products matching filters).

User sees:

- Filtered products (black, size M or L, price 2000-4000)
- Updated total count
- Updated pagination

---

## 🎯 API Endpoints Summary

| Screen              | Endpoint                             | Purpose                                        |
| ------------------- | ------------------------------------ | ---------------------------------------------- |
| **Catalog**         | `GET /categories`                    | Get all main categories with images and counts |
| **Category Page**   | `GET /categories/{slug}`             | Get subcategories for a category               |
| **Product Listing** | `GET /subcategories/{slug}/products` | Get products with filters, sorting, pagination |

---

## 🚀 Deployment Status

✅ **All endpoints are LIVE in production:**

- Base URL: `https://marquebackend-production.up.railway.app`
- All categories support images via `image_url` field
- All subcategories support images via `image_url` field
- Product listing supports:
  - Pagination (page, limit)
  - Sorting (newest, popular, price, rating)
  - Filters (price, size, color, brand)
  - Search

---

## 📝 Next Steps for Frontend

1. **Create Catalog Page**

   - Fetch `/categories`
   - Display grid of categories with images
   - Navigate to category page on click

2. **Create Category Page**

   - Fetch `/categories/{slug}`
   - Display list of subcategories with counts
   - Navigate to product listing on click

3. **Create Product Listing Page**

   - Fetch `/subcategories/{slug}/products` with filters
   - Display product grid
   - Implement filters (size, color, price, brand)
   - Implement sorting dropdown
   - Implement pagination

4. **Upload Category Images via Admin**
   - Go to `/admin` → 🛍️ Каталог → Категории
   - Add image URLs for each category
   - Go to 🛍️ Каталог → Подкатегории
   - Add image URLs for each subcategory

---

## 🎉 Your API is Ready!

All the logic you described is implemented and working:

- ✅ User picks category → sees subcategories
- ✅ User picks subcategory → sees products
- ✅ Products can be filtered by size, color, price, brand
- ✅ Products can be sorted by popularity, price, rating, date
- ✅ Full pagination support
- ✅ All images supported (categories and subcategories)

**Just connect your frontend and upload images! 🚀**
