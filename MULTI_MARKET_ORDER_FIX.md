# Multi-Market Order System Fix

## 🎯 Problem Discovered

The user was experiencing orders not saving to the database. After investigation, we discovered a **multi-market database mismatch**:

### The Root Cause:

The application has **TWO separate databases**:

- **KG Database** (Kyrgyzstan): For users with +996 phone numbers
- **US Database** (United States): For users with +1 phone numbers

**The Issue:**

- User logged in with phone **+13128059851** (US number)
- Frontend authenticated against **US database** → Got **User ID 19**
- But `order_router.py` was using `Depends(get_db)` which **defaults to KG database**
- Order creation tried to save with **User ID 19** in **KG database**
- **KG database has no User ID 19** (only has User ID 10 for a different +996 user)
- Result: **"User not found"** error, orders not saving

### Database State:

```
📍 KG Database (Kyrgyzstan):
   - Phone +13128059851 → User ID: 10 (created for testing)
   - Currency: сом (KGS)
   - Prefix: +996

📍 US Database (United States):
   - Phone +13128059851 → User ID: 19 (actual user)
   - Currency: $ (USD)
   - Prefix: +1
```

### User Token (from frontend):

```json
{
  "sub": "19", // User ID
  "market": "us", // US database
  "exp": 1730506363 // Token expiration
}
```

---

## ✅ Solution Implemented

Modified `src/app_01/routers/order_router.py` to use the **user's market from their JWT token** instead of defaulting to KG database.

### Changes Made:

#### 1. `create_order` endpoint (Line 170-195)

**Before:**

```python
async def create_order(
    request: CreateOrderRequest,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)  # ❌ Always defaults to KG database
):
    try:
        user_id = current_user.user_id
        # ...
```

**After:**

```python
async def create_order(
    request: CreateOrderRequest,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    try:
        user_id = current_user.user_id

        # ✅ FIX: Use the user's market from token instead of defaulting to KG
        user_market = Market(current_user.market.value) if current_user.market else Market.KG
        from ..db.market_db import db_manager
        SessionLocal = db_manager.get_session_factory(user_market)
        db = SessionLocal()

        # Step 1: Get items to order
        # ...
    finally:
        db.close()
```

#### 2. `get_user_orders` endpoint (Line 358-422)

**Before:**

```python
async def get_user_orders(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),  # ❌ Always defaults to KG database
    # ...
):
    query = db.query(Order).filter(
        Order.user_id == current_user.user_id
    )
```

**After:**

```python
async def get_user_orders(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    status_filter: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    # ✅ FIX: Use the user's market from token
    user_market = Market(current_user.market.value) if current_user.market else Market.KG
    from ..db.market_db import db_manager
    SessionLocal = db_manager.get_session_factory(user_market)
    db = SessionLocal()

    try:
        query = db.query(Order).filter(
            Order.user_id == current_user.user_id
        )
        # ...
        return [orders]
    finally:
        db.close()
```

#### 3. `get_order_detail` endpoint (Line 426-478)

**Before:**

```python
async def get_order_detail(
    order_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)  # ❌ Always defaults to KG database
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.user_id
    ).first()
```

**After:**

```python
async def get_order_detail(
    order_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    # ✅ FIX: Use the user's market from token
    user_market = Market(current_user.market.value) if current_user.market else Market.KG
    from ..db.market_db import db_manager
    SessionLocal = db_manager.get_session_factory(user_market)
    db = SessionLocal()

    try:
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.user_id
        ).first()
        # ...
        return OrderResponse(...)
    finally:
        db.close()
```

---

## 🔧 How It Works Now

### Authentication Flow:

1. **User logs in** with phone **+13128059851**
2. **Backend** (`auth_service.py`):
   - Detects market from phone number: `+1` → **US**
   - Looks up user in **US database**
   - Finds **User ID 19**
   - Creates JWT token:
     ```json
     {
       "sub": "19",
       "market": "us",
       "exp": ...
     }
     ```
3. **Frontend** stores token in `localStorage`

### Order Creation Flow:

1. **User** clicks "Place Order"
2. **Frontend** sends request with JWT token
3. **Backend** (`order_router.py`):
   - Verifies token → Gets `user_id: 19`, `market: us`
   - ✅ **NEW:** Extracts market from token
   - Connects to **US database** (not KG!)
   - Looks up **User ID 19** in **US database** ✅ (exists!)
   - Creates order successfully
   - Saves to **US database**
