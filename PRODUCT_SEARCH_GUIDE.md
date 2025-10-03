# 🔍 Product Search API Guide

## Overview

The Product Search API allows you to search for products by name, description, and brand. It includes powerful filtering, sorting, and pagination capabilities.

---

## 🎯 Search Features

### What Gets Searched:

- **Product Title/Name** - Main product name
- **Product Description** - Full product description text
- **Brand Name** - Brand/manufacturer name

### Search Capabilities:

- ✅ Case-insensitive search
- ✅ Partial matching (finds "shirt" in "T-shirt")
- ✅ Combines with filters (category, brand, price)
- ✅ Multiple sort options
- ✅ Pagination support
- ✅ Relevance scoring

---

## 📡 API Endpoints

### 1. Simple Search in Products List

**Endpoint:** `GET /api/v1/products`

**Query Parameters:**

```
search       - Search term (searches title, description, brand)
category     - Filter by category slug
subcategory  - Filter by subcategory slug
brand        - Filter by brand slug
sort_by      - Sort order (newest, popular, price_high_to_low, price_low_to_high)
page         - Page number (default: 1)
limit        - Items per page (default: 20)
```

**Example:**

```bash
GET /api/v1/products?search=shirt&category=mens&sort_by=popular&page=1&limit=20
```

**Response:**

```json
[
  {
    "id": "1",
    "name": "Classic T-Shirt",
    "brand": "Nike",
    "price": 29.99,
    "originalPrice": 39.99,
    "discount": 25,
    "image": "https://example.com/image.jpg",
    "images": ["https://example.com/image1.jpg", "..."],
    "category": "Men's Clothing",
    "subcategory": "T-Shirts",
    "sizes": ["S", "M", "L", "XL"],
    "colors": ["Black", "White", "Blue"],
    "rating": 4.5,
    "reviews": 120,
    "salesCount": 500,
    "inStock": true,
    "description": "Comfortable cotton t-shirt...",
    "features": []
  }
]
```

---

### 2. Advanced Search (Dedicated Endpoint)

**Endpoint:** `GET /api/v1/products/search`

**Query Parameters:**

```
q            - Search query (REQUIRED, min 1 character)
category     - Filter by category slug
brand        - Filter by brand slug
min_price    - Minimum price filter
max_price    - Maximum price filter
sort_by      - Sort order (newest, popular, price_low, price_high, relevance)
page         - Page number (default: 1, min: 1)
limit        - Items per page (default: 20, min: 1, max: 100)
```

**Example:**

```bash
GET /api/v1/products/search?q=jacket&min_price=50&max_price=200&sort_by=relevance&page=1&limit=20
```

**Response:**

```json
{
  "query": "jacket",
  "results": [
    {
      "id": "5",
      "name": "Winter Jacket",
      "brand": "North Face",
      "price": 149.99,
      ...
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20,
  "total_pages": 3,
  "has_more": true
}
```

---

## 🧪 Usage Examples

### Example 1: Basic Text Search

```bash
curl "http://localhost:8000/api/v1/products/search?q=shoes"
```

### Example 2: Search with Category Filter

```bash
curl "http://localhost:8000/api/v1/products/search?q=running&category=sports"
```

### Example 3: Search with Price Range

```bash
curl "http://localhost:8000/api/v1/products/search?q=dress&min_price=30&max_price=100"
```

### Example 4: Search with Brand and Sort

```bash
curl "http://localhost:8000/api/v1/products/search?q=sneakers&brand=nike&sort_by=price_low"
```

### Example 5: Paginated Search

```bash
curl "http://localhost:8000/api/v1/products/search?q=shirt&page=2&limit=10"
```

### Example 6: Search by Brand Name

```bash
curl "http://localhost:8000/api/v1/products?search=nike"
```

Returns all products from Nike brand.

---

## 📊 Sort Options

| Sort Option  | Description                | Use Case         |
| ------------ | -------------------------- | ---------------- |
| `relevance`  | Best match first (default) | General search   |
| `newest`     | Latest products first      | "New arrivals"   |
| `popular`    | Most sold products first   | "Trending"       |
| `price_low`  | Cheapest first             | Budget shoppers  |
| `price_high` | Most expensive first       | Premium shoppers |

