# Testing Guide - Market-Based Order System

## ✅ System Status

**User Configuration:**

- User ID: 19
- Phone: +13128059851
- Market: us (stored in database)
- Database: US

---

## 🧪 Test 1: Verify Backend is Running

Open a **NEW terminal** and run:

```bash
curl http://localhost:8000/health
```

**Expected Output:**

```json
{ "status": "ok" }
```

**If backend is NOT running:**

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
uvicorn src.app_01.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 Test 2: Verify User Data

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 << 'EOF'
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.users.user import User

us_db = db_manager.get_session_factory(Market.US)()
user = us_db.query(User).filter(User.id == 19).first()

print(f"\nUser ID: {user.id}")
print(f"Phone: {user.phone_number}")
print(f"Market: {user.market}")
print(f"Active: {user.is_active}")
us_db.close()
EOF
```

**Expected Output:**

```
User ID: 19
Phone: +13128059851
Market: us
Active: True
```

---

## 🧪 Test 3: Frontend Order Test (MAIN TEST)

### Step 1: Open Frontend

1. Open browser: `http://marque.website` (or your frontend URL)
2. Open Developer Tools (F12)
3. Go to **Console** tab

### Step 2: Verify You're Logged In

In Console, run:

```javascript
const userData = JSON.parse(localStorage.getItem("userData"));
console.log("User ID:", userData?.id);
console.log("Phone:", userData?.phone);
console.log("Market:", userData?.market);
```

**Expected:**

```
User ID: 19
Phone: +13128059851
Market: us
```

### Step 3: Place an Order

1. Add items to cart
2. Go to checkout/cart page
3. Fill in order details:
   - Name: Test Customer
   - Phone: +13128059851
   - Address: 123 Main St
   - Payment: Card or Cash
4. Click **"Place Order"**
5. Watch the Console for API calls

### Step 4: Check Console for Success

Look for:

```
✅ POST /api/v1/orders/create → 201 Created
Order response: { order_number: "MQ-...", ... }
```

---

## 🧪 Test 4: Verify Order in Database

After placing order, run:

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 << 'EOF'
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.orders.order import Order

print("\n🔍 Checking US Database for User 19 orders:")
us_db = db_manager.get_session_factory(Market.US)()
orders = us_db.query(Order).filter(Order.user_id == 19).order_by(Order.created_at.desc()).limit(5).all()

print(f"Found {len(orders)} orders for User 19 in US database\n")
for order in orders:
    print(f"  📦 {order.order_number}")
    print(f"     Customer: {order.customer_name}")
    print(f"     Total: ${order.total_amount}")
    print(f"     Status: {order.status}")
    print(f"     Date: {order.order_date}")
    print()

us_db.close()
EOF
```

**Expected:**

```
Found 1 orders for User 19 in US database

  📦 MQ-20251102-XXXXX
     Customer: Test Customer
     Total: $XX.XX
     Status: pending
     Date: 2025-11-02 ...
```

---

## 🧪 Test 5: Verify Market Logic in Backend Logs

Check backend logs for market assignment:

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
tail -50 backend.log | grep -i "market"
```

**Look for:**

```
✅ User market set to: us (Phone: +13128059851)
```

---

## 🔍 Troubleshooting

### Issue 1: Backend Not Responding

**Check if running:**

```bash
ps aux | grep uvicorn
```

**Restart if needed:**

```bash
pkill -f uvicorn
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
uvicorn src.app_01.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue 2: Order Not Saving

**Check backend terminal** for errors like:

- `User not found` → User market mismatch
- `Invalid token` → Need to login again
- `Database connection error` → Check DATABASE_URL_MARQUE_US

**Solution:**

1. Logout from frontend
2. Clear localStorage: `localStorage.clear()`
3. Login again
4. Try order again

### Issue 3: Still Seeing Old User ID

**Clear browser cache:**

```javascript
localStorage.clear();
sessionStorage.clear();
location.reload();
```

Then login fresh.

---

## ✅ Success Indicators

You'll know it's working when:

1. ✅ User data shows `market: "us"` in database
2. ✅ Order creates without errors
3. ✅ Order appears in US database (not KG)
4. ✅ Backend logs show: `User market set to: us`
5. ✅ Frontend shows success message

---

## 📊 Quick Status Check (One Command)

Run this to see everything at once:

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 << 'EOF'
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.users.user import User
from src.app_01.models.orders.order import Order

print("\n" + "="*70)
print("SYSTEM STATUS CHECK")
print("="*70)

# Check user
us_db = db_manager.get_session_factory(Market.US)()
user = us_db.query(User).filter(User.id == 19).first()

if user:
    print(f"\n✅ USER FOUND:")
    print(f"   ID: {user.id}")
    print(f"   Phone: {user.phone_number}")
    print(f"   Market: {user.market}")
    print(f"   Active: {user.is_active}")

    # Check orders
    orders = us_db.query(Order).filter(Order.user_id == 19).count()
    print(f"\n📦 ORDERS:")
    print(f"   Total: {orders} orders in US database")

    if orders > 0:
        latest = us_db.query(Order).filter(Order.user_id == 19).order_by(Order.created_at.desc()).first()
        print(f"   Latest: {latest.order_number}")
        print(f"   Date: {latest.order_date}")
else:
    print("\n❌ USER NOT FOUND")

us_db.close()
print("\n" + "="*70)
EOF
```

---

## 🎯 Next Steps

1. **If everything shows correctly** → Go to frontend and place an order
2. **If order succeeds** → Run "Quick Status Check" to confirm it saved
3. **If order fails** → Check the "Troubleshooting" section above

---

**Documentation:**

- Full implementation: `DATABASE_MARKET_FROM_USER_TABLE.md`
- Connection flow: `DATABASE_CONNECTION_FLOW.md`
- Fix history: `MULTI_MARKET_ORDER_FIX.md`
