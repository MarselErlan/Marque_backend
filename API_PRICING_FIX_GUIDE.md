# API Pricing Fix Guide - Use New Product Properties

## ❌ Current Problem in Your API

Your current API code (in `product_router.py`) has this issue:

```python
# ❌ PROBLEM: Only gets FIRST SKU price
price = skus[0].price if skus else 0
original_price = skus[0].original_price if skus and skus[0].original_price else None
discount = int(((original_price - price) / original_price) * 100) if original_price and price and original_price > price else 0
```

**Why this is wrong:**

- If you have a product with multiple SKUs (e.g., different sizes), each might have different prices
- `skus[0]` just picks the first one randomly (could be the most expensive!)
- Customers see inconsistent prices
- Not showing the "from" price (minimum price)

## ✅ Solution: Use New Product Properties

Your improved Product model now has smart properties that handle this correctly:

```python
# ✅ CORRECT: Smart price calculation
price = product.display_price          # Always shows minimum price
original_price = product.original_price  # Minimum original price
discount = product.discount_percentage   # Calculated correctly
```

## 🔧 How to Fix Your API

### File: `src/app_01/routers/product_router.py`

### Fix #1: Product List Endpoint (around line 516-560)

**BEFORE:**

```python
for p in products:
    skus = p.skus

    # ... image code ...

    # ❌ OLD CODE
    price = skus[0].price if skus else 0
    original_price = skus[0].original_price if skus and skus[0].original_price else None
    discount = int(((original_price - price) / original_price) * 100) if original_price and price and original_price > price else 0

    response_products.append(ProductSchema(
        id=str(p.id),
        name=p.title,
        slug=p.slug,
        brand=p.brand.name if p.brand else "",
        price=price,
        originalPrice=original_price,
        discount=discount,
        # ... rest ...
    ))
```

**AFTER:**

```python
for p in products:
    # ... image code ...

    # ✅ NEW CODE - Use smart properties
    response_products.append(ProductSchema(
        id=str(p.id),
        name=p.title,
        slug=p.slug,
        brand=p.brand.name if p.brand else "",
        price=p.display_price,           # ✅ Smart minimum price
        originalPrice=p.original_price,  # ✅ For discount calculation
        discount=p.discount_percentage,  # ✅ Auto-calculated
        image=p.get_image_or_default(),  # ✅ With fallback
        images=p.get_all_images(),       # ✅ All images
        # ... rest stays the same ...
        inStock=p.is_in_stock,
        description=p.description,
    ))
```

### Fix #2: Product Detail Endpoint (around line 595-619)

**BEFORE:**

```python
price = skus[0].price if skus else 0
original_price = skus[0].original_price if skus and skus[0].original_price else None
discount = int(((original_price - price) / original_price) * 100) if original_price and price and original_price > price else 0

return ProductSchema(
    id=str(p.id),
    name=p.title,
    price=price,
    originalPrice=original_price,
    discount=discount,
    # ...
)
```

**AFTER:**

```python
# ✅ Track product view for analytics
p.increment_view_count()
db.commit()

return ProductSchema(
    id=str(p.id),
    name=p.title,
    price=p.display_price,           # ✅ Smart price
    originalPrice=p.original_price,  # ✅ Smart original
    discount=p.discount_percentage,  # ✅ Auto-calculated
    image=p.get_image_or_default(),  # ✅ With fallback
    images=p.get_all_images(),       # ✅ All images
    stockStatus=p.stock_status,      # ✅ "in_stock", "low_stock", "out_of_stock"
    isNew=p.is_new,                  # ✅ New arrival flag
    isTrending=p.is_trending,        # ✅ Trending flag
    viewCount=p.view_count,          # ✅ Analytics
    # ...
)
```

### Fix #3: Product Detail with Full Info (around line 278)

**Add these fields to ProductDetailSchema response:**

```python
return ProductDetailSchema(
    id=product.id,
    title=product.title,
    slug=product.slug,
    description=product.description,

    # ✅ Use smart pricing
    price_min=product.min_price,
    price_max=product.max_price,
    price_display=product.display_price,
    original_price=product.original_price,
    discount_percentage=product.discount_percentage,
    price_range=product.price_range,  # "5000 - 7500 сом"

    # ✅ Stock info
    in_stock=product.is_in_stock,
    stock_status=product.stock_status,
    is_low_stock=product.is_low_stock,

    # ✅ Status flags
    is_new=product.is_new,
    is_trending=product.is_trending,
    is_featured=product.is_featured,

    # ✅ Analytics
    view_count=product.view_count,
    sold_count=product.sold_count,

    # ✅ Ratings
    rating=product.rating_avg,
    rating_count=product.rating_count,

    # ✅ Images
    main_image=product.get_image_or_default(),
    images=product.get_all_images(),

    # ✅ Available options (only in-stock)
    available_sizes=product.get_available_sizes(),
    available_colors=product.get_available_colors(),

    # ... SKUs, brand, category, etc ...
)
```

## 🎯 New Homepage Endpoints to Add

### Add Featured Products Endpoint

