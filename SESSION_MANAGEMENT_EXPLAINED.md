# 🔐 Session Management & Data Persistence - Complete Guide

> **Answer**: You DON'T need session tokens! Your cart, wishlist, and orders will NEVER be lost. Here's why...

---

## 🎯 Your Question

**"If I don't save access_token in the database, how do I ensure user cart/wishlist/orders don't get lost?"**

---

## ✅ The Answer: JWT + Database Foreign Keys

Your system is **already correctly implemented**! Here's how it works:

### 1. **JWT Token Contains User ID**

When user logs in, the JWT token contains:

```json
{
  "user_id": 19,
  "market": "us",
  "exp": 1729703400
}
```

This token is:

- ✅ Stored in **frontend** (localStorage or AsyncStorage)
- ❌ NOT stored in **database**
- ✅ Sent with every API request

---

### 2. **Database Links Everything to User ID**

Your database already has these relationships:

```sql
-- Cart is linked to user
CREATE TABLE carts (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,  -- 👈 Links cart to user!
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Wishlist is linked to user
CREATE TABLE wishlists (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,  -- 👈 Links wishlist to user!
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Orders are linked to user
CREATE TABLE orders (
    id INT PRIMARY KEY,
    user_id INT NOT NULL,  -- 👈 Links order to user!
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

### 3. **Complete Flow: Adding Product to Cart**

Let's trace what happens when user adds a product to cart:

#### Frontend (React/React Native):

```javascript
// 1. User clicks "Add to Cart"
async function addToCart(sku_id, quantity) {
  // 2. Get token from storage
  const token = await AsyncStorage.getItem("access_token");

  // 3. Send request with token
  const response = await fetch("https://api.com/cart/items", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`, // 👈 Token sent here
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ sku_id, quantity }),
  });
}
```

#### Backend (Your FastAPI code):

```python
# src/app_01/routers/cart_router.py

@router.post("/items")
def add_to_cart(
    request: AddToCartRequest,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    # 1. get_current_user_from_token() automatically:
    #    - Extracts token from Authorization header
    #    - Decodes JWT → gets user_id = 19
    #    - Returns user info

    user_id = current_user.user_id  # user_id = 19

    # 2. Find or create cart for THIS user
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)  # Create cart linked to user_id
        db.add(cart)
        db.commit()

    # 3. Add item to cart
    cart_item = CartItem(
        cart_id=cart.id,
        sku_id=request.sku_id,
        quantity=request.quantity
    )
    db.add(cart_item)
    db.commit()

    # ✅ Data is now PERMANENTLY stored in database!
    # ✅ Linked to user_id = 19
    # ✅ Will survive login/logout/token expiration
```

---

## 🔄 What Happens in Different Scenarios

### Scenario 1: User Logs Out and Logs Back In

```
1. User adds 3 items to cart
   ↓
2. Database saves: cart (user_id=19) → cart_items (3 items) ✅
   ↓
3. User logs out:
   - Frontend: Deletes token from AsyncStorage
   - Backend: Sets is_active = false
   ↓
4. User logs back in:
   - New JWT token generated (still contains user_id=19)
   - Frontend: Stores new token
   ↓
5. User opens cart:
   GET /cart
   Authorization: Bearer {new_token}
   ↓
6. Backend:
   - Decodes token → user_id = 19
   - Queries: SELECT * FROM carts WHERE user_id = 19
   - Returns: Same 3 items! ✅
```

**Result**: Cart is preserved! 🎉

---

### Scenario 2: Token Expires

```
1. User adds items to cart
   ↓
2. Database saves items ✅
   ↓
3. 30 minutes later: Token expires
   ↓
4. User tries to add more items:
   - Backend rejects: "Token expired"
   - Frontend redirects to login
   ↓
5. User logs in again:
   - New token generated
   - Still same user_id = 19
   ↓
6. Cart loads:
   - Same items still there! ✅
```

**Result**: Cart is preserved! 🎉

---

### Scenario 3: User Closes App for a Week

```
1. User adds items to cart
   ↓
2. Database saves items ✅
   ↓
3. User closes app for 1 week
   ↓
4. User opens app again:
   - Old token expired
   - User must login again
   ↓
5. User logs in:
   - New token with same user_id = 19
   ↓
6. Cart loads:
   - Same items from 1 week ago! ✅
```

**Result**: Cart is preserved! 🎉

---

## 📊 Data Persistence Architecture

```
┌─────────────────────────────────────────────────┐
│                  FRONTEND                       │
│                                                 │
│  ┌────────────────────────────────────────┐   │
│  │  AsyncStorage / localStorage           │   │
│  │                                        │   │
│  │  access_token: "eyJhbGci..."          │   │
│  │  (Contains user_id: 19)               │   │
│  └────────────────────────────────────────┘   │
│                                                 │
│  Every API request:                            │
│  Authorization: Bearer {access_token}          │
└───────────────────┬─────────────────────────────┘
                    │
                    │ HTTP Request
                    ↓
┌─────────────────────────────────────────────────┐
│                  BACKEND                        │
│                                                 │
│  1. Extract token from header                  │
│  2. Decode JWT → user_id = 19                  │
│  3. Check is_active = true                     │
│  4. Use user_id for all database queries       │
└───────────────────┬─────────────────────────────┘
                    │
                    │ Database Query
                    ↓
┌─────────────────────────────────────────────────┐
│                DATABASE (PostgreSQL)            │
│                                                 │
│  users                                         │
│  ├─ id: 19                                    │
│  ├─ phone: +13128059851                       │
│  ├─ is_active: true                           │
│  └─ last_login: 2025-10-24                    │
│                                                 │
│  carts                                         │
│  ├─ id: 5                                     │
│  └─ user_id: 19 ──────────────┐ (FK)         │
│                                 │               │
│  cart_items                    │               │
│  ├─ id: 101                    │               │
│  ├─ cart_id: 5 ────────────────┘              │
│  ├─ sku_id: 42                                │
│  └─ quantity: 2                               │
│                                                 │
│  wishlists                                     │
│  ├─ id: 8                                     │
│  └─ user_id: 19 ──────────────┐ (FK)         │
│                                 │               │
│  wishlist_items                │               │
│  ├─ id: 201                    │               │
│  ├─ wishlist_id: 8 ────────────┘              │
│  └─ product_id: 15                            │
│                                                 │
│  orders                                        │
│  ├─ id: 1001                                  │
│  ├─ user_id: 19 ──────────────┐ (FK)         │
│  ├─ order_number: #1001                       │
│  ├─ status: delivered                         │
│  └─ total_amount: 5999.99                     │
│                                 │               │
│  order_items                   │               │
│  ├─ id: 5001                   │               │
│  ├─ order_id: 1001 ────────────┘              │
│  ├─ sku_id: 42                                │
│  └─ quantity: 1                               │
└─────────────────────────────────────────────────┘

✅ ALL DATA PERSISTS IN DATABASE
✅ ALL DATA LINKED TO user_id
✅ TOKEN IS JUST A KEY TO IDENTIFY USER
✅ LOSING TOKEN ≠ LOSING DATA
```

---

## 🎯 Key Concepts

### 1. **JWT Token = Temporary Key**

Think of JWT token like a **hotel room key card**:

- ✅ It gives you access to your room (your data)
- ✅ Your belongings are in the room (database)
- ✅ If you lose the card, you get a new one (re-login)
- ✅ Your belongings are still in the room! (data persists)

### 2. **user_id = Your Identity**

The `user_id` never changes:

```python
# First login (Oct 1):
JWT Token 1: { user_id: 19, exp: ... }

# Second login (Oct 15):
JWT Token 2: { user_id: 19, exp: ... }  # Still same user_id!

# Third login (Oct 30):
JWT Token 3: { user_id: 19, exp: ... }  # Still same user_id!
```

Database queries always use `user_id`:

```python
# Backend always does this:
cart = db.query(Cart).filter(Cart.user_id == current_user.user_id).first()

# Not this:
cart = db.query(Cart).filter(Cart.token == token).first()  # ❌ WRONG!
```

---

## 🔒 Security: Why is_active Matters

The `is_active` flag is what ACTUALLY controls access:

```python
# User model
class User:
    id = 19
    phone = "+13128059851"
    is_active = True  # 👈 This controls access!
```

### Login:

```python
# Backend sets:
user.is_active = True
user.last_login = datetime.now()
db.commit()

# Returns JWT with user_id = 19
```

### Logout:

```python
# Backend sets:
user.is_active = False
db.commit()

# Token becomes useless (even if not expired!)
```

### Every Request:

```python
# Backend checks:
if not user.is_active:
    raise HTTPException(401, "User account is inactive")
```

---

## 📱 Frontend Implementation Best Practices

### 1. **Store Token Securely**

```javascript
// ✅ CORRECT
import AsyncStorage from "@react-native-async-storage/async-storage";

// After login:
await AsyncStorage.setItem("access_token", token);

// On each request:
const token = await AsyncStorage.getItem("access_token");
```

### 2. **Send Token with Every Request**

```javascript
// ✅ CORRECT - All your cart/wishlist/order requests
async function apiRequest(endpoint, method = "GET", body = null) {
  const token = await AsyncStorage.getItem("access_token");

  const response = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`, // 👈 Required!
      "Content-Type": "application/json",
      "X-Market": "us", // or 'kg'
    },
    body: body ? JSON.stringify(body) : null,
  });

  return response.json();
}

