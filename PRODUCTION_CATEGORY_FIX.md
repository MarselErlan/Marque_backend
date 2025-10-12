# 🚨 PRODUCTION CATALOG FIX

**Issue**: Catalog showing empty when clicking "Каталог" button  
**Error**: `500 Internal Server Error` on `/api/v1/categories`  
**Cause**: Categories not activated in production database

---

## 🎯 The Problem

You activated categories in your **local database**, but the **production Railway database** still has inactive categories!

### Errors You're Seeing:

```
❌ CORS policy: No 'Access-Control-Allow-Origin' header
❌ Failed to load resource: net::ERR_FAILED
❌ GET https://marquebackend-production.up.railway.app/api/v1/categories 500 (Internal Server Error)
❌ Failed to load categories: ApiError: Network error
```

### What's Working:

```
✅ Banners load fine (4 banners loaded)
✅ Individual product pages work
✅ Admin panel shows products
```

---

## ✅ SOLUTION: Activate Categories in Production

### Option 1: Using Python Script (Recommended)

1. **Get your Railway Production Database URL**:

   ```
   Go to: Railway Dashboard → marquebackend-production → Variables
   Copy: DATABASE_URL (starts with postgresql://...)
   ```

2. **Set the environment variable**:

   ```bash
   export RAILWAY_PROD_DATABASE_URL="postgresql://postgres:..."
   ```

3. **Run the activation script**:
   ```bash
   cd /Users/macbookpro/M4_Projects/Prodaction/Marque
   python3 activate_production_categories.py
   ```

### Option 2: Direct SQL in Railway Console

1. Go to Railway Dashboard
2. Open your PostgreSQL database
3. Click "Query" tab
4. Run this SQL:

```sql
-- Activate all categories that have products
UPDATE categories
SET is_active = TRUE
WHERE id IN (
    SELECT DISTINCT category_id
    FROM products
    WHERE is_active = TRUE
)
AND (is_active IS NULL OR is_active = FALSE);

-- Activate all subcategories that have products
UPDATE subcategories
SET is_active = TRUE
WHERE id IN (
    SELECT DISTINCT subcategory_id
    FROM products
    WHERE is_active = TRUE
)
AND (is_active IS NULL OR is_active = FALSE);

-- Verify
SELECT c.id, c.name, c.slug, c.is_active,
       (SELECT COUNT(*) FROM products WHERE category_id = c.id AND is_active = TRUE) as product_count
FROM categories c
ORDER BY c.id;
```

---

## 🧪 Verification

After activation:

1. **Wait 30-60 seconds** for Railway backend to restart
2. **Refresh your frontend**: https://marque.website
3. **Click "Каталог"** button
4. **You should see**: "Мужчинам" category with products

### Test API Directly:

```bash
curl "https://marquebackend-production.up.railway.app/api/v1/categories"
```

**Expected Response**:

```json
{
  "categories": [
    {
      "id": 11,
      "name": "Мужчинам",
      "slug": "men",
      "product_count": 5,
      "is_active": true
    }
  ]
}
```

---

## 📊 What Gets Activated

### Categories:

- **ID 11**: "Мужчинам" (men) → 5 products
  - SKUs, images, all relationships ✅

### Subcategories:

- **ID 16**: "Футболки" (t-shirts) → 5 products
  - Classic White T-Shirt
  - Blue Denim Jeans
  - Black Hoodie Premium
  - Casual Shirt Button-Up
  - Sport Track Pants

---

## 🔍 Debugging

If it still doesn't work:

### 1. Check Backend Logs:

```
Railway Dashboard → marquebackend-production → Deployments → View Logs
```

Look for:

- ✅ Server started successfully
- ❌ Any Python errors or database connection issues

### 2. Check Database Connection:

```bash
curl "https://marquebackend-production.up.railway.app/health"
```

### 3. Check Categories Endpoint:

```bash
curl "https://marquebackend-production.up.railway.app/api/v1/categories"
```

---

## 🎯 Why This Happened

1. You added products to your **local** database
2. You activated categories in your **local** database
3. But **production** database on Railway is separate!
4. Production still has `is_active = NULL` for categories

---

## ✅ After This Fix

Once categories are activated in production:

- ✅ Catalog will show categories
- ✅ Clicking "Мужчинам" will show subcategories
- ✅ Clicking "Футболки" will show products
- ✅ All 5 test products will be visible
- ✅ CORS errors will stop (they're caused by 500 errors)

---

## 🚀 Deploy This Fix to Production

If you want to automate this in future deployments:

Add to your backend startup script:

```python
# In marque_api_production.py or migration script
@app.on_event("startup")
async def activate_categories():
    """Auto-activate categories on startup"""
    session = SessionLocal()
    try:
        session.execute("""
            UPDATE categories SET is_active = TRUE
            WHERE id IN (SELECT DISTINCT category_id FROM products WHERE is_active = TRUE)
            AND (is_active IS NULL OR is_active = FALSE)
        """)
        session.commit()
    finally:
        session.close()
```

---

**Status**: ⚠️ **WAITING FOR USER ACTION**  
**Next Step**: Run the activation script or SQL commands in production database
