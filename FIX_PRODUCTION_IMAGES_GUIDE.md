# 🔧 Fix Production Images on Railway

## 🚨 The Problem

Your production logs show **404 errors** for images:

```
❌ GET /banner/xxx.png - 404 Not Found
❌ GET /product/xxx.png - 404 Not Found
```

**Why?**

- Static files are mounted at `/uploads/`
- Database URLs are missing `/uploads/` prefix or have wrong folder names

## ✅ The Solution

Run `fix_railway_images.py` to update your production database.

---

## 📝 Step 1: Get Railway DATABASE_URL

### Option A: From Railway Dashboard (Easiest)

1. Go to https://railway.app/dashboard
2. Click your project: `marquebackend`
3. Click on the **PostgreSQL** service (not your app)
4. Go to **Variables** tab
5. Find and copy the **`DATABASE_URL`** value

It looks like:

```
postgresql://postgres:password@containers-us-west-xxx.railway.app:7432/railway
```

### Option B: From Railway CLI

```bash
# Login to Railway
railway login

# Link to your project
railway link

# Get DATABASE_URL
railway variables --json | grep DATABASE_URL
```

---

## 📝 Step 2: Run the Fix Script

### On macOS/Linux:

```bash
# Set the DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@containers-us-west-xxx.railway.app:7432/railway"

# Run the fix script
python3 fix_railway_images.py
```

### On Windows:

```cmd
REM Set the DATABASE_URL environment variable
set DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@containers-us-west-xxx.railway.app:7432/railway

REM Run the fix script
python fix_railway_images.py
```

---

## 🎯 What the Script Does

1. **Connects** to Railway production database
2. **Finds** all banners and products
3. **Fixes** image URLs:
   - `/banner/xxx.png` → `/uploads/banners/xxx.png` ✅
   - `/product/xxx.png` → `/uploads/products/xxx.png` ✅
   - Missing `/uploads/` → Adds it ✅
4. **Updates** database
5. **Shows** all fixed records

---

## 📊 Expected Output

```bash
================================================================================
🚀 FIXING PRODUCTION IMAGES ON RAILWAY
================================================================================
🚀 Connecting to Railway production database...
URL: postgresql://postgres:xxxxx...

🔧 Fixing PRODUCTION banner URLs...
   Found 5 banners
   ✅ Fixed: Новая коллекция
      Old: /b93dc4af6b33446ca2a5472bc63797bc73a9eae2.png
      New: /uploads/banners/b93dc4af6b33446ca2a5472bc63797bc73a9eae2.png
   ✅ Fixed: Мужская одежда
      Old: /uploads/banner/773916fe-8f84-41fb-a519-4685674ecb62.png
      New: /uploads/banners/773916fe-8f84-41fb-a519-4685674ecb62.png

✅ Fixed 4 banner URLs in production!

📋 All production banners:
   1. Новая коллекция
      /uploads/banners/b93dc4af6b33446ca2a5472bc63797bc73a9eae2.png
   ...

🔧 Fixing PRODUCTION product URLs...
   Found 1 products
   ✅ Fixed: test kg product 1
      Old: /uploads/product/aabba996-0a14-4fc3-babd-56c547f2a851.png
      New: /uploads/products/aabba996-0a14-4fc3-babd-56c547f2a851.png

✅ Fixed 1 product URLs in production!

================================================================================
✅ PRODUCTION DATABASE FIXED!
================================================================================

Your production site should now show images correctly! 🎉

Test it:
  https://marquebackend-production.up.railway.app/api/v1/banners/
  https://marquebackend-production.up.railway.app/api/v1/products/
```

---

## 🧪 Step 3: Test Your Production Site

### Test Banners API:

```bash
curl https://marquebackend-production.up.railway.app/api/v1/banners/
```

You should see correct image URLs like:

```json
{
  "banners": [
    {
      "id": 1,
      "title": "Новая коллекция",
      "image_url": "/uploads/banners/xxx.png"  ← ✅ Correct!
    }
  ]
}
```

### Test Products API:

```bash
curl "https://marquebackend-production.up.railway.app/api/v1/products?limit=5"
```

### Test in Browser:

1. Open your frontend
2. Check if banner images load
3. Check if product images load
4. No more 404 errors! ✅

---

## 🚨 Troubleshooting

### Error: "DATABASE_URL environment variable not set"

**Solution:**

```bash
# Make sure you export it in the same terminal where you run the script
export DATABASE_URL="postgresql://..."
python3 fix_railway_images.py
```

### Error: "Connection refused" or "could not connect"

**Possible causes:**

1. Wrong DATABASE_URL
2. Railway database is paused (free tier)
3. Network/firewall issues

**Solution:**

- Double-check the DATABASE_URL from Railway dashboard
- Make sure your Railway project is active (not paused)

### Error: "Authentication failed"

**Solution:**

- Your DATABASE_URL might be outdated
- Railway changes database credentials sometimes
- Get fresh DATABASE_URL from Railway dashboard

### Images still show 404 after fix

**Possible causes:**

1. **Image files don't exist** - Database has URLs but files aren't uploaded
2. **Railway static file mounting issue**

**Check:**

```bash
# Check if files exist on Railway
railway run ls -la static/uploads/banners/
railway run ls -la static/uploads/products/
```

**If files are missing:**
You need to upload the actual image files to Railway:

```bash
# Upload local images to Railway
scp -r static/uploads/* railway:/app/static/uploads/
```

Or use Railway's file upload feature.

---

## 📚 Summary

| What                        | Status                         |
| --------------------------- | ------------------------------ |
| Local KG database           | ✅ Fixed                       |
| Local US database           | ✅ No images yet (OK)          |
| Production Railway database | 🔧 Run `fix_railway_images.py` |
| Image files on Railway      | ❓ Check if they exist         |

---

## 🎯 Quick Commands

```bash
# 1. Get DATABASE_URL from Railway
railway variables --json | grep DATABASE_URL

# 2. Set it
export DATABASE_URL="your_url_here"

# 3. Fix production
python3 fix_railway_images.py

# 4. Test
curl https://marquebackend-production.up.railway.app/api/v1/banners/
```

---

**Created:** October 23, 2025  
**Script:** `fix_railway_images.py`  
**Purpose:** Fix image URLs in production Railway database
