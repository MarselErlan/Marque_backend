# 🚂 Railway Variables - Simple Setup

## ✅ Current Configuration: Railway Database Only

Both KG and US markets now use the **same Railway database**.

---

## 📝 Required Railway Variables

Go to Railway Dashboard → Your Project → App Service → **Variables** tab

Add these variables:

### 1. Database (Both markets use same database)

```
DATABASE_URL_MARQUE_KG
Value: ${{Postgres.DATABASE_URL}}

DATABASE_URL_MARQUE_US
Value: ${{Postgres.DATABASE_URL}}
```

**Important:** Both should reference the **same** PostgreSQL service!

---

### 2. Twilio (SMS Verification)

```
TWILIO_ACCOUNT_SID
Value: <your_twilio_account_sid>

TWILIO_AUTH_TOKEN
Value: <your_twilio_auth_token>

TWILIO_VERIFY_SERVICE_SID
Value: <your_twilio_verify_service_sid>
```

---

### 3. Security

```
SECRET_KEY
Value: your-super-secure-production-secret-key-change-this

JWT_ALGORITHM
Value: HS256

ACCESS_TOKEN_EXPIRE_MINUTES
Value: 30
```

---

### 4. Environment

```
ENVIRONMENT
Value: production

PORT
Value: 8000
```

---

## ✅ Verification Checklist

After adding variables in Railway:

- [ ] `DATABASE_URL_MARQUE_KG` is set
- [ ] `DATABASE_URL_MARQUE_US` is set (same value as KG)
- [ ] Both point to `${{Postgres.DATABASE_URL}}`
- [ ] Twilio variables are set
- [ ] App redeployed automatically

---

## 🧪 Test After Setup

Once Railway finishes deploying, test:

```bash
# Test authentication flow
python3 test_auth_flow_complete.py

# Check if user appears in database
export DATABASE_URL="$DATABASE_URL_MARQUE_KG"
python3 check_railway_user_19.py
```

You should now see **all users** (KG and US) in the **same Railway database**! 🎉

---

## 📊 Expected Database Contents

After testing with both markets:

```
Railway PostgreSQL Database:
├── User 3: +996700123456 (KG) ✅ Already exists
├── User 4: +996700234567 (KG) ✅ Already exists
└── User 19+: +13128059851 (US) ✅ Will appear here now!
```

All users in **ONE database** = Simple and easy! ✅

---

## 🎯 Summary

**Before:**

- ❌ Local databases (complicated)
- ❌ Multiple database URLs (confusing)
- ❌ User 19 missing (not in Railway)

**After:**

- ✅ Railway database only
- ✅ Both markets use same database
- ✅ All users visible in Railway dashboard

Simple and production-ready! 🚀
