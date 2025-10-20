# 🎯 MARQUE Frontend API Documentation

**Complete API Reference for Frontend Integration**

Base URL: `https://marque.website` (Production)  
Base URL: `http://localhost:8000` (Local Development)

All API endpoints are prefixed with `/api/v1/` unless noted otherwise.

---

## 📋 Table of Contents

1. [Authentication](#-1-authentication-api)
2. [Products](#-2-products-api)
3. [Categories & Navigation](#-3-categories--navigation-api)
4. [Product Search](#-4-product-search-api)
5. [Cart Management](#-5-cart-api)
6. [Wishlist](#-6-wishlist-api)
7. [Banners](#-7-banners-api)
8. [Product Catalog](#-8-product-catalog-api)
9. [Search Analytics](#-9-search-analytics-api)

---

## 🔐 1. Authentication API

**Base Path:** `/api/v1/auth`

### 1.1 Get Supported Markets

```http
GET /api/v1/auth/markets
```

**Response:**

```json
{
  "supported_markets": [
    {
      "code": "kg",
      "country": "Kyrgyzstan",
      "currency": "KGS",
      "phone_prefix": "+996",
      "language": "ru"
    },
    {
      "code": "us",
      "country": "United States",
      "currency": "USD",
      "phone_prefix": "+1",
      "language": "en"
    }
  ],
  "default_market": "kg"
}
```

---

### 1.2 Send Verification Code

```http
POST /api/v1/auth/send-verification
```

**Headers:**

```
Content-Type: application/json
X-Market: kg  # Optional: Override market detection
```

**Request Body:**

```json
{
  "phone": "+996555123456"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Verification code sent successfully",
  "phone_number": "+996555123456",
  "code_length": 6,
  "expires_in": 300,
  "market": "kg"
}
```

**Error Responses:**

- `422` - Invalid phone format
- `429` - Rate limit exceeded (too many requests)
- `500` - SMS service error

---

### 1.3 Verify Code & Login

```http
POST /api/v1/auth/verify-code
```

**Request Body:**

```json
{
  "phone": "+996555123456",
  "verification_code": "123456"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Phone verified successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 2592000,
  "user": {
    "id": 123,
    "phone_number": "+996555123456",
    "full_name": "Иван Петров",
    "profile_image_url": null,
    "market": "kg",
    "created_at": "2024-01-15T10:30:00Z"
  },
  "market": "kg"
}
```

**Error Responses:**

- `400` - Invalid verification code
- `422` - Validation error

---

### 1.4 Get User Profile

```http
GET /api/v1/auth/profile
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "id": 123,
  "phone_number": "+996555123456",
  "full_name": "Иван Петров",
  "profile_image_url": "https://...",
  "market": "kg",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 1.5 Update Profile

```http
PUT /api/v1/auth/profile
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "full_name": "Иван Петров",
  "profile_image_url": "https://example.com/avatar.jpg"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": 123,
    "phone_number": "+996555123456",
    "full_name": "Иван Петров",
    "profile_image_url": "https://example.com/avatar.jpg",
    "market": "kg"
  }
}
```

---

### 1.6 Verify Token

```http
GET /api/v1/auth/verify-token
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "valid": true,
  "user_id": 123,
  "phone_number": "+996555123456",
  "market": "kg"
}
```

---

### 1.7 Logout

```http
POST /api/v1/auth/logout
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Logged out successfully. Please discard your token."
}
```

**Note:** JWT tokens are stateless. Simply delete the token from client storage.

---

## 🛍️ 2. Products API

**Base Path:** `/api/v1`

### 2.1 Get Best Sellers

```http
GET /api/v1/products/best-sellers?limit=20
```

**Query Parameters:**

- `limit` (optional): Number of products (default: all, max: 500)

**Response:**

```json
[
  {
    "id": 1,
    "title": "Nike Air Max 270",
    "slug": "nike-air-max-270",
    "brand_name": "Nike",
    "brand_slug": "nike",
    "image": "https://example.com/nike-air-max.jpg",
    "price_min": 8900.0,
    "price_max": 11500.0,
    "original_price_min": 12000.0,
    "discount_percent": 26,
    "rating_avg": 4.7,
    "rating_count": 156,
    "sold_count": 342,
    "in_stock": true
  }
]
```

---

### 2.2 Get Featured Products

```http
GET /api/v1/products/featured?limit=10
```

**Query Parameters:**

- `limit` (optional): 1-100 (default: 10)

**Use for:** Homepage featured section

---

### 2.3 Get New Arrivals

```http
GET /api/v1/products/new-arrivals?limit=20
```

**Query Parameters:**

- `limit` (optional): 1-100 (default: 20)

**Use for:** "New Arrivals" section

---

### 2.4 Get Trending Products

```http
GET /api/v1/products/trending?limit=10
```

**Query Parameters:**

- `limit` (optional): 1-100 (default: 10)

**Use for:** "Trending Now" section

---

### 2.5 Get Top Rated

```http
GET /api/v1/products/top-rated?limit=10&min_reviews=5
```

**Query Parameters:**

- `limit` (optional): 1-100 (default: 10)
- `min_reviews` (optional): Minimum review count (default: 5)

---

### 2.6 Get Products On Sale

```http
GET /api/v1/products/on-sale?limit=20
```

**Query Parameters:**

- `limit` (optional): 1-100 (default: 20)

---

### 2.7 Search Products (Global Search)

```http
GET /api/v1/products/search?query=nike&page=1&limit=20&sort_by=relevance
```

**🎯 Smart SKU Redirect:** If the search query exactly matches a product's SKU code, this endpoint automatically redirects (307) to the product detail page!

**Query Parameters:**

- `query` (required): Search query (1-200 chars)
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (1-100, default: 20)
- `sort_by` (optional): `relevance` | `price_asc` | `price_desc` | `newest` | `popular` | `rating`
- `price_min` (optional): Minimum price filter
- `price_max` (optional): Maximum price filter
- `sizes` (optional): Comma-separated sizes: `"M,L,XL"`
- `colors` (optional): Comma-separated colors: `"black,white,red"`
- `brands` (optional): Comma-separated brand slugs: `"nike,adidas"`
- `category` (optional): Category slug
- `subcategory` (optional): Subcategory slug

**Response:**

```json
{
  "products": [
    {
      "id": 1,
      "title": "Nike Air Max 270",
      "slug": "nike-air-max-270",
      "brand_name": "Nike",
      "brand_slug": "nike",
      "image": "https://...",
      "price_min": 8900.0,
      "price_max": 11500.0,
      "original_price_min": 12000.0,
      "discount_percent": 26,
      "rating_avg": 4.7,
      "rating_count": 156,
      "sold_count": 342,
      "in_stock": true
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20,
  "total_pages": 3,
  "has_more": true
}
```

---

### 2.8 Get Product Detail

```http
GET /api/v1/products/{slug}
```

**Example:**

```http
GET /api/v1/products/nike-air-max-270
```

**Response:**

```json
{
  "id": 1,
  "title": "Nike Air Max 270",
  "slug": "nike-air-max-270",
  "description": "Полное описание продукта...",
  "brand": {
    "id": 5,
    "name": "Nike",
    "slug": "nike"
  },
  "category": {
    "id": 2,
    "name": "Обувь",
    "slug": "obuv"
  },
  "subcategory": {
    "id": 8,
    "name": "Кроссовки",
    "slug": "krossovki"
  },
  "images": [
    {
      "id": 0,
      "url": "https://example.com/main.jpg",
      "alt_text": "Nike Air Max 270",
      "type": "image",
      "order": 0
    },
    {
      "id": 1,
      "url": "https://example.com/image2.jpg",
      "alt_text": "Nike Air Max 270 - изображение 1",
      "type": "image",
      "order": 1
    }
  ],
  "skus": [
    {
      "id": 101,
      "sku_code": "NIKE-001-42-BLACK",
      "size": "42",
      "color": "Черный",
      "price": 8900.0,
      "original_price": 12000.0,
      "stock": 15
    },
    {
      "id": 102,
      "sku_code": "NIKE-001-43-BLACK",
      "size": "43",
      "color": "Черный",
      "price": 8900.0,
      "original_price": 12000.0,
      "stock": 8
    }
  ],
  "available_sizes": ["40", "41", "42", "43", "44", "45"],
  "available_colors": ["Черный", "Белый", "Красный"],
  "price_min": 8900.0,
  "price_max": 11500.0,
  "in_stock": true,
  "rating_avg": 4.7,
  "rating_count": 156,
  "sold_count": 342,
  "reviews": [
    {
      "id": 1,
      "rating": 5,
      "text": "Отличные кроссовки!",
      "created_at": "2024-01-20T14:30:00Z"
    }
  ],
  "attributes": {
    "gender": "Мужские",
    "season": "Всесезонные",
    "composition": "Синтетика 60%, Текстиль 40%"
  },
  "breadcrumbs": [
    { "name": "Главная", "slug": "/" },
    { "name": "Обувь", "slug": "obuv" },
    { "name": "Кроссовки", "slug": "krossovki" },
    { "name": "Nike Air Max 270", "slug": "nike-air-max-270" }
  ],
  "similar_products": [
    {
      "id": 2,
      "title": "Nike Air Force 1",
      "slug": "nike-air-force-1",
      "price_min": 7500.0,
      "image": "https://...",
      "rating_avg": 4.8
    }
  ]
}
```

**Note:** This endpoint automatically tracks product views for analytics!

---

## 📂 3. Categories & Navigation API

**Base Path:** `/api/v1`

### 3.1 Get All Categories

```http
GET /api/v1/categories
```

**Response:**

```json
{
  "categories": [
    {
      "id": 1,
      "name": "Одежда",
      "slug": "odezhda",
      "icon": "👕",
      "image_url": "https://example.com/category-odezhda.jpg",
      "product_count": 342,
      "is_active": true,
      "sort_order": 1
    },
    {
      "id": 2,
      "name": "Обувь",
      "slug": "obuv",
      "icon": "👟",
      "image_url": "https://example.com/category-obuv.jpg",
      "product_count": 156,
      "is_active": true,
      "sort_order": 2
    }
  ]
}
```

---

### 3.2 Get Category Detail

```http
GET /api/v1/categories/{category_slug}
```

**Example:**

```http
GET /api/v1/categories/obuv
```

**Response:**

```json
{
  "id": 2,
  "name": "Обувь",
  "slug": "obuv",
  "description": "Широкий ассортимент обуви для всей семьи",
  "icon": "👟",
  "image_url": "https://example.com/category-obuv.jpg",
  "product_count": 156,
  "subcategories": [
    {
      "id": 8,
      "name": "Кроссовки",
      "slug": "krossovki",
      "image_url": "https://...",
      "product_count": 89,
      "is_active": true,
      "sort_order": 1
    },
    {
      "id": 9,
      "name": "Ботинки",
      "slug": "botinki",
      "image_url": "https://...",
      "product_count": 42,
      "is_active": true,
      "sort_order": 2
    }
  ],
  "is_active": true,
  "sort_order": 2
}
```

---

### 3.3 Get Subcategories

```http
GET /api/v1/categories/{category_slug}/subcategories
```

**Example:**

```http
GET /api/v1/categories/obuv/subcategories
```

**Response:**

```json
{
  "subcategories": [
    {
      "id": 8,
      "name": "Кроссовки",
      "slug": "krossovki",
      "image_url": "https://...",
      "product_count": 89,
      "is_active": true,
      "sort_order": 1
    }
  ]
}
```

---

### 3.4 Get Products by Subcategory

```http
GET /api/v1/subcategories/{subcategory_slug}/products
```

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (1-100, default: 20)
- `sort_by` (optional): `newest` | `price_asc` | `price_desc` | `popular` | `rating`
- `price_min` (optional): Minimum price
- `price_max` (optional): Maximum price
- `sizes` (optional): Comma-separated: `"M,L,XL"`
- `colors` (optional): Comma-separated: `"black,white"`
- `brands` (optional): Comma-separated slugs: `"nike,adidas"`
- `search` (optional): Search within subcategory

**Example:**

```http
GET /api/v1/subcategories/krossovki/products?page=1&limit=20&sort_by=popular&sizes=42,43&brands=nike,adidas
```

**Response:**

```json
{
  "products": [
    {
      "id": 1,
      "title": "Nike Air Max 270",
      "slug": "nike-air-max-270",
      "brand_name": "Nike",
      "brand_slug": "nike",
      "image": "https://...",
      "price_min": 8900.0,
      "price_max": 11500.0,
      "original_price_min": 12000.0,
      "discount_percent": 26,
      "rating_avg": 4.7,
      "rating_count": 156,
      "sold_count": 342
    }
  ],
  "total": 89,
  "page": 1,
  "limit": 20,
  "total_pages": 5,
  "filters": {
    "available_sizes": ["40", "41", "42", "43", "44", "45"],
    "available_colors": ["Черный", "Белый", "Красный", "Синий"],
    "available_brands": [
      { "slug": "nike", "name": "Nike" },
      { "slug": "adidas", "name": "Adidas" }
    ],
    "price_range": {
      "min": 2500.0,
      "max": 25000.0
    }
  },
  "category": {
    "id": 2,
    "slug": "obuv",
    "name": "Обувь"
  },
  "subcategory": {
    "id": 8,
    "slug": "krossovki",
    "name": "Кроссовки"
  }
}
```

---

## 🔍 4. Product Search API

### 4.1 Get Products (Legacy)

```http
GET /api/v1/products
```

**Query Parameters:**

- `search` (optional): Search query
- `category` (optional): Category slug
- `subcategory` (optional): Subcategory slug
- `brand` (optional): Brand slug
- `sort_by` (optional): `newest` | `popular` | `price_high_to_low` | `price_low_to_high`
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20)

**Note:** Use `/products/search` for better search functionality with smart SKU redirect!

---

## 🛒 5. Cart API

**Base Path:** `/api/v1/cart`

**Authentication Required:** Yes (Bearer token)

### 5.1 Get Cart

```http
GET /api/v1/cart
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "id": 45,
  "user_id": 123,
  "items": [
    {
      "id": 1,
      "sku_id": 101,
      "quantity": 2,
      "name": "Nike Air Max 270",
      "price": 8900.0,
      "image": "https://..."
    }
  ],
  "total_items": 1,
  "total_price": 17800.0
}
```

---

### 5.2 Add to Cart

```http
POST /api/v1/cart/items
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "sku_id": 101,
  "quantity": 1
}
```

**Response:** Returns updated cart (same as GET /cart)

---

### 5.3 Update Cart Item

```http
PUT /api/v1/cart/items/{item_id}?quantity=3
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `quantity`: New quantity

**Response:** Returns updated cart

---

### 5.4 Remove from Cart

```http
DELETE /api/v1/cart/items/{item_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** Returns updated cart

---

### 5.5 Clear Cart

```http
DELETE /api/v1/cart
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** Returns empty cart

---

## ❤️ 6. Wishlist API

**Base Path:** `/api/v1/wishlist`

**Authentication Required:** Yes (Bearer token)

### 6.1 Get Wishlist

```http
GET /api/v1/wishlist
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:**

```json
{
  "id": 23,
  "user_id": 123,
  "items": [
    {
      "id": 1,
      "product": {
        "id": "5",
        "name": "Nike Air Max 270",
        "slug": "nike-air-max-270",
        "brand": "Nike",
        "price": 8900.0,
        "image": "https://...",
        "inStock": true
      }
    }
  ]
}
```

---

### 6.2 Add to Wishlist

```http
POST /api/v1/wishlist/items
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "product_id": 5
}
```

**Response:** Returns updated wishlist

---

### 6.3 Remove from Wishlist

```http
DELETE /api/v1/wishlist/items/{product_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** Returns updated wishlist

---

### 6.4 Clear Wishlist

```http
DELETE /api/v1/wishlist
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response:** Returns empty wishlist

---

## 🎨 7. Banners API

**Base Path:** `/api/v1/banners`

### 7.1 Get All Active Banners

```http
GET /api/v1/banners/
```

**Response:**

```json
{
  "hero_banners": [
    {
      "id": 1,
      "title": "Летняя распродажа",
      "subtitle": "Скидки до 50%",
      "description": "На всю летнюю коллекцию",
      "image_url": "https://example.com/banner-summer.jpg",
      "mobile_image_url": "https://example.com/banner-summer-mobile.jpg",
      "banner_type": "hero",
      "cta_text": "Купить сейчас",
      "cta_url": "/catalog/sale",
      "display_order": 1,
      "is_active": true,
      "start_date": null,
      "end_date": null,
      "created_at": "2024-01-10T10:00:00Z"
    }
  ],
  "promo_banners": [
    {
      "id": 2,
      "title": "Бесплатная доставка",
      "subtitle": "При заказе от 5000 KGS",
      "image_url": "https://...",
      "banner_type": "promo",
      "cta_text": "Подробнее",
      "cta_url": "/delivery",
      "display_order": 1
    }
  ],
  "category_banners": [
    {
      "id": 3,
      "title": "Новая коллекция Nike",
      "image_url": "https://...",
      "banner_type": "category",
      "cta_text": "Смотреть",
      "cta_url": "/catalog/nike",
      "display_order": 1
    }
  ],
  "total": 3
}
```

---

### 7.2 Get Hero Banners Only

```http
GET /api/v1/banners/hero
```

**Use for:** Main carousel

---

### 7.3 Get Promo Banners Only

```http
GET /api/v1/banners/promo
```

**Use for:** Promotional sections

---

### 7.4 Get Category Banners Only

```http
GET /api/v1/banners/category
```

**Use for:** Category showcase sections

---

## 🏷️ 8. Product Catalog API

**Base Path:** `/api/v1/catalog`

### 8.1 Get Seasons

```http
GET /api/v1/catalog/seasons?featured_only=false
```

**Query Parameters:**

- `featured_only` (optional): boolean (default: false)

**Response:**

```json
[
  {
    "id": 1,
    "name": "Лето",
    "slug": "leto",
    "description": "Летняя коллекция",
    "product_count": 156,
    "is_featured": true,
    "is_active": true,
    "sort_order": 1
  },
  {
    "id": 2,
    "name": "Зима",
    "slug": "zima",
    "description": "Зимняя коллекция",
    "product_count": 89,
    "is_featured": false,
    "is_active": true,
    "sort_order": 2
  }
]
```

---

### 8.2 Get Popular Seasons

```http
GET /api/v1/catalog/seasons/popular?limit=5
```

**Query Parameters:**

- `limit` (optional): 1-20 (default: 5)

**Use for:** Homepage seasonal collections

---

### 8.3 Get Season by Slug

```http
GET /api/v1/catalog/seasons/{slug}
```

**Example:**

```http
GET /api/v1/catalog/seasons/leto
```

---

### 8.4 Get Materials

```http
GET /api/v1/catalog/materials?featured_only=false
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "Хлопок",
    "slug": "cotton",
    "description": "100% натуральный хлопок",
    "product_count": 234,
    "is_featured": true,
    "is_active": true,
    "sort_order": 1
  }
]
```

---

### 8.5 Get Popular Materials

```http
GET /api/v1/catalog/materials/popular?limit=10
```

---

### 8.6 Get Material by Slug

```http
GET /api/v1/catalog/materials/{slug}
```

---

### 8.7 Get Styles

```http
GET /api/v1/catalog/styles?featured_only=false
```

**Response:**

```json
[
  {
    "id": 1,
    "name": "Спортивный",
    "slug": "sport",
    "description": "Спортивный стиль",
    "product_count": 189,
    "is_featured": true,
    "is_active": true,
    "sort_order": 1
  }
]
```

---

### 8.8 Get Popular Styles

```http
GET /api/v1/catalog/styles/popular?limit=10
```

---

### 8.9 Get Style by Slug

```http
GET /api/v1/catalog/styles/{slug}
```

---

### 8.10 Get Catalog Overview

```http
GET /api/v1/catalog/overview
```

**Response:**

```json
{
  "attributes": {
    "total_sizes": 24,
    "total_colors": 35,
    "total_brands": 42
  },
  "seasons": {
    "total": 4,
    "featured": 2
  },
  "materials": {
    "total": 12,
    "featured": 5
  },
  "styles": {
    "total": 8,
    "featured": 3
  }
}
```

**Use for:** Dashboard stats

---

## 📊 9. Search Analytics API

**Base Path:** `/api/v1/search`

### 9.1 Track Search

```http
POST /api/v1/search/track
```

**Request Body:**

```json
{
  "search_term": "nike air max",
  "result_count": 15
}
```

**Response:**

```json
{
  "success": true,
  "message": "Search tracked successfully",
  "search_term": "nike air max",
  "result_count": 15
}
```

**Use:** Call this endpoint after performing a search to track analytics

---

### 9.2 Get Popular Searches

```http
GET /api/v1/search/popular?limit=10
```

**Query Parameters:**

- `limit` (optional): 1-100 (default: 10)

**Response:**

```json
[
  {
    "id": 1,
    "search_term": "nike air max",
    "search_count": 342,
    "result_count": 15,
    "last_searched": "2024-01-20T15:30:00Z"
  }
]
```

**Use for:** "Popular Searches" section

---

### 9.3 Get Search Suggestions

```http
GET /api/v1/search/suggestions?q=nik&limit=5
```

**Query Parameters:**

- `q` (required): Partial query (min 2 chars)
- `limit` (optional): 1-20 (default: 5)

**Response:**

```json
{
  "query": "nik",
  "suggestions": [
    {
      "term": "nike air max",
      "search_count": 342,
      "result_count": 15
    },
    {
      "term": "nike кроссовки",
      "search_count": 156,
      "result_count": 42
    }
  ]
}
```

**Use for:** Search autocomplete

---

### 9.4 Get Trending Searches

```http
GET /api/v1/search/trending?days=7&limit=10
```

**Query Parameters:**

- `days` (optional): 1-90 (default: 7)
- `limit` (optional): 1-100 (default: 10)

**Use for:** "Trending Now" section

---

### 9.5 Get Search Statistics

```http
GET /api/v1/search/stats
```

**Response:**

```json
{
  "total_searches": 5420,
  "unique_terms": 892,
  "avg_results_per_search": 12.5,
  "zero_result_searches": 34,
  "most_popular_term": "nike air max"
}
```

---

### 9.6 Get Search Insights

```http
GET /api/v1/search/insights
```

**Response:**

```json
{
  "popular_searches": [
    {
      "id": 1,
      "search_term": "nike air max",
      "search_count": 342,
      "result_count": 15
    }
  ],
  "zero_result_searches": [
    {
      "id": 23,
      "search_term": "gucci belt",
      "search_count": 15,
      "result_count": 0
    }
  ],
  "trending_searches": [
    {
      "id": 45,
      "search_term": "adidas кроссовки",
      "search_count": 89,
      "result_count": 23
    }
  ],
  "recommendations": [
    "🎯 Add products for 'gucci belt' - searched 15 times with no results",
    "✅ Excellent search success rate: 94.2%"
  ]
}
```

**Use for:** Admin dashboard

---

## 🛠️ Common Patterns

### Error Handling

All endpoints return consistent error responses:

```json
{
  "detail": "Error message here"
}
```

**HTTP Status Codes:**

- `200` - Success
- `201` - Created
- `307` - Redirect (Smart SKU search)
- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limit Exceeded
- `500` - Server Error

---

### Authentication

For protected endpoints, include the JWT token:

```javascript
fetch("https://marque.website/api/v1/cart", {
  headers: {
    Authorization: `Bearer ${accessToken}`,
    "Content-Type": "application/json",
  },
});
```

---

### Pagination

Paginated endpoints return:

```json
{
  "products": [...],
  "total": 156,
  "page": 1,
  "limit": 20,
  "total_pages": 8,
  "has_more": true
}
```

---

### Market Detection

Market is auto-detected from phone number, but can be overridden:

```javascript
fetch("https://marque.website/api/v1/auth/send-verification", {
  headers: {
    "X-Market": "kg", // or 'us'
  },
  method: "POST",
  body: JSON.stringify({ phone: "+996555123456" }),
});
```

---

## 🚀 Quick Start Examples

### Example 1: User Authentication Flow

```javascript
// 1. Send verification code
const sendCode = await fetch("/api/v1/auth/send-verification", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ phone: "+996555123456" }),
});

