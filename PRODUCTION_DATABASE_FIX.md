# 🔴 CRITICAL: Production Database Migration Fix

## Issue Detected

Your production API is returning:

```
500 Internal Server Error
column users.market does not exist
```

This means your **production PostgreSQL database schema is outdated** and missing the new multi-market columns.

---

## 🎯 Quick Fix (3 Steps)

### Step 1: Connect to Railway Dashboard

1. Go to [railway.app](https://railway.app)
2. Navigate to your Marque project
3. Click on your database service

### Step 2: Run Migrations Manually

**Option A: Using Railway CLI (Recommended)**

```bash
# Install Railway CLI if you haven't
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migrations (connect to project environment)
railway run alembic upgrade head
```

**Option B: Using Railway Dashboard Shell**

1. In Railway dashboard, go to your web service
2. Click on "Deploy Logs" tab
3. Click "Create a deployment" → "Shell"
4. Run:

```bash
alembic upgrade head
```

### Step 3: Restart Your Service

1. In Railway dashboard, go to your service
2. Click "Deploy" → "Redeploy"
3. Wait for deployment to complete
4. Test the endpoint again

---

## 🔧 Automated Fix (Recommended for Future)

### Update Deployment to Auto-Migrate

#### Option 1: Update Procfile (Recommended)

Replace your current `Procfile` with:

```
release: alembic upgrade head
web: uvicorn src.app_01.main:app --host 0.0.0.0 --port $PORT
```

This will run migrations automatically before each deployment.

#### Option 2: Create a Startup Script

**Create `start_production.sh`:**

```bash
#!/bin/bash
echo "🔄 Running database migrations..."
alembic upgrade head

echo "🚀 Starting production server..."
uvicorn src.app_01.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

**Make it executable:**

```bash
chmod +x start_production.sh
```

**Update Procfile:**

```
web: ./start_production.sh
```

---

## 📋 Available Migrations

Your project has these migrations that need to be applied:

1. ✅ `71d0a21d5609` - Initial migration for multi-market architecture
2. ✅ `1d198e139e13` - Align models with frontend requirements
3. ✅ `0ca8b2ef41f8` - Add original_price to SKU
4. ✅ `6994966bbf08` - Add banners table for main page
5. ✅ `7371bc5cd7ba` - Add cart and cart_item models
6. ✅ `88ebdddde521` - Add wishlist models

---

## 🔍 Verify Migrations Status

**Check current database version:**

```bash
railway run alembic current
```

**Check pending migrations:**

```bash
railway run alembic history
```

**Check what changes will be applied:**

```bash
railway run alembic upgrade head --sql
```

---

## 🌍 Multi-Market Database Notes

Your production should have **TWO separate databases**:

### Database 1: KG Market

- Environment variable: `DATABASE_URL_MARQUE_KG`
- For Kyrgyzstan users (+996 phone numbers)

### Database 2: US Market

- Environment variable: `DATABASE_URL_MARQUE_US`
- For US users (+1 phone numbers)

**Current Issue:** It seems you're using a single database or the US database doesn't have the updated schema.

### Run Migrations for BOTH Markets

```bash
# Migrate KG database
ALEMBIC_TARGET_DB=KG railway run alembic upgrade head

# Migrate US database
ALEMBIC_TARGET_DB=US railway run alembic upgrade head
```

---

## 🚨 If Migrations Fail

### Error: "Multiple heads detected"

```bash
# Check migration tree
alembic heads

# Merge heads if needed
alembic merge -m "merge heads" head1_rev head2_rev

# Then upgrade
alembic upgrade head
```

### Error: "Can't locate revision"

```bash
# Stamp current version (use carefully!)
alembic stamp head
```

### Error: "Target database is not up to date"

```bash
# Downgrade one version
alembic downgrade -1

# Then upgrade again
alembic upgrade head
```

### Error: "Permission denied" or "Role doesn't exist"

- Check that Railway database environment variables are correct
- Verify database credentials in Railway dashboard
- Ensure `DATABASE_URL_MARQUE_KG` and `DATABASE_URL_MARQUE_US` are set

---

## ✅ Verification Steps

After running migrations:

### 1. Check Database Schema

```bash
# Connect to Railway database
railway run psql $DATABASE_URL_MARQUE_US

# Check users table
\d users

# Verify market column exists
SELECT column_name, data_type FROM information_schema.columns
WHERE table_name = 'users';
```

You should see columns:

- `id`
- `phone_number`
- `full_name`
- `market` ← THIS MUST EXIST
- `language`
- `country`
- `is_active`
- `is_verified`
- `created_at`
- `updated_at`

### 2. Test the Endpoint

```bash
curl -X POST "https://your-app.up.railway.app/api/v1/auth/send-verification" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+13128059851"}'
```

Expected response:

```json
{
  "success": true,
  "message": "Verification code sent successfully",
  "phone_number": "+1 (312) 805-9851",
  "market": "us",
  "language": "en",
  "expires_in_minutes": 15
}
```

### 3. Check Logs

```bash
# View Railway logs
railway logs

# Should see:
# ✅ "Running database migrations..."
# ✅ "Alembic migrations completed"
# ✅ "Starting production server..."
```

---

## 📝 Environment Variables Checklist

Make sure these are set in Railway:

### Required for Migrations:

```bash
DATABASE_URL_MARQUE_KG=postgresql://user:pass@host:port/marque_kg
DATABASE_URL_MARQUE_US=postgresql://user:pass@host:port/marque_us
```

### Required for App:

```bash
SECRET_KEY=your-secret-key-here
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_VERIFY_SERVICE_SID=your_verify_service_sid
ENVIRONMENT=production
```

---

## 🔄 Deployment Workflow (Post-Fix)

After implementing the automated migrations:

1. **Push code to GitHub**

   ```bash
   git add .
   git commit -m "feat: add auto-migration on deployment"
   git push origin main
   ```

2. **Railway auto-deploys**

   - Runs `release: alembic upgrade head`
   - Then starts `web: uvicorn ...`

3. **Migrations run automatically** ✅
   - No manual intervention needed
   - Safe for future schema changes

---

## 🆘 Emergency Rollback

If something goes wrong:

```bash
# Rollback one migration
railway run alembic downgrade -1

# Rollback to specific version
railway run alembic downgrade 71d0a21d5609

# Rollback everything (DANGEROUS!)
railway run alembic downgrade base
```

---

## 📞 Next Steps After Fix

1. ✅ Run migrations on Railway
2. ✅ Update Procfile for auto-migration
3. ✅ Test both `/send-verification` and `/verify-code` endpoints
4. ✅ Test with both +996 (KG) and +1 (US) phone numbers
5. ✅ Monitor error logs for any remaining issues

---

## 💡 Prevention for Future

**Always include in deployment checklist:**

- [ ] Run migrations before deploying new models
- [ ] Test migrations on staging database first
- [ ] Keep migrations in version control
- [ ] Document schema changes in migration messages
- [ ] Use Railway's release phase for automatic migrations

---

## 🎉 Success Criteria

You'll know it's fixed when:

1. ✅ No more "column users.market does not exist" errors
2. ✅ SMS sends successfully to US numbers
3. ✅ SMS sends successfully to KG numbers
4. ✅ Users can verify codes and get JWT tokens
5. ✅ User profiles return market-specific data

---

**Need help? Check the logs and share any error messages!**