```python
@router.get("/products/featured", response_model=List[ProductSchema])
def get_featured_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get featured products for homepage"""
    products = Product.get_featured_products(db, limit=limit)
    return [serialize_product(p) for p in products]
```

### Add New Arrivals Endpoint

```python
@router.get("/products/new-arrivals", response_model=List[ProductSchema])
def get_new_arrivals(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=50)
):
    """Get new arrival products"""
    products = Product.get_new_products(db, limit=limit)
    return [serialize_product(p) for p in products]
```

### Add Trending Products Endpoint

```python
@router.get("/products/trending", response_model=List[ProductSchema])
def get_trending_products(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get trending products"""
    products = Product.get_trending_products(db, limit=limit)
    return [serialize_product(p) for p in products]
```

### Add Best Sellers Endpoint

```python
@router.get("/products/best-sellers", response_model=List[ProductSchema])
def get_best_sellers(
    db: Session = Depends(get_db),
    limit: int = Query(10, ge=1, le=50)
):
    """Get best selling products"""
    products = Product.get_best_sellers(db, limit=limit)
    return [serialize_product(p) for p in products]
```

### Add On Sale Endpoint

```python
@router.get("/products/on-sale", response_model=List[ProductSchema])
def get_on_sale_products(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Get products on sale"""
    products = Product.get_on_sale_products(db)

    # Apply pagination
    offset = (page - 1) * limit
    paginated = products[offset:offset + limit]

    return [serialize_product(p) for p in paginated]
```

## 📊 Helper Function for Serialization

Create a helper function to avoid code duplication:

```python
def serialize_product(p: Product) -> ProductSchema:
    """Convert Product model to ProductSchema"""
    return ProductSchema(
        id=str(p.id),
        name=p.title,
        slug=p.slug,
        brand=p.brand.name if p.brand else "",
        price=p.display_price,
        originalPrice=p.original_price,
        discount=p.discount_percentage,
        image=p.get_image_or_default(),
        images=p.get_all_images(),
        category=p.category.name if p.category else "",
        subcategory=p.subcategory.name if p.subcategory else "",
        sizes=p.get_available_sizes(),
        colors=p.get_available_colors(),
        rating=p.rating_avg,
        reviews=p.rating_count,
        salesCount=p.sold_count,
        viewCount=p.view_count,
        inStock=p.is_in_stock,
        stockStatus=p.stock_status,
        isNew=p.is_new,
        isTrending=p.is_trending,
        isFeatured=p.is_featured,
        description=p.description,
        features=[]  # Add if you have features
    )
```

Then use it everywhere:

```python
# In list endpoint
response_products = [serialize_product(p) for p in products]
return response_products

# In detail endpoint
return serialize_product(product)
```

## 🎨 Frontend Usage Examples

### Show Price Range

```tsx
// If product has multiple prices
{
  product.price_min !== product.price_max ? (
    <span>
      от {product.price_min} - {product.price_max} сом
    </span>
  ) : (
    <span>{product.price} сом</span>
  );
}
```

### Show Stock Status

```tsx
{
  product.stock_status === "out_of_stock" && (
    <span className="text-red-600">Нет в наличии</span>
  );
}
{
  product.stock_status === "low_stock" && (
    <span className="text-yellow-600">Осталось мало!</span>
  );
}
{
  product.stock_status === "in_stock" && (
    <span className="text-green-600">В наличии</span>
  );
}
```

### Show Badges

```tsx
{
  product.isNew && <Badge>Новинка</Badge>;
}
{
  product.isTrending && <Badge variant="hot">Хит продаж</Badge>;
}
{
  product.discount > 0 && <Badge variant="sale">-{product.discount}%</Badge>;
}
```

## ✅ Benefits After Fixing

1. **Correct Pricing**: Always shows minimum price across all SKUs
2. **Better UX**: Customers see "от 5000 сом" for multi-variant products
3. **Accurate Discounts**: Properly calculated from original prices
4. **Stock Status**: Clear visibility of availability
5. **Analytics**: Track product views automatically
6. **Marketing**: New/Trending/Featured sections
7. **Performance**: Uses cached properties instead of recalculating

## 🚀 Quick Steps to Apply

1. **Run migration**: `alembic upgrade head`
2. **Update products**: `python update_products_with_new_fields.py`
3. **Fix API endpoints**: Replace old pricing code with new properties
4. **Add new endpoints**: Featured, trending, new arrivals
5. **Update frontend**: Use new fields for badges, stock status
6. **Test**: Check that prices display correctly
7. **Deploy**: You're ready! 🎉

## 📝 Schema Updates Needed

Make sure your `ProductSchema` includes these fields:

```python
class ProductSchema(BaseModel):
    id: str
    name: str
    slug: str
    price: float
    originalPrice: Optional[float]
    discount: int

    # Add these new fields
    stockStatus: Optional[str]  # "in_stock", "low_stock", "out_of_stock"
    isNew: Optional[bool]
    isTrending: Optional[bool]
    isFeatured: Optional[bool]
    viewCount: Optional[int]

    # ... rest of fields ...
```

---

**Need help?** Check `PRODUCT_MODEL_IMPROVEMENTS.md` for full documentation!
