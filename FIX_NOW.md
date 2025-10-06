# 🚨 IMMEDIATE FIX - Railway Production Database

## Your Current Error

```
ERROR: column users.market does not exist
LINE 1: ...users.last_login, users.mark...
```

## Quick Fix (5 minutes)

### Step 1: Install Railway CLI (if not installed)

```bash
npm i -g @railway/cli
```

### Step 2: Login and Link

```bash
railway login
railway link
```

Select your Marque project when prompted.

### Step 3: Run Migrations

```bash
# Option A: Use the script (recommended)
./railway_migrate.sh

# Option B: Run directly
railway run alembic upgrade head
```

### Step 4: Verify

Wait 30 seconds, then test:

```bash
curl -X POST "https://marquebackend-production.up.railway.app/api/v1/auth/send-verification" \
  -H "Content-Type: application/json" \
  -d '{"phone": "+13128059851"}'
```

You should get:

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

---

## Alternative: Push Code (Automatic Fix)

Since you've updated the Procfile:

```bash
git add .
git commit -m "fix: add automatic database migrations"
git push origin main
```

Railway will auto-migrate on next deployment!

---

## Success Indicators

✅ No more "column users.market does not exist" errors
✅ API returns 200 instead of 500
✅ Response includes `"market": "us"` or `"market": "kg"`
✅ Railway logs show "Running database migrations..."

---

## If Something Goes Wrong

Check Railway logs:

```bash
railway logs
```

Or contact me with the error message!