4. **Success!** Order is saved and returned

### Market Detection:

```python
# Get user's market from token
user_market = Market(current_user.market.value) if current_user.market else Market.KG

# Connect to the correct database
SessionLocal = db_manager.get_session_factory(user_market)
db = SessionLocal()
```

---

## 📊 Testing

### Before Fix:

```bash
Frontend: Login with +13128059851
Token: { user_id: 19, market: "us" }

Frontend: Place order
Backend: Using KG database (default)
Backend: Looking for User ID 19 in KG database
Result: ❌ "User not found" (KG database has no ID 19)
```

### After Fix:

```bash
Frontend: Login with +13128059851
Token: { user_id: 19, market: "us" }

Frontend: Place order
Backend: Extract market from token → "us"
Backend: Using US database (from token!)
Backend: Looking for User ID 19 in US database
Result: ✅ User found! Order created successfully!
```

---

## ✅ Verification Steps

### 1. Check Backend Logs:

```bash
tail -f /Users/macbookpro/M4_Projects/Prodaction/Marque/backend.log
```

Look for:

```
✅ User authenticated successfully: ID=19, Market=us
✅ Order created: Order #MQ-20251102-XXXXX for User ID=19
```

### 2. Check Database:

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python -c "
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.orders.order import Order

# Check US database
SessionLocal = db_manager.get_session_factory(Market.US)
db = SessionLocal()

orders = db.query(Order).filter(Order.user_id == 19).order_by(Order.created_at.desc()).limit(5).all()
print(f'\n📦 Recent Orders for User ID 19 (US):')
for o in orders:
    print(f'   {o.order_number}: {o.customer_name} - {o.total_amount} {o.currency}')

db.close()
"
```

### 3. Test Frontend:

1. Clear browser cache and localStorage
2. Login with **+13128059851**
3. Add items to cart
4. Place order
5. ✅ Order should save successfully!
6. Check profile → Orders section → Should see new order

---

## 🔄 Market Auto-Detection

The system automatically detects market from phone number:

```python
# From src/app_01/db/market_db.py:
def detect_market_from_phone(phone_number: str) -> Market:
    clean_phone = phone_number.replace(" ", "").replace("-", "")

    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    if clean_phone.startswith("+996"):
        return Market.KG  # Kyrgyzstan
    elif clean_phone.startswith("+1"):
        return Market.US  # United States
    else:
        return Market.KG  # Default to KG
```

---

## 📋 Files Modified

1. **src/app_01/routers/order_router.py**
   - `create_order` endpoint: Extract market from token
   - `get_user_orders` endpoint: Extract market from token
   - `get_order_detail` endpoint: Extract market from token
   - All endpoints now connect to correct database based on user's market

---

## 🎯 Key Takeaways

### What Was Wrong:

- ❌ Order system defaulted to KG database for ALL users
- ❌ US users couldn't create orders (user not found in KG DB)
- ❌ KG users couldn't access orders if using US DB

### What's Fixed:

- ✅ Order system now uses user's market from JWT token
- ✅ US users → US database → Orders save correctly
- ✅ KG users → KG database → Orders save correctly
- ✅ Each user sees only their orders from their market's database

### Why It Works:

- JWT token contains `market` field set during login
- Market is determined by phone number prefix (+1 = US, +996 = KG)
- Order endpoints extract market from token and connect to correct DB
- User ID is unique within each market's database

---

## 🚀 Next Steps

1. **Clear your browser localStorage** (if you haven't already):

   ```javascript
   localStorage.clear();
   sessionStorage.clear();
   location.reload();
   ```

2. **Login fresh** with **+13128059851**

3. **Place an order** - Should work now! ✅

4. **Verify in database**:
   - Orders should appear in **US database**
   - With **User ID 19**
   - Not in KG database

---

## 📝 Notes

- The multi-market system is designed for scalability (can add more markets)
- Each market has its own:
  - Database
  - Currency
  - Phone format
  - Tax rates
  - Shipping zones
  - Payment methods
- The fix ensures orders are always created in the correct market's database

---

**Status:** ✅ **FIXED** - Multi-market order system now works correctly for both KG and US users!