// 2. Verify code and get token
const verify = await fetch("/api/v1/auth/verify-code", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    phone: "+996555123456",
    verification_code: "123456",
  }),
});

const { access_token } = await verify.json();

// 3. Store token for future requests
localStorage.setItem("accessToken", access_token);
```

---

### Example 2: Homepage Data Loading

```javascript
// Load all homepage sections in parallel
const [featured, bestSellers, trending, banners] = await Promise.all([
  fetch("/api/v1/products/featured?limit=10"),
  fetch("/api/v1/products/best-sellers?limit=20"),
  fetch("/api/v1/products/trending?limit=8"),
  fetch("/api/v1/banners/"),
]);

const data = {
  featured: await featured.json(),
  bestSellers: await bestSellers.json(),
  trending: await trending.json(),
  banners: await banners.json(),
};
```

---

### Example 3: Product Search with Filters

```javascript
const searchParams = new URLSearchParams({
  query: "nike",
  page: 1,
  limit: 20,
  sort_by: "popular",
  sizes: "42,43,44",
  brands: "nike,adidas",
  price_min: 5000,
  price_max: 15000,
});

const response = await fetch(`/api/v1/products/search?${searchParams}`);
const { products, total, has_more } = await response.json();
```

---

### Example 4: Add to Cart

```javascript
const addToCart = async (skuId, quantity = 1) => {
  const token = localStorage.getItem("accessToken");

  const response = await fetch("/api/v1/cart/items", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ sku_id: skuId, quantity }),
  });

  const cart = await response.json();
  console.log("Cart updated:", cart);
};
```

---

## 📝 Notes

### Smart SKU Search

When a user searches for an exact SKU code (e.g., `"NIKE-001"`), the API automatically redirects (HTTP 307) to the product detail page. Handle this in your frontend:

```javascript
const response = await fetch("/api/v1/products/search?query=NIKE-001", {
  redirect: "follow", // Follow the redirect automatically
});
```

---

### Product View Tracking

The product detail endpoint (`GET /api/v1/products/{slug}`) automatically increments the view count. No additional action required!

---

### Search Analytics

Always call `/api/v1/search/track` after performing a search to help improve search suggestions and analytics.

---

### Image URLs

All image URLs are absolute URLs (CDN or full paths). Display them directly:

```html
<img src="https://example.com/product.jpg" alt="Product" />
```

---

## 🔗 Additional Resources

- **API Base URL (Production):** `https://marque.website`
- **Swagger Docs:** `https://marque.website/docs`
- **ReDoc:** `https://marque.website/redoc`

---

## 📞 Support

For API questions or issues, contact the backend team.

**Last Updated:** October 20, 2024  
**API Version:** 1.0.0
