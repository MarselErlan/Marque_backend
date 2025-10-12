# 🎯 FIX: Update Backend Database URL

## ✅ **Problem Found!**

Your backend is connected to the **WRONG database**!

### Current Situation:

**❌ Backend is using**: (EMPTY database)

```
postgresql://postgres:HnxnpmuFbMiTFmOFJQkfhTDjaublaith@interchange.proxy.rlwy.net:54878/railway
```

- 0 products
- 0 categories
- 0 brands
- **This is why catalog shows empty!**

**✅ Your data is in**: (KG database with all products)

```
postgresql://postgres:YgyDmMbYyzPKvSsNyDRShLJqehXtTdJx@metro.proxy.rlwy.net:45504/railway
```

- 6 products (including your 5 new test products!)
- 2 categories (both active)
- 2 subcategories (both active)
- 5 brands
- 29 SKUs
- 12 product images

---

## 🛠️ **SOLUTION: Update Backend Database URL**

### **Step 1: Go to Railway Dashboard**

1. Visit: https://railway.app
2. Find and click your **backend service** (should be named something like "marquebackend-production" or "marque-backend")
3. Click the **"Variables"** tab

### **Step 2: Update DATABASE_URL**

Find the variable named `DATABASE_URL` (or similar like `DATABASE_URL_KG`)

**Change it FROM:**

```
postgresql://postgres:HnxnpmuFbMiTFmOFJQkfhTDjaublaith@interchange.proxy.rlwy.net:54878/railway
```

**Change it TO:**

```
postgresql://postgres:YgyDmMbYyzPKvSsNyDRShLJqehXtTdJx@metro.proxy.rlwy.net:45504/railway
```

### **Step 3: Save & Wait**

1. Click **"Save"** or **"Update Variables"**
2. Railway will automatically restart your backend
3. **Wait 30-60 seconds** for the restart to complete

---

## 🧪 **Verify It's Working**

### Test the API:

```bash
curl "https://marquebackend-production.up.railway.app/api/v1/categories"
```

**Should return:**

```json
{
  "categories": [
    {
      "id": 11,
      "name": "Мужчинам",
      "slug": "men",
      "product_count": 6,
      "is_active": true
    }
  ]
}
```

### Test the Frontend:

1. Go to: https://marque.website
2. Click **"Каталог"** button
3. **You should see**: "Мужчинам" category
4. Click it and you'll see "Футболки" subcategory
5. Click that and you'll see **all 5 new products**! 🎉

---

## 📊 **Products in KG Database**

Your database has these products ready to display:

| ID  | Product                   | Brand      | Category        | Subcategory            | Status    |
| --- | ------------------------- | ---------- | --------------- | ---------------------- | --------- |
| 8   | Футболка из хлопка (Test) | Test Brand | Мужчинам (Test) | Футболки и поло (Test) | ✅ Active |
| 10  | Classic White T-Shirt     | MARQUE     | Мужчинам        | Футболки               | ✅ Active |
| 11  | Blue Denim Jeans          | MARQUE     | Мужчинам        | Футболки               | ✅ Active |
| 12  | Black Hoodie Premium      | MARQUE     | Мужчинам        | Футболки               | ✅ Active |
| 13  | Casual Shirt Button-Up    | MARQUE     | Мужчинам        | Футболки               | ✅ Active |
| 14  | Sport Track Pants         | MARQUE     | Мужчинам        | Футболки               | ✅ Active |

---

## 🎯 **What This Fixes**

After updating the DATABASE_URL:

- ✅ Categories endpoint will work
- ✅ Catalog sidebar will show categories
- ✅ Products will be visible
- ✅ No more 500 errors
- ✅ No more CORS errors
- ✅ Admin panel will show correct data

---

## 🔍 **Why This Happened**

You have a **multi-market system** with separate databases:

- **KG Market** (Kyrgyzstan) → metro.proxy.rlwy.net
- **US Market** (or empty/test) → interchange.proxy.rlwy.net

You added products to the KG database, but your backend was pointing to the empty one!

---

## ✅ **After This Fix**

Your production site will show:

- Main page with products
- Working catalog with categories
- All 5 new test products visible
- Proper product details
- Working images and SKUs

---

**Status**: ⚠️ **WAITING FOR USER ACTION**  
**Action Required**: Update DATABASE_URL in Railway backend variables

Once done, your catalog will work perfectly! 🚀
