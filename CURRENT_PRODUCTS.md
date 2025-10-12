# 🛍️ Current Products in Database

**Last Updated**: October 12, 2025  
**Total Products**: 5 test products

---

## 📊 Product Catalog

### 1. Classic White T-Shirt ⭐ Featured

- **Brand**: MARQUE
- **Category**: Мужчинам → Футболки
- **Slug**: `classic-white-tshirt-test`
- **Price**: 990 сом
- **Stock**: 63 units
- **Description**: Comfortable cotton t-shirt perfect for everyday wear. Made from 100% premium cotton.
- **Composition**: 100% Cotton
- **Article**: TSH-001

**Variants (4 SKUs)**:

| Size | Color | Price   | Stock | SKU Code       |
| ---- | ----- | ------- | ----- | -------------- |
| S    | White | 990 сом | 15    | TSH-001-S-WHI  |
| M    | White | 990 сом | 20    | TSH-001-M-WHI  |
| L    | White | 990 сом | 18    | TSH-001-L-WHI  |
| XL   | White | 990 сом | 10    | TSH-001-XL-WHI |

**Images**: 2 professional product photos

---

### 2. Blue Denim Jeans ⭐ Featured

- **Brand**: MARQUE
- **Category**: Мужчинам → Футболки
- **Slug**: `blue-denim-jeans-test`
- **Price**: 2,990 сом ~~3,990 сом~~ (25% OFF!)
- **Stock**: 45 units
- **Description**: Classic fit denim jeans. Durable and stylish, perfect for any occasion.
- **Composition**: 98% Cotton, 2% Elastane
- **Article**: JNS-002

**Variants (4 SKUs)**:

| Size | Color | Price     | Original Price | Stock | SKU Code       |
| ---- | ----- | --------- | -------------- | ----- | -------------- |
| 30   | Blue  | 2,990 сом | 3,990 сом      | 12    | JNS-002-30-BLU |
| 32   | Blue  | 2,990 сом | 3,990 сом      | 15    | JNS-002-32-BLU |
| 34   | Blue  | 2,990 сом | 3,990 сом      | 10    | JNS-002-34-BLU |
| 36   | Blue  | 2,990 сом | 3,990 сом      | 8     | JNS-002-36-BLU |

**Images**: 2 professional product photos

---

### 3. Black Hoodie Premium

- **Brand**: MARQUE
- **Category**: Мужчинам → Футболки
- **Slug**: `black-hoodie-premium-test`
- **Price**: 3,490 сом
- **Stock**: 43 units
- **Description**: Cozy fleece hoodie with kangaroo pocket. Perfect for cool weather.
- **Composition**: 80% Cotton, 20% Polyester
- **Article**: HOD-003

**Variants (5 SKUs)**:

| Size | Color | Price     | Stock | SKU Code       |
| ---- | ----- | --------- | ----- | -------------- |
| M    | Black | 3,490 сом | 8     | HOD-003-M-BLA  |
| L    | Black | 3,490 сом | 12    | HOD-003-L-BLA  |
| XL   | Black | 3,490 сом | 6     | HOD-003-XL-BLA |
| M    | Gray  | 3,490 сом | 10    | HOD-003-M-GRA  |
| L    | Gray  | 3,490 сом | 7     | HOD-003-L-GRA  |

**Images**: 2 professional product photos

---

### 4. Casual Shirt Button-Up

- **Brand**: MARQUE
- **Category**: Мужчинам → Футболки
- **Slug**: `casual-shirt-button-up-test`
- **Price**: 1,990 сом
- **Stock**: 62 units
- **Description**: Smart casual button-up shirt. Ideal for office or casual outings.
- **Composition**: 100% Cotton
- **Article**: SHT-004

**Variants (5 SKUs)**:

| Size | Color | Price     | Stock | SKU Code      |
| ---- | ----- | --------- | ----- | ------------- |
| S    | Blue  | 1,990 сом | 10    | SHT-004-S-BLU |
| M    | Blue  | 1,990 сом | 15    | SHT-004-M-BLU |
| L    | Blue  | 1,990 сом | 12    | SHT-004-L-BLU |
| M    | White | 1,990 сом | 14    | SHT-004-M-WHI |
| L    | White | 1,990 сом | 11    | SHT-004-L-WHI |

**Images**: 2 professional product photos

---

### 5. Sport Track Pants ⭐ Featured

- **Brand**: MARQUE
- **Category**: Мужчинам → Футболки
- **Slug**: `sport-track-pants-test`
- **Price**: 2,490 сом
- **Stock**: 65 units
- **Description**: Comfortable athletic track pants with elastic waistband. Perfect for workouts.
- **Composition**: 65% Polyester, 35% Cotton
- **Article**: PNT-005

**Variants (4 SKUs)**:

| Size | Color | Price     | Stock | SKU Code       |
| ---- | ----- | --------- | ----- | -------------- |
| M    | Black | 2,490 сом | 20    | PNT-005-M-BLA  |
| L    | Black | 2,490 сом | 18    | PNT-005-L-BLA  |
| XL   | Black | 2,490 сом | 12    | PNT-005-XL-BLA |
| M    | Navy  | 2,490 сом | 15    | PNT-005-M-NAV  |