// Usage:
await apiRequest("/cart/items", "POST", { sku_id: 42, quantity: 2 });
await apiRequest("/wishlist/items", "POST", { product_id: 15 });
await apiRequest("/profile/orders"); // Get order history
```

### 3. **Handle Token Expiration**

```javascript
// ✅ CORRECT - Redirect to login on 401
async function apiRequest(endpoint, method = "GET", body = null) {
  const token = await AsyncStorage.getItem("access_token");

  const response = await fetch(`${API_URL}${endpoint}`, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: body ? JSON.stringify(body) : null,
  });

  if (response.status === 401) {
    // Token expired or invalid
    await AsyncStorage.removeItem("access_token");
    navigation.navigate("Login");
    throw new Error("Please login again");
  }

  return response.json();
}
```

### 4. **Proper Logout**

```javascript
// ✅ CORRECT - Call backend logout + clear local token
async function logout() {
  try {
    // 1. Call backend logout (sets is_active = false)
    await apiRequest("/auth/logout", "POST");
  } catch (error) {
    console.error("Logout error:", error);
  } finally {
    // 2. Clear local token
    await AsyncStorage.removeItem("access_token");

    // 3. Navigate to login
    navigation.navigate("Login");
  }
}
```

---

## 🧪 Testing Your Implementation

### Test 1: Cart Persistence After Logout

```bash
# 1. Login
curl -X POST https://api.com/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+13128059851", "verification_code": "123456"}'