---

## 🎯 Search Tips

### For Best Results:

1. **Use Specific Terms**

   - Good: "red running shoes"
   - Better: "nike red running"

2. **Combine Filters**

   ```bash
   ?q=jacket&category=mens&min_price=50&max_price=150&sort_by=popular
   ```

3. **Use Relevance Sort for Text Search**

   - Prioritizes exact title matches
   - Then checks description matches

4. **Pagination**
   - Use `page` and `limit` for large result sets
   - Check `has_more` field to see if more results exist

---

## 🔍 Search Behavior

### Case Insensitive

```bash
"SHIRT" = "shirt" = "Shirt"
```

### Partial Matching

```bash
Search: "run"
Matches: "Running shoes", "Nike Run Club", "Trail runner"
```

### Multi-word Search

```bash
Search: "blue jacket"
Matches products with "blue" OR "jacket" in title/description
```

---

## 💡 Frontend Integration

### React Example:

```javascript
// Search products
const searchProducts = async (query, filters = {}) => {
  const params = new URLSearchParams({
    q: query,
    ...filters,
  });

  const response = await fetch(`/api/v1/products/search?${params}`);

  const data = await response.json();

  return {
    products: data.results,
    total: data.total,
    hasMore: data.has_more,
  };
};

// Usage
const results = await searchProducts("shoes", {
  category: "mens",
  min_price: 50,
  max_price: 150,
  sort_by: "popular",
  page: 1,
  limit: 20,
});
```

### JavaScript (Vanilla):

```javascript
// Search with autocomplete
const searchInput = document.getElementById("search");
let searchTimeout;

searchInput.addEventListener("input", (e) => {
  clearTimeout(searchTimeout);

  searchTimeout = setTimeout(async () => {
    const query = e.target.value;

    if (query.length < 2) return;

    const response = await fetch(`/api/v1/products/search?q=${query}&limit=5`);

    const data = await response.json();
    displayResults(data.results);
  }, 300); // Debounce 300ms
});
```

---

## ⚡ Performance Tips

1. **Use Pagination**

   - Don't load all results at once
   - Default limit: 20 items

2. **Debounce Search Input**

   - Wait 300ms after user stops typing
   - Reduces unnecessary API calls

3. **Cache Results**

   - Cache search results on frontend
   - Use same query? Return cached data

4. **Limit Search Length**
   - Min: 1 character
   - Recommended min: 2-3 characters for better results

---

## 🚀 Response Fields

### ProductSchema

```typescript
{
  id: string              // Product ID
  name: string            // Product title
  brand: string           // Brand name
  price: number           // Current price
  originalPrice?: number  // Original price (if discounted)
  discount?: number       // Discount percentage
  image: string           // Main product image
  images: string[]        // All product images
  category: string        // Category name
  subcategory?: string    // Subcategory name
  sizes: string[]         // Available sizes
  colors: string[]        // Available colors
  rating: number          // Average rating (0-5)
  reviews: number         // Number of reviews
  salesCount: number      // Total sales
  inStock: boolean        // Stock availability
  description?: string    // Product description
  features: string[]      // Product features
}
```

### SearchResponse (Advanced Endpoint Only)

```typescript
{
  query: string           // Original search query
  results: Product[]      // Array of products
  total: number           // Total results found
  page: number            // Current page
  limit: number           // Items per page
  total_pages: number     // Total number of pages
  has_more: boolean       // More pages available?
}
```

---

## 📝 Notes

- **Minimum Search Length:** 1 character (recommended 2-3 for better results)
- **Maximum Items Per Page:** 100
- **Default Sort:** Relevance (for search), newest (for general listing)
- **Search Scope:** Title, Description, Brand name
- **Response Time:** Typically < 100ms for most searches

---

## 🎉 Summary

The search feature provides:
✅ Fast, case-insensitive text search  
✅ Multi-field search (title, description, brand)  
✅ Advanced filtering (category, brand, price)  
✅ Flexible sorting options  
✅ Pagination support  
✅ Detailed response with metadata

Perfect for building search bars, product finders, and filtered product listings!
