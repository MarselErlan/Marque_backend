# 🛍️ TDD Plan: Catalog System Implementation

## 📋 **Overview**

Building a complete catalog system with:

1. **Left Sidebar Navigation** - Categories with subcategories
2. **Product Listing Page** - With filters, sorting, pagination
3. **Filter Options** - Price, size, color, brand, material, style
4. **Sort Options** - Price (high/low), popular, newest, rating
5. **Pagination** - Page-based navigation

---

## 🎯 **Requirements from Design**

### Main Categories (Left Sidebar):

- 👔 **Мужчинам** (Men) - 2355 items
- 👗 **Женщинам** (Women) - 2375 items
- 👶 **Детям** (Kids)
- 🏃 **Спорт** (Sport)
- 👟 **Обувь** (Shoes)
- 💎 **Аксессуары** (Accessories)
- ⭐ **Бренды** (Brands)

### Subcategories for Men:

- 👕 **Футболки и поло** - 2355 items
- 🧥 **Свитшоты и худи** - 8533 items
- 👖 **Брюки и шорты** - 643 items
- 🧥 **Верхня одежда** - 74 items
- 👔 **Рубашки** - 2375 items
- 👖 **Джинсы** - 1264 items
- 🤵 **Костюмы и пиджаки** - 124 items
- 🩲 **Нижнее бельё** - 7634 items
- 🏃 **Спортивная одежда** - 2362 items
- 🏠 **Домашняя одежда** - 23 items

### Subcategory Page Features:

1. **Breadcrumbs**: Мужчинам > Футболки и поло
2. **Title**: "Футболки и поло" (22 128 товаров)
3. **Filters** (Left sidebar):
   - По популярности
   - Все фильтры
   - Максимально
   - Футболки и поло
   - Цена (min-max range)
   - Пол
   - Размеры (40, 42, 44, 46, 48, 50...)
   - Категории (filter categories)
   - Мужской?
4. **Sorting**: По популярности, Цена (↓/↑), Новинки
5. **Product Grid**: Cards with image, title, price, discount
6. **Pagination**: 1, 2, 3, 4, 5... 10

---

## 🔴 **RED Phase: Write Tests First**

### Test Suite 1: Category Navigation API

```python
tests/integration/test_catalog_navigation.py
```

**Tests**:

1. ✅ `test_get_all_main_categories` - Get all main categories with product counts
2. ✅ `test_get_category_with_subcategories` - Get specific category with subcategories
3. ✅ `test_get_subcategories_by_category_slug` - Get subcategories for a category
4. ✅ `test_category_includes_product_count` - Each category has product count
5. ✅ `test_subcategory_includes_product_count` - Each subcategory has product count
6. ✅ `test_inactive_categories_not_returned` - Only active categories shown
7. ✅ `test_categories_sorted_by_order` - Categories in correct order

### Test Suite 2: Product Listing by Subcategory

```python
tests/integration/test_catalog_products.py
```

**Tests**:

1. ✅ `test_get_products_by_subcategory` - List products for a subcategory
2. ✅ `test_products_pagination` - Pagination works correctly
3. ✅ `test_products_include_all_info` - Products have all required fields
4. ✅ `test_empty_subcategory_returns_empty_list` - Handle empty categories
5. ✅ `test_invalid_subcategory_returns_404` - Handle invalid slugs

### Test Suite 3: Product Filtering

```python
tests/integration/test_catalog_filters.py
```

**Tests**:

1. ✅ `test_filter_by_price_range` - Filter products by min/max price
2. ✅ `test_filter_by_size` - Filter products by size
3. ✅ `test_filter_by_color` - Filter products by color
4. ✅ `test_filter_by_brand` - Filter products by brand
5. ✅ `test_filter_by_material` - Filter products by material
6. ✅ `test_filter_by_style` - Filter products by style
7. ✅ `test_multiple_filters_combined` - Combine multiple filters
8. ✅ `test_get_available_filters_for_subcategory` - Get filter options
9. ✅ `test_filters_show_count` - Each filter shows product count

### Test Suite 4: Product Sorting

```python
tests/integration/test_catalog_sorting.py
```

**Tests**:

1. ✅ `test_sort_by_popularity` - Sort by sold_count desc
2. ✅ `test_sort_by_newest` - Sort by created_at desc
3. ✅ `test_sort_by_price_low_to_high` - Sort by price asc
4. ✅ `test_sort_by_price_high_to_low` - Sort by price desc
5. ✅ `test_sort_by_rating` - Sort by rating_avg desc
6. ✅ `test_default_sort_is_popularity` - Default sorting
7. ✅ `test_invalid_sort_param_ignored` - Handle invalid sort

### Test Suite 5: Complete Catalog Flow

```python
tests/integration/test_catalog_e2e.py
```

**Tests**:

1. ✅ `test_complete_catalog_flow` - Full flow from category to product
2. ✅ `test_filter_and_sort_together` - Combine filters and sorting
3. ✅ `test_pagination_with_filters` - Pagination works with filters
4. ✅ `test_breadcrumb_data` - Breadcrumb information included
5. ✅ `test_subcategory_metadata` - Title, count, description

