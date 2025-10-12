# 🚀 Deploy Product Filters

## ✅ What's Ready

### Backend Updates (2 files)

- `src/app_01/schemas/product.py` - Added filter metadata fields
- `src/app_01/routers/category_router.py` - Returns available sizes, colors, brands, price range

### Frontend

- **No changes needed** - Already has complete filter UI!

---

## 📦 Deploy Backend to Railway

### Step 1: Commit Changes

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque

git add src/app_01/schemas/product.py
git add src/app_01/routers/category_router.py
git commit -m "Add product filter metadata to API"
```

### Step 2: Push to Railway

```bash
git push origin main
```

Railway will automatically deploy (takes ~2-3 minutes).

---

## 🧪 Test After Deployment

### 1. Test API Filter Data

```bash
curl "https://marquebackend-production.up.railway.app/api/v1/subcategories/t-shirts/products" | json_pp
```

**Should see**:

```json
{
  "products": [...],
  "filters": {
    "available_sizes": ["S", "M", "L", "XL", "30", "32", "34", "36"],
    "available_colors": ["Black", "Blue", "Gray", "Navy", "White"],
    "available_brands": [{"slug": "marque", "name": "MARQUE"}],
    "price_range": {"min": 990.0, "max": 3490.0}
  }
}
```

### 2. Test Frontend Filters

1. Go to: **https://marque.website**
2. Click **"Каталог"**
3. Select **"Мужчинам"** → **"Футболки"**
4. Should see filter sidebar with:
   - ✅ Size buttons: S, M, L, XL, 30, 32, 34, 36
   - ✅ Color checkboxes: Black, Blue, Gray, Navy, White
   - ✅ Brand checkboxes: MARQUE
   - ✅ Price range: 990 - 3490 сом

### 3. Test Filtering

1. Click **"M"** size button
2. Products should filter instantly
3. URL should update: `?sizes=M`
4. Click **"Black"** color
5. Further filtering
6. URL: `?sizes=M&colors=Black`

### 4. Test Sorting

1. Click **"Сортировать"** dropdown
2. Select **"Сначала дешёвые"**
3. Products re-order by price (lowest first)

### 5. Test Clear Filters

1. Click **"Сбросить фильтры"** button
2. All filters should clear
3. All products show again

---

## 📊 Expected Results

### Product Listing Page (/subcategory/men/t-shirts)

**Current Test Data**:

- **Total Products**: 5
- **Available Sizes**: S, M, L, XL, 30, 32, 34, 36
- **Available Colors**: Black, Blue, Gray, Navy, White
- **Price Range**: 990 - 3490 сом
- **Brands**: MARQUE

**Products**:

1. Classic White T-Shirt - 990 сом
2. Blue Denim Jeans - 2990 сом (was 3990, -25%)
3. Black Hoodie Premium - 3490 сом
4. Casual Shirt Button-Up - 1990 сом
5. Sport Track Pants - 2490 сом

---

## ✅ Checklist

After deployment, verify:

- [ ] Backend API returns filter metadata
- [ ] Frontend filter sidebar shows sizes
- [ ] Frontend filter sidebar shows colors
- [ ] Frontend filter sidebar shows price range
- [ ] Clicking size button filters products
- [ ] Clicking color checkbox filters products
- [ ] Price range inputs work
- [ ] Sorting dropdown works
- [ ] Clear filters button works
- [ ] URL updates with filter params
- [ ] Pagination works with filters
- [ ] No console errors

---

## 🎯 Complete User Flow

1. ✅ **Homepage** → Click "Каталог"
2. ✅ **Catalog opens** → Shows "Мужчинам"
3. ✅ **Click "Мужчинам"** → Shows "Футболки" subcategory
4. ✅ **Click "Футболки"** → Opens product listing page
5. ✅ **Filter sidebar loads** with real data from API
6. ✅ **User selects filters** → Products update instantly
7. ✅ **User sorts** → Products re-order
8. ✅ **User clears filters** → Back to all products

---

## 🔧 Troubleshooting

### If filters don't show:

1. Check backend API response includes `filters` field
2. Check browser console for errors
3. Verify Railway deployment completed successfully

### If filtering doesn't work:

1. Check URL updates with filter params
2. Check API accepts filter params (sizes, colors, etc.)
3. Check browser console for API errors

### If no products after filtering:

1. Normal! Means no products match those filters
2. Try different filter combination
3. Click "Сбросить фильтры" to reset

---

## 📝 Deploy Command (Copy & Paste)

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque && \
git add src/app_01/schemas/product.py src/app_01/routers/category_router.py && \
git commit -m "Add product filter metadata to API" && \
git push origin main
```

---

**Status**: ✅ **READY TO DEPLOY**  
**Risk**: ✅ **Low (only adds fields, doesn't break existing)**  
**Frontend Changes**: ✅ **None needed (already implemented)**

Deploy with confidence! 🎯