**Images**: 2 professional product photos

---

## 📈 Overall Statistics

| Metric            | Value           |
| ----------------- | --------------- |
| Total Products    | 5               |
| Total SKUs        | 22              |
| Total Stock       | 278             |
| Total Images      | 10              |
| Featured Products | 3               |
| Active Products   | 5               |
| Average Stock/SKU | 12.6            |
| Price Range       | 990 - 3,490 сом |

---

## 🎯 Product Categories

### By Price Range

- **Budget (< 1,500 сом)**: 1 product
- **Mid-range (1,500 - 3,000 сом)**: 3 products
- **Premium (> 3,000 сом)**: 1 product

### By Stock Availability

- **High Stock (> 50 units)**: 3 products
- **Medium Stock (30-50 units)**: 2 products
- **Low Stock (< 30 units)**: 0 products

---

## 🔌 API Endpoints to Test

### Get All Products

```bash
curl http://localhost:8000/api/v1/products
```

### Get Product by ID

```bash
# Get first test product
curl http://localhost:8000/api/v1/products/1
```

### Get Product by Slug

```bash
curl http://localhost:8000/api/v1/products/slug/classic-white-tshirt-test
```

### Search Products

```bash
# Search for "shirt"
curl http://localhost:8000/api/v1/products/search?q=shirt

# Search for "jeans"
curl http://localhost:8000/api/v1/products/search?q=jeans
```

### Filter Products

```bash
# Filter by category
curl http://localhost:8000/api/v1/products?category=men

# Filter by brand
curl http://localhost:8000/api/v1/products?brand=marque

# Filter by price range
curl http://localhost:8000/api/v1/products?min_price=1000&max_price=3000
```

### Get Featured Products

```bash
curl http://localhost:8000/api/v1/products?featured=true
```

---

## 🎛️ Admin Panel Access

**URL**: http://localhost:8001/admin/product/list

### Features Available:

- ✅ View all products with filtering
- ✅ Edit product details
- ✅ Manage SKUs (sizes, colors, prices)
- ✅ Upload/manage product images
- ✅ Set featured products
- ✅ Toggle active/inactive status
- ✅ View stock levels
- ✅ Search products

---

## 📝 Quick Actions

### View All Products

```bash
python3 -c "from src.app_01.db import Market, db_manager; from src.app_01.models.products import Product; session = db_manager.get_session_factory(Market.KG)(); products = session.query(Product).all(); [print(f'{i+1}. {p.title} - {p.price_range}') for i, p in enumerate(products)]; session.close()"
```

### Check Stock Levels

```bash
python3 -c "from src.app_01.db import Market, db_manager; from src.app_01.models.products import Product; session = db_manager.get_session_factory(Market.KG)(); products = session.query(Product).all(); print('Stock Levels:'); [print(f'{p.title}: {p.total_stock} units') for p in products]; print(f'Total: {sum(p.total_stock for p in products)} units'); session.close()"
```

### View Product Details

```bash
python3 -c "from src.app_01.db import Market, db_manager; from src.app_01.models.products import Product; session = db_manager.get_session_factory(Market.KG)(); product = session.query(Product).filter(Product.slug == 'classic-white-tshirt-test').first(); print(f'\n{product.title}'); print(f'Price: {product.price_range}'); print(f'Stock: {product.total_stock}'); print(f'SKUs: {len(product.skus)}'); [print(f'  - {sku.size}/{sku.color}: {sku.stock} units') for sku in product.skus]; session.close()"
```

---

## ✅ Test Checklist

- [x] 5 products created
- [x] 22 SKUs created
- [x] 10 product images added
- [x] All products have stock
- [x] Price ranges set correctly
- [x] Featured products marked
- [x] Multiple sizes and colors available
- [x] Product attributes configured
- [ ] Test in admin panel
- [ ] Test API endpoints
- [ ] Test on frontend
- [ ] Test cart functionality
- [ ] Test order placement

---

## 🎨 Image Sources

All product images are from Unsplash (free high-quality images):

- Professional product photography
- High resolution
- Commercial use allowed
- No attribution required

---

## 🚀 Next Steps

1. **Test Products in Admin Panel**:

   - Visit: http://localhost:8001/admin/product/list
   - Try editing a product
   - Add more SKUs or images
   - Toggle featured status

2. **Test Product API**:

   ```bash
   # Get all products
   curl http://localhost:8000/api/v1/products | jq

   # Get specific product
   curl http://localhost:8000/api/v1/products/1 | jq

   # Search products
   curl "http://localhost:8000/api/v1/products/search?q=shirt" | jq
   ```

3. **Test Cart Functionality**:

   - Add products to cart via API
   - Check cart totals
   - Test checkout flow

4. **Frontend Integration**:
   - Display products in product grid
   - Show product details page
   - Implement cart functionality
   - Test responsive images

---

## 💡 Tips

- **SKU Code Format**: `ARTICLE-SIZE-COLOR`
- **Price Format**: Kyrgyzstan Som (сом)
- **Stock Management**: Automatically tracked in SKUs
- **Images**: Use CDN or cloud storage for production
- **Featured Products**: Show on homepage/main catalog

---

**Status**: ✅ Ready for testing!  
**Created**: October 12, 2025