---

## 🟢 **GREEN Phase: Implement Features**

### Step 1: Enhanced Category Schema

**File**: `src/app_01/schemas/category.py`

```python
class CategoryWithCountSchema(BaseModel):
    id: int
    name: str
    slug: str
    icon: Optional[str]
    product_count: int
    is_active: bool
    sort_order: int

class SubcategoryWithCountSchema(BaseModel):
    id: int
    name: str
    slug: str
    image_url: Optional[str]
    product_count: int
    is_active: bool
    sort_order: int

class CategoryDetailSchema(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    icon: Optional[str]
    product_count: int
    subcategories: List[SubcategoryWithCountSchema]
```

### Step 2: Filter Options Schema

**File**: `src/app_01/schemas/product.py` (enhance)

```python
class FilterOptionSchema(BaseModel):
    value: str
    label: str
    count: int

class FilterGroupSchema(BaseModel):
    filter_type: str  # price, size, color, brand, etc.
    label: str  # Display name
    options: List[FilterOptionSchema]

class AvailableFiltersSchema(BaseModel):
    filters: List[FilterGroupSchema]
```

### Step 3: Product List Response Schema

**File**: `src/app_01/schemas/product.py` (enhance)

```python
class ProductListResponse(BaseModel):
    # Breadcrumb data
    category: CategorySchema
    subcategory: SubcategorySchema

    # Products
    products: List[ProductSchema]

    # Pagination
    total: int
    page: int
    limit: int
    total_pages: int
    has_more: bool

    # Available filters
    available_filters: AvailableFiltersSchema

    # Applied filters
    applied_filters: Dict[str, List[str]]
    applied_sort: Optional[str]
```

### Step 4: Enhanced Category Router

**File**: `src/app_01/routers/category_router.py` (enhance)

**New endpoints**:

```python
GET /api/categories
  → Get all main categories with product counts

GET /api/categories/{category_slug}
  → Get category detail with subcategories

GET /api/categories/{category_slug}/subcategories
  → Get subcategories for a category

GET /api/categories/{category_slug}/{subcategory_slug}/products
  → Get products for subcategory with filters, sorting, pagination

GET /api/categories/{category_slug}/{subcategory_slug}/filters
  → Get available filter options for subcategory
```

### Step 5: Product Service Layer

**File**: `src/app_01/services/catalog_service.py` (NEW)

**Methods**:

```python
def get_products_for_subcategory(
    db, category_slug, subcategory_slug,
    filters, sort_by, page, limit
)

def get_available_filters_for_subcategory(
    db, category_slug, subcategory_slug
)

def apply_product_filters(query, filters)

def apply_product_sorting(query, sort_by)
```

---

## 🔵 **REFACTOR Phase**

1. **Optimize queries** - Use eager loading for relationships
2. **Cache filter options** - Store common filter results
3. **Add indexes** - Ensure fast filtering and sorting
4. **Extract common logic** - DRY principles
5. **Add logging** - Track popular filters and sorts

---

## 📊 **Expected API Structure**

### 1. Get All Categories

```http
GET /api/categories
```

**Response**:

```json
{
  "categories": [
    {
      "id": 1,
      "name": "Мужчинам",
      "slug": "men",
      "icon": "fa-solid fa-mars",
      "product_count": 2355,
      "sort_order": 1
    },
    {
      "id": 2,
      "name": "Женщинам",
      "slug": "women",
      "icon": "fa-solid fa-venus",
      "product_count": 2375,
      "sort_order": 2
    }
  ]
}
```

### 2. Get Category with Subcategories

```http
GET /api/categories/men
```

**Response**:

```json
{
  "id": 1,
  "name": "Мужчинам",
  "slug": "men",
  "description": "Одежда для мужчин",
  "icon": "fa-solid fa-mars",
  "product_count": 2355,
  "subcategories": [
    {
      "id": 1,
      "name": "Футболки и поло",
      "slug": "t-shirts-polos",
      "image_url": "...",
      "product_count": 2355,
      "sort_order": 1
    },
    {
      "id": 2,
      "name": "Свитшоты и худи",
      "slug": "sweatshirts-hoodies",
      "product_count": 8533,
      "sort_order": 2
    }
  ]
}
```

### 3. Get Products for Subcategory (with filters)

```http
GET /api/categories/men/t-shirts-polos/products?
    page=1&
    limit=20&
    sort=popularity&
    price_min=1000&
    price_max=5000&
    sizes=40,42,44&
    colors=black,white&
    brands=hm,zara
```

**Response**:

