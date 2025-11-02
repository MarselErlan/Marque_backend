# Step-by-Step Fix for User ID Issue

## Current Status:

- ✅ Database has User ID 10 for phone +13128059851
- ✅ User ID 19 does NOT exist in database
- ✅ localStorage cleared
- ❌ You're seeing OLD console logs from before clear
- ❌ Need to login again to get fresh token

---

## ✅ Complete Fix (Follow Exactly):

### Step 1: Clear Everything (Again, to be sure)

1. Press **F12** (DevTools)
2. Go to **Console** tab
3. Clear old logs by clicking 🚫 icon or pressing Ctrl+L
4. Paste and run:

```javascript
localStorage.clear();
sessionStorage.clear();
console.log("✅ Storage cleared");
console.log("Auth token:", localStorage.getItem("authToken"));
console.log("User data:", localStorage.getItem("userData"));
```

**Expected Output:**

```
✅ Storage cleared
Auth token: null
User data: null
```

---

### Step 2: Refresh Page

```javascript
location.reload();
```

---

### Step 3: Login Again

1. Click "Войти" (Login) button
2. Enter phone: **+13128059851**
3. Request verification code
4. Enter the code you receive
5. Complete login

---

### Step 4: Verify New Token

After login, open Console again and run:

```javascript
const userData = JSON.parse(localStorage.getItem("userData"));
const authToken = localStorage.getItem("authToken");

console.log("=== NEW LOGIN DATA ===");
console.log("User ID:", userData?.id); // Should be 10
console.log("Phone:", userData?.phone);
console.log("Token exists:", !!authToken);
console.log("Token preview:", authToken?.substring(0, 50) + "...");
```

**Expected Output:**

```
=== NEW LOGIN DATA ===
User ID: 10          ← Should be 10, not 19!
Phone: +13128059851
Token exists: true
Token preview: eyJhbGci...
```

---

### Step 5: Test Order Creation

1. Add item to cart
2. Go to checkout
3. Fill in:
   - Name: Test Customer
   - Phone: +13128059851
   - Address: Юнусалиева, 40
   - Payment: Card or Cash
4. Click "Place Order"
5. ✅ Order should save!

---

### Step 6: Verify in Database

Run this in your terminal:

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python -c "
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.orders.order import Order

SessionLocal = db_manager.get_session_factory(Market.KG)
db = SessionLocal()

orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()
print(f'\n📦 Recent Orders:')
for o in orders:
    print(f'   {o.order_number}: {o.customer_name} - {o.total_amount} {o.currency}')

db.close()
"
```

---

## 🔍 Why You're Still Seeing ID 19:

The console logs you're seeing are from **BEFORE** you cleared localStorage. Those errors happened when:

1. Old token (with user_id 19) tried to make API calls
2. Backend returned "User not found" (because ID 19 doesn't exist)
3. Those errors are cached in the console

**Solution:** After clearing storage and logging in again, you'll get a **fresh token with user_id 10**.

---

## 🎯 What Should Happen:

### Before Login (After Clear):

```
localStorage.getItem('authToken') → null
localStorage.getItem('userData') → null
```

### After Login with +13128059851:

```
localStorage.getItem('authToken') → "eyJhbGciOiJI..." (new token)
localStorage.getItem('userData') → {"id": 10, "phone": "+13128059851", ...}
                                           ↑
                                      Should be 10!
```

---

## ⚠️ Important Notes:

1. **Don't look at old console logs** - They show errors from before you cleared storage
2. **Clear console logs** - Click 🚫 or press Ctrl+L
3. **Login again** - This creates a NEW token with correct user_id
4. **Check userData.id** - Should be 10 after new login
5. **Then test order** - Will save to database!

---

## 🐛 If Still Showing 19 After New Login:

If after logging in fresh you STILL see user_id 19, then check:

1. **Which phone number did you use?**

   ```javascript
   // In console after login:
   const userData = JSON.parse(localStorage.getItem("userData"));
   console.log("Logged in with phone:", userData?.phone);
   ```

2. **Check backend logs** - See what user_id backend returned:

   ```bash
   tail -20 /Users/macbookpro/M4_Projects/Prodaction/Marque/backend.log
   ```

3. **Try incognito window** - Completely fresh browser:
   - Open Chrome/Firefox incognito
   - Go to site
   - Login with +13128059851
   - Check user_id

---

## ✅ Success Indicators:

After completing all steps, you should see:

- ✅ `userData.id = 10` (not 19)
- ✅ No "User not found" errors in console
- ✅ Cart loads successfully
- ✅ Orders save to database
- ✅ Order appears in admin panel

---

**Next:** Clear console, refresh, login again, then check userData.id!