# Response:
{
  "access_token": "eyJhbGci...",
  "user": {"id": 19, ...}
}

# 2. Add item to cart
curl -X POST https://api.com/cart/items \
  -H "Authorization: Bearer eyJhbGci..." \
  -H "Content-Type: application/json" \
  -d '{"sku_id": 42, "quantity": 2}'

# Response: Cart with item

# 3. Logout
curl -X POST https://api.com/auth/logout \
  -H "Authorization: Bearer eyJhbGci..."

# 4. Login again (same user)
curl -X POST https://api.com/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"phone": "+13128059851", "verification_code": "654321"}'

# Response:
{
  "access_token": "NEW_TOKEN_HERE",  # Different token!
  "user": {"id": 19, ...}            # Same user_id!
}

# 5. Get cart
curl -X GET https://api.com/cart \
  -H "Authorization: Bearer NEW_TOKEN_HERE"

# Response: Cart still has the item! ✅
```

---

## 🎯 Summary: What You Need to Know

### ✅ What IS Stored in Database:

- User information (`users` table)
- Cart items (`carts` and `cart_items` tables)
- Wishlist items (`wishlists` and `wishlist_items` tables)
- Orders (`orders` and `order_items` tables)
- All linked via `user_id` foreign key

### ❌ What is NOT Stored in Database:

- JWT access tokens (stored only in frontend)
- Session tokens (not needed!)

### 🔑 How It Works:

1. User logs in → Backend generates JWT with `user_id`
2. Frontend stores JWT in AsyncStorage/localStorage
3. Every API request includes JWT in `Authorization` header
4. Backend decodes JWT → extracts `user_id`
5. Backend uses `user_id` to query database
6. All data (cart/wishlist/orders) persists via `user_id` foreign keys

### 🛡️ Security:

- JWT tokens are short-lived (30 min)
- Backend checks `is_active` flag on every request
- Logout sets `is_active = false` → token becomes useless
- User must re-login after logout or token expiration

### 📦 Data Persistence:

- Cart/wishlist/orders are **ALWAYS** saved in database
- Losing token ≠ losing data
- Re-login → same `user_id` → same data ✅

---

## 🚀 You're All Set!

Your current implementation is **correct** and **secure**! You don't need to change anything.

### What Happens Now:

1. ✅ User can add items to cart → Items persist in database
2. ✅ User can logout and login → Cart items still there
3. ✅ User can close app → Cart items still there
4. ✅ Token expires → User re-logins → Cart items still there
5. ✅ Orders are saved forever (linked to user_id)
6. ✅ Wishlist persists across sessions

**You're ready to build your frontend!** 🎉

---

## 📚 Related Documentation

- [`NO_DATABASE_MIGRATION_NEEDED.md`](./NO_DATABASE_MIGRATION_NEEDED.md) - Why tokens aren't stored in DB
- [`START_HERE_FRONTEND.md`](./START_HERE_FRONTEND.md) - Frontend integration guides
- [`FRONTEND_INTEGRATION_GUIDE.md`](./FRONTEND_INTEGRATION_GUIDE.md) - Complete API reference
- [`COPY_PASTE_FRONTEND_CODE.md`](./COPY_PASTE_FRONTEND_CODE.md) - Ready-to-use code

---

## ❓ Still Have Questions?

### Q: What if user changes phone number?

**A**: The `user_id` stays the same. You update `phone_number` field, but cart/orders stay linked to same `user_id`.

### Q: Can multiple users share same cart?

**A**: No. Each cart has unique `user_id`. Each user has their own cart.

### Q: What happens if token is stolen?

**A**:

1. User can logout → sets `is_active = false` → stolen token becomes useless
2. Tokens expire after 30 minutes
3. Use HTTPS (you are!) to prevent token theft

### Q: Do I need session management library?

**A**: No! Your JWT + database approach is industry standard and works perfectly.

---

**🎉 Happy Coding!**