```json
{
  "category": {
    "id": 1,
    "name": "Мужчинам",
    "slug": "men"
  },
  "subcategory": {
    "id": 1,
    "name": "Футболки и поло",
    "slug": "t-shirts-polos",
    "product_count": 2355
  },
  "products": [
    {
      "id": "1",
      "name": "Футболка спорт. из хлопка",
      "brand": "H&M",
      "price": 2999,
      "originalPrice": 3999,
      "discount": 25,
      "image": "...",
      "images": ["...", "..."],
      "sizes": ["RUS 40", "RUS 42", "RUS 44"],
      "colors": ["black", "white"],
      "rating": 4.5,
      "reviews": 123,
      "salesCount": 456,
      "inStock": true
    }
  ],
  "total": 2355,
  "page": 1,
  "limit": 20,
  "total_pages": 118,
  "has_more": true,
  "available_filters": {
    "filters": [
      {
        "filter_type": "price",
        "label": "Цена",
        "options": [
          { "value": "0-2000", "label": "0-2000 сом", "count": 450 },
          { "value": "2000-5000", "label": "2000-5000 сом", "count": 890 }
        ]
      },
      {
        "filter_type": "size",
        "label": "Размер",
        "options": [
          { "value": "40", "label": "RUS 40", "count": 234 },
          { "value": "42", "label": "RUS 42", "count": 345 }
        ]
      },
      {
        "filter_type": "color",
        "label": "Цвет",
        "options": [
          { "value": "black", "label": "Черный", "count": 567 },
          { "value": "white", "label": "Белый", "count": 432 }
        ]
      },
      {
        "filter_type": "brand",
        "label": "Бренд",
        "options": [
          { "value": "hm", "label": "H&M", "count": 234 },
          { "value": "zara", "label": "Zara", "count": 189 }
        ]
      }
    ]
  },
  "applied_filters": {
    "price_min": "1000",
    "price_max": "5000",
    "sizes": ["40", "42", "44"],
    "colors": ["black", "white"],
    "brands": ["hm", "zara"]
  },
  "applied_sort": "popularity"
}
```

### 4. Get Available Filters

```http
GET /api/categories/men/t-shirts-polos/filters
```

**Response**: Same as `available_filters` above

---

## 📝 **Test Organization**

```
tests/
├── integration/
│   ├── test_catalog_navigation.py  (7 tests)
│   ├── test_catalog_products.py    (5 tests)
│   ├── test_catalog_filters.py     (9 tests)
│   ├── test_catalog_sorting.py     (7 tests)
│   └── test_catalog_e2e.py         (5 tests)
└── fixtures/
    └── catalog_fixtures.py         (Sample data)
```

**Total: 33 comprehensive tests**

---

## 🎯 **Success Criteria**

### Functional:

- ✅ All 33 tests passing
- ✅ Categories load with correct counts
- ✅ Subcategories filterable and sortable
- ✅ Products display with all info
- ✅ Filters work correctly
- ✅ Sorting works correctly
- ✅ Pagination works correctly
- ✅ API responses match design specs

### Performance:

- ✅ Category list loads < 100ms
- ✅ Product list loads < 500ms
- ✅ Filter application < 300ms
- ✅ Proper database indexing
- ✅ Efficient SQL queries (N+1 avoided)

### UX:

- ✅ Clear breadcrumbs
- ✅ Product counts accurate
- ✅ Filter options relevant
- ✅ Fast response times
- ✅ Proper error handling

---

## 🚀 **Implementation Order**

### Phase 1: Tests & Schemas (30 min)

1. Write all test files (RED phase)
2. Create enhanced schemas
3. Run tests (all failing)

### Phase 2: Category Enhancement (45 min)

4. Enhance category router
5. Add product count logic
6. Test category endpoints (GREEN)

### Phase 3: Product Listing (60 min)

7. Create catalog service
8. Implement product listing
9. Add pagination
10. Test product endpoints (GREEN)

### Phase 4: Filtering (60 min)

11. Implement filter logic
12. Create filter option generation
13. Test all filter combinations (GREEN)

### Phase 5: Sorting (30 min)

14. Implement sorting logic
15. Test all sort options (GREEN)

### Phase 6: Integration (30 min)

16. Test complete flows
17. Optimize queries
18. Add logging

**Total Time: ~4 hours**

---

## 📚 **Files to Create/Modify**

### New Files:

- `src/app_01/services/catalog_service.py`
- `tests/integration/test_catalog_navigation.py`
- `tests/integration/test_catalog_products.py`
- `tests/integration/test_catalog_filters.py`
- `tests/integration/test_catalog_sorting.py`
- `tests/integration/test_catalog_e2e.py`
- `tests/fixtures/catalog_fixtures.py`

### Modified Files:

- `src/app_01/schemas/category.py` (enhance)
- `src/app_01/schemas/product.py` (enhance)
- `src/app_01/routers/category_router.py` (enhance)
- `src/app_01/models/products/category.py` (add methods)
- `src/app_01/models/products/product.py` (add methods)

---

## ✅ **Ready to Start?**

**Next Step**: Start with **RED Phase** - Write the first test suite!

Let's begin with `test_catalog_navigation.py` - the foundation of the catalog system.

---

**Status**: 🔴 RED Phase Ready  
**Next**: Write failing tests for category navigation  
**Goal**: 33 comprehensive tests → Full catalog system! 🛍️
