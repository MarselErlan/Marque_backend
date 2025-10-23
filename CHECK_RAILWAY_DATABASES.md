# 🔍 Check Your Railway Databases

## Your Current Setup

Your application uses **TWO separate database connections**:

```python
# KG Market Database
DATABASE_URL_MARQUE_KG = "postgresql://..."  # Users 3, 4 (KG numbers)

# US Market Database
DATABASE_URL_MARQUE_US = "postgresql://..."  # User 19 (US numbers) ← HERE!
```

---

## 🎯 How to Find User ID 19

### Step 1: Check Environment Variables in Railway

1. Go to https://railway.app/dashboard
2. Click your project: **marque_db_kg** or **marquebackend**
3. Click on your service (the main app)
4. Go to **Variables** tab
5. Look for these variables:
   - `DATABASE_URL_MARQUE_KG`
   - `DATABASE_URL_MARQUE_US`

You should see **TWO different URLs**!

---

### Step 2: Identify Which Database Has User 19

Both databases might be:

- ✅ **Option A:** Two separate Railway Postgres services
- ✅ **Option B:** Same Postgres service, different databases
- ✅ **Option C:** Same Postgres service, same database (all users together)

---

## 🔧 Quick Check: View US Database

Let me query the US database directly from Railway:

### Copy your `DATABASE_URL_MARQUE_US` value

1. Get the value from Railway Variables
2. Run this command locally:

```bash
export US_DB_URL="paste_your_DATABASE_URL_MARQUE_US_here"

python3 -c "
from sqlalchemy import create_engine, text
import os

engine = create_engine(os.getenv('US_DB_URL'))

with engine.connect() as conn:
    print('📊 Users in US DATABASE:')
    print('=' * 80)

    users = conn.execute(text('''
        SELECT id, phone_number, full_name, is_active, is_verified,
               last_login, created_at
        FROM users
        ORDER BY id DESC
        LIMIT 20
    ''')).fetchall()

    print(f'Total users: {len(users)}\\n')

    for user in users:
        print(f'User ID: {user[0]}')
        print(f'  Phone: {user[1]}')
        print(f'  Name: {user[2] or \"Not set\"}')
        print(f'  is_active: {user[3]}')
        print(f'  is_verified: {user[4]}')
        print(f'  last_login: {user[5]}')
        print(f'  created: {user[6]}')
        print()
"
```

---

## 📊 Expected Result

You should see:

```
📊 Users in US DATABASE:
================================================================================
Total users: 1

User ID: 19
  Phone: +13128059851
  Name: Not set
  is_active: True          ← After re-login!
  is_verified: True
  last_login: 2025-10-23 22:50:26
  created: 2025-10-23 22:41:21
```

---

## 🎯 Most Likely Scenario

Looking at your Railway screenshot, you have **ONE Postgres database** that contains:

- KG users (IDs 3, 4 with +996 numbers)
- US users (ID 19 with +1 numbers)

**They're in the SAME database!**

But your `DATABASE_URL_MARQUE_KG` and `DATABASE_URL_MARQUE_US` might be:

- Pointing to the same database ✅
- But your code separates them logically

Let me verify this:

```bash
# Check if both URLs point to same database
echo "KG URL: $DATABASE_URL_MARQUE_KG"
echo "US URL: $DATABASE_URL_MARQUE_US"
```

If they're the **same**, then User ID 19 **IS** in the database you're viewing!

---

## 🔍 Railway Dashboard - Find User 19

In the Railway Postgres panel you showed:

1. Click the **users** table
2. Scroll down or use **Query** tab
3. Run this SQL:

```sql
SELECT * FROM users WHERE id = 19;
```

Or see all users:

```sql
SELECT id, phone_number, is_active, is_verified, last_login
FROM users
ORDER BY id DESC;
```

You should see:

- User 3: +996700123456 (KG)
- User 4: +996700234567 (KG)
- **User 19: +13128059851 (US)** ← Should be here!

---

## ⚠️ If You Don't See User 19

Two possibilities:

### 1. Different Databases

`DATABASE_URL_MARQUE_US` points to a **different Railway Postgres service**

**Solution:** In Railway dashboard, check if you have **2 Postgres services**:

- One for KG
- One for US

### 2. Railway Shows Limited Data

The Railway UI might be paginating or filtering results

**Solution:** Use the **Query** tab in Railway to run:

```sql
SELECT COUNT(*) FROM users;  -- How many total?
SELECT * FROM users WHERE phone_number LIKE '+1%';  -- US users
```

---

## ✅ Verify Your Test Was Against Production

Your test output showed:

```
🌐 Testing API: https://marquebackend-production.up.railway.app/api/v1
✅ User ID: 19 created
✅ All tests passed
```

This **proves** User ID 19 exists in Railway production!

---

## 🎯 Action Plan

1. **Check Railway Variables**

   ```
   DATABASE_URL_MARQUE_KG = ?
   DATABASE_URL_MARQUE_US = ?
   ```

2. **Check if they're the same URL**

   - If YES: User 19 is in the same database (scroll down in Railway UI)
   - If NO: You have 2 databases (check the other one)

3. **Use Query Tab in Railway**
   ```sql
   SELECT * FROM users WHERE id = 19;
   ```

---

## 💡 Quick Test

From your terminal, check production:

```bash
curl -s "https://marquebackend-production.up.railway.app/api/v1/auth/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_FROM_TEST"
```

This will return User 19's data, proving it exists in production!

---

**Need help?** Share:

1. Your `DATABASE_URL_MARQUE_KG` value (from Railway Variables)
2. Your `DATABASE_URL_MARQUE_US` value (from Railway Variables)

And I'll tell you exactly where User 19 is! 🎯
