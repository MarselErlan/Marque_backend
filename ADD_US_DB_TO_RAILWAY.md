# 🚂 Add US Database to Railway

## ✅ Local Setup Complete!

Your local `.env` is now configured with TWO separate Railway databases:

- **KG Market**: `metro.proxy.rlwy.net:45504`
- **US Market**: `interchange.proxy.rlwy.net:54878`

---

## 🚀 Now Add to Railway (2 minutes)

### Step 1: Go to Railway Dashboard

1. Open: **https://railway.app/dashboard**
2. Click your **Marque** project
3. Click your **app service** (the FastAPI app, NOT PostgreSQL)

### Step 2: Add the US Database Variable

1. Click on **"Variables"** tab
2. Click **"+ New Variable"**
3. Add this:

```
Variable Name:  DATABASE_URL_MARQUE_US
Variable Value: postgresql://postgres:HnxnpmuFbMiTFmOFJQkfhTDjaublaith@interchange.proxy.rlwy.net:54878/railway
```

4. Click **"Add"** or **"Save"**

### Step 3: Wait for Auto-Deploy

Railway will automatically redeploy your app (takes 2-3 minutes).

You'll see:

- "Building..." → "Deploying..." → "Active"

---

## 🧪 Test It!

### Test 1: Create a New US User

```bash
python3 test_auth_flow_complete.py
```

Use phone: `+13128059851` (or any +1 number)

### Test 2: Check US Database

```bash
python3 check_railway_user_19.py
```

This will check the **KG database** (metro.proxy.rlwy.net).

To check the **US database**, create this quick script:

**check_us_railway.py**:

```python
import psycopg2
from psycopg2.extras import RealDictCursor

US_DB = "postgresql://postgres:HnxnpmuFbMiTFmOFJQkfhTDjaublaith@interchange.proxy.rlwy.net:54878/railway"

print("🔍 Checking US Railway Database")
print("=" * 80)

conn = psycopg2.connect(US_DB)
cursor = conn.cursor(cursor_factory=RealDictCursor)

cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 10")
users = cursor.fetchall()

print(f"\n📊 Total users: {len(users)}\n")

for user in users:
    print(f"User ID {user['id']}: {user['phone_number']}")
    print(f"  Active: {user['is_active']}, Verified: {user['is_verified']}")
    print()

conn.close()
```

Run it:

```bash
python3 check_us_railway.py
```

---

## 🎯 Expected Result

After adding the variable to Railway:

**US Database (interchange.proxy.rlwy.net)**:

- User 19: +13128059851 ✅
- All future US users (+1 numbers)

**KG Database (metro.proxy.rlwy.net)**:

- User 3: +996700123456 ✅
- User 4: +996700234567 ✅
- All future KG users (+996 numbers)

---

## ⚠️ Important Notes

1. **Two Separate Databases**: You now have TWO Railway PostgreSQL services:

   - One for KG market
   - One for US market

2. **Market Detection**: Your app automatically detects market by phone number:

   - `+996...` → KG database
   - `+1...` → US database

3. **Railway Variables Needed**:
   ```
   DATABASE_URL_MARQUE_KG = metro.proxy.rlwy.net:45504
   DATABASE_URL_MARQUE_US = interchange.proxy.rlwy.net:54878
   ```

---

**🎯 ACTION**: Go to Railway dashboard and add `DATABASE_URL_MARQUE_US` now!
