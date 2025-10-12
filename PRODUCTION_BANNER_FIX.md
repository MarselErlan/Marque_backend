# 🔧 Production Banner Error Fix

## Problem

Getting "Internal Server Error" (500) when accessing banner admin panel in production:

```
URL: marquebackend-production.up.railway.app/admin/banner/list
Error: 500 Internal Server Error
```

## Root Cause

The production database still has the **old enum values** (`SALE`, `MODEL`) while the code expects **new values** (`hero`, `promo`, `category`).

## Solution

### Option 1: Fix via Railway PostgreSQL Console (Recommended)

1. **Access Railway Dashboard**

   - Go to: https://railway.app
   - Select your project: `marquebackend-production`
   - Click on your PostgreSQL database service

2. **Open PostgreSQL Console**

   - Click "Data" tab or "Connect"
   - Open the Query tab or connect via psql

3. **Run the Fix Script**

   Copy and paste this SQL:

   ```sql
   -- Step 1: Check current enum (should show SALE, MODEL)
   SELECT enum_range(NULL::bannertype);

   -- Step 2: Convert to VARCHAR temporarily
   ALTER TABLE banners ALTER COLUMN banner_type TYPE VARCHAR(50);

   -- Step 3: Drop old enum
   DROP TYPE IF EXISTS bannertype CASCADE;

   -- Step 4: Create new enum with correct values
   CREATE TYPE bannertype AS ENUM ('hero', 'promo', 'category');

   -- Step 5: Convert back to enum
   ALTER TABLE banners ALTER COLUMN banner_type TYPE bannertype
   USING banner_type::bannertype;

   -- Step 6: Verify (should show hero, promo, category)
   SELECT enum_range(NULL::bannertype);
   ```

4. **Verify**
   ```sql
   SELECT COUNT(*) FROM banners;
   SELECT id, title, banner_type, is_active FROM banners LIMIT 10;
   ```

### Option 2: Create Migration Script

If you prefer to use Alembic migrations:

1. **Create new migration**

   ```bash
   cd /Users/macbookpro/M4_Projects/Prodaction/Marque
   alembic revision -m "fix_banner_enum_values"
   ```

2. **Edit the migration file** (in `alembic/versions/`)

   ```python
   def upgrade() -> None:
       # Fix banner enum
       op.execute("ALTER TABLE banners ALTER COLUMN banner_type TYPE VARCHAR(50)")
       op.execute("DROP TYPE IF EXISTS bannertype CASCADE")
       op.execute("CREATE TYPE bannertype AS ENUM ('hero', 'promo', 'category')")
       op.execute("ALTER TABLE banners ALTER COLUMN banner_type TYPE bannertype USING banner_type::bannertype")

   def downgrade() -> None:
       # Revert if needed
       op.execute("ALTER TABLE banners ALTER COLUMN banner_type TYPE VARCHAR(50)")
       op.execute("DROP TYPE IF EXISTS bannertype CASCADE")
       op.execute("CREATE TYPE bannertype AS ENUM ('SALE', 'MODEL')")
       op.execute("ALTER TABLE banners ALTER COLUMN banner_type TYPE bannertype USING banner_type::bannertype")
   ```

3. **Run migration on Railway**
   ```bash
   # In Railway environment or local with production DB URL
   alembic upgrade head
   ```

### Option 3: Python Script (If you have DB access)

Run this locally with production database URL:

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque

# Set production database URL
export DATABASE_URL="your_production_postgresql_url"

# Run fix script
python3 fix_banner_enum.py
```

## After the Fix

1. **Restart your Railway service**

   - Go to Railway dashboard
   - Click "Restart" on your backend service

2. **Test the admin panel**

   - Visit: `https://marquebackend-production.up.railway.app/admin`
   - Navigate to "Баннеры"
   - Should load without errors

3. **Add sample banners** (if needed)
   ```bash
   # Using production database
   python3 add_sample_banners.py
   ```

## Verification Checklist

After applying the fix:

- [ ] Enum values changed from `{SALE,MODEL}` to `{hero,promo,category}`
- [ ] Admin panel `/admin/banner/list` loads without 500 error
- [ ] Can create new banners
- [ ] Can edit existing banners
- [ ] API endpoint works: `/api/v1/banners/`

## Quick Test Commands

### Test API endpoint:

```bash
# Should return banners (or empty array)
curl https://marquebackend-production.up.railway.app/api/v1/banners/
```

### Test admin panel:

```
https://marquebackend-production.up.railway.app/admin/banner/list
```

## Common Issues

### Issue: "cannot cast type varchar to bannertype"

**Solution**: Make sure to drop the old enum type first before creating the new one

### Issue: "type bannertype already exists"

**Solution**: Drop it first with `DROP TYPE IF EXISTS bannertype CASCADE`

### Issue: Still getting 500 error

**Possible causes**:

1. Railway service not restarted after DB change
2. Multiple database instances (check you're fixing the right one)
3. Check Railway logs for actual error

**To check logs**:

- Railway Dashboard → Your Service → Deployments → View Logs

## Need More Help?

If you continue to have issues:

1. **Check Railway logs**:

   ```
   Railway Dashboard → Backend Service → Logs
   ```

2. **Check database connection**:

   ```sql
   SELECT version();
   SELECT current_database();
   ```

3. **Verify table exists**:

   ```sql
   \dt banners
   ```

4. **Check enum type**:
   ```sql
   SELECT typname, typnamespace, typowner, typlen
   FROM pg_type
   WHERE typname = 'bannertype';
   ```

---

**Fix Script Available**: `fix_production_banner_enum.sql`

**Status**: Ready to apply to production database
