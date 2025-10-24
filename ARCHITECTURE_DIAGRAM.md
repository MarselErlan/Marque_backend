# 🏗️ Authentication & Session Management Architecture

> Visual guide showing how everything works together

---

## 🎯 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S PHONE                            │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    REACT NATIVE APP                       │  │
│  │                                                           │  │
│  │  📱 UI Components:                                       │  │
│  │     - LoginScreen                                        │  │
│  │     - CartScreen                                         │  │
│  │     - WishlistScreen                                     │  │
│  │     - ProductScreen                                      │  │
│  │     - OrdersScreen                                       │  │
│  │                                                           │  │
│  │  💾 AsyncStorage:                                        │  │
│  │     ┌──────────────────────────────────────────┐       │  │
│  │     │  access_token: "eyJhbGci..."            │       │  │
│  │     │  (Contains: user_id, market, exp)       │       │  │
│  │     └──────────────────────────────────────────┘       │  │
│  │                                                           │  │
│  │  🔧 Services:                                            │  │
│  │     - authService.js (login/logout)                      │  │
│  │     - cartService.js (cart operations)                   │  │
│  │     - wishlistService.js (wishlist operations)           │  │
│  │                                                           │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                              │ HTTPS Request
                              │ Authorization: Bearer {token}
                              │ X-Market: us
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│                    (Railway Deployment)                         │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                   API Endpoints                          │  │
│  │                                                           │  │
│  │  🔐 Auth:                                                │  │
│  │     POST /auth/send-verification                         │  │
│  │     POST /auth/verify-code                               │  │
│  │     POST /auth/logout                                    │  │
│  │                                                           │  │
│  │  🛒 Cart:                                                │  │
│  │     GET  /cart                                           │  │
│  │     POST /cart/items                                     │  │
│  │     PUT  /cart/items/{id}                                │  │
│  │     DELETE /cart/items/{id}                              │  │
│  │                                                           │  │
│  │  ❤️  Wishlist:                                           │  │
│  │     GET  /wishlist                                       │  │
│  │     POST /wishlist/items                                 │  │
│  │     DELETE /wishlist/items/{id}                          │  │
│  │                                                           │  │
│  │  📦 Orders:                                              │  │
│  │     GET  /profile/orders                                 │  │
│  │     GET  /profile/orders/{id}                            │  │
│  │     POST /profile/orders/{id}/cancel                     │  │
│  │                                                           │  │
│  └──────────────────────────┬───────────────────────────────┘  │
│                              │                                  │
│  ┌──────────────────────────┴───────────────────────────────┐  │
│  │             Dependency: get_current_user_from_token()     │  │
│  │                                                           │  │
│  │  1. Extract token from Authorization header             │  │
│  │  2. Decode JWT:                                          │  │
│  │     {                                                    │  │
│  │       "user_id": 19,                                    │  │
│  │       "market": "us",                                   │  │
│  │       "exp": 1729703400                                 │  │
│  │     }                                                    │  │
│  │  3. Check expiration                                     │  │
│  │  4. Query database: SELECT * FROM users WHERE id = 19   │  │
│  │  5. Check is_active = true                              │  │
│  │  6. Return user info                                     │  │
│  │                                                           │  │
│  └──────────────────────────┬───────────────────────────────┘  │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                              │ SQL Queries
                              │ (using user_id = 19)
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                           │
│                    (Railway Deployment)                         │
│                                                                 │
│  📊 Tables:                                                     │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ users                                                   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ id: 19                                                  │  │
│  │ phone: +13128059851                                    │  │
│  │ is_active: true      ← Controls session validity! 🔑   │  │
│  │ is_verified: true                                      │  │
│  │ market: us                                             │  │
│  │ last_login: 2025-10-24 12:30:00                       │  │
│  └────────────────────────────────────────────────────────┘  │
│                              │                                  │
│                              │ Foreign Key                      │
│                              │                                  │
│  ┌───────────────────────────┴─────────────────────────────┐  │
│  │ carts                                                    │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ id: 5                                                    │  │
│  │ user_id: 19  ← Links cart to user! 🔗                   │  │
│  └───────────────────────────┬──────────────────────────────┘  │
│                              │ Foreign Key                      │
│                              │                                  │
│  ┌───────────────────────────┴─────────────────────────────┐  │
│  │ cart_items                                               │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ id: 101                                                  │  │
│  │ cart_id: 5  ← Links to cart above 🔗                    │  │
│  │ sku_id: 42                                              │  │
│  │ quantity: 2                                             │  │
│  │ ─────────────────────────                               │  │
│  │ id: 102                                                  │  │
│  │ cart_id: 5                                              │  │
│  │ sku_id: 88                                              │  │
│  │ quantity: 1                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ wishlists                                               │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ id: 8                                                   │  │
│  │ user_id: 19  ← Links wishlist to user! 🔗              │  │
│  └───────────────────────────┬─────────────────────────────┘  │
│                              │ Foreign Key                      │
│                              │                                  │
│  ┌───────────────────────────┴─────────────────────────────┐  │
│  │ wishlist_items                                           │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ id: 201                                                  │  │
│  │ wishlist_id: 8  ← Links to wishlist above 🔗           │  │
│  │ product_id: 15                                          │  │
│  │ ─────────────────────────                               │  │
│  │ id: 202                                                  │  │
│  │ wishlist_id: 8                                          │  │
│  │ product_id: 27                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ orders                                                  │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ id: 1001                                                │  │
│  │ order_number: #1001                                    │  │
│  │ user_id: 19  ← Links order to user! 🔗                 │  │
│  │ status: delivered                                      │  │
│  │ total_amount: 5999.99                                  │  │
│  │ order_date: 2025-10-20                                 │  │
│  │ ─────────────────────────                               │  │
│  │ id: 1002                                                │  │
│  │ order_number: #1002                                    │  │
│  │ user_id: 19                                            │  │
│  │ status: processing                                     │  │
│  │ total_amount: 2499.99                                  │  │
│  └───────────────────────────┬─────────────────────────────┘  │
│                              │ Foreign Key                      │
│                              │                                  │
│  ┌───────────────────────────┴─────────────────────────────┐  │
│  │ order_items                                              │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ id: 5001                                                 │  │
│  │ order_id: 1001                                          │  │
│  │ sku_id: 42                                              │  │
│  │ quantity: 1                                             │  │
│  │ unit_price: 5999.99                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete User Flow: Add to Cart

```
Step 1: User clicks "Add to Cart"
┌─────────────────────────────────────┐
│      React Native App               │
│                                     │
│  User clicks: Add to Cart           │
│  Button: sku_id = 42, quantity = 2 │
└──────────────┬──────────────────────┘
               │
               │ JavaScript:
               │ await cartService.addToCart(42, 2)
               │
               ↓
┌─────────────────────────────────────┐
│      API Service                    │
│                                     │
│  1. Get token from AsyncStorage     │
│     token = "eyJhbGci..."          │
│                                     │
│  2. Make HTTP request:              │
│     POST /cart/items                │
│     Headers:                        │
│       Authorization: Bearer {token} │
│       X-Market: us                  │
│     Body:                           │
│       {sku_id: 42, quantity: 2}    │
└──────────────┬──────────────────────┘
               │
               │ HTTPS Request
               │
               ↓
┌─────────────────────────────────────┐
│      Backend API Endpoint           │
│                                     │
│  @router.post("/cart/items")        │
│  def add_to_cart(                   │
│    request: AddToCartRequest,       │
│    current_user = Depends(...)      │
│  )                                  │
└──────────────┬──────────────────────┘
               │
               │ Decode JWT Token
               │
               ↓
┌─────────────────────────────────────┐
│  get_current_user_from_token()      │
│                                     │
│  1. Extract token:                  │
│     "eyJhbGci..."                  │
│                                     │
│  2. Decode JWT:                     │
│     payload = {                     │
│       user_id: 19,                 │
│       market: "us",                │
│       exp: 1729703400              │
│     }                               │
│                                     │
│  3. Check expiration:               │
│     if now() > exp: REJECT ❌      │
│                                     │
│  4. Query database:                 │
│     user = SELECT * FROM users     │
│            WHERE id = 19           │
│                                     │
│  5. Check if active:                │
│     if not user.is_active: REJECT ❌│
│                                     │
│  6. Return user:                    │
│     return {user_id: 19, ...}      │
└──────────────┬──────────────────────┘
               │
               │ user_id = 19 ✅
               │
               ↓
┌─────────────────────────────────────┐
│  add_to_cart() continues...         │
│                                     │
│  user_id = current_user.user_id    │
│  # user_id = 19                    │
│                                     │
│  1. Find or create cart:            │
│     cart = SELECT * FROM carts     │
│            WHERE user_id = 19      │
│                                     │
│     if not cart:                    │
│       INSERT INTO carts            │
│       (user_id) VALUES (19)       │
│       cart_id = 5                  │
│                                     │
│  2. Add item to cart:               │
│     INSERT INTO cart_items         │
│     (cart_id, sku_id, quantity)   │
│     VALUES (5, 42, 2)              │
│                                     │
│  3. Return response                 │
└──────────────┬──────────────────────┘
               │
               │ Response: {cart data}
               │
               ↓
┌─────────────────────────────────────┐
│      React Native App               │
│                                     │
│  Show: "Added to cart!" ✅         │
└─────────────────────────────────────┘
```

---

## 🚪 Logout and Login Flow

```
LOGOUT:
───────

User clicks "Logout"
  ↓
Frontend: authService.logout()
  ↓
Backend: POST /auth/logout
  ↓
Database: UPDATE users
          SET is_active = false
          WHERE id = 19
  ↓
Frontend: AsyncStorage.removeItem('access_token')
  ↓
✅ User logged out
   - Token deleted from phone
   - is_active = false (token won't work even if intercepted)
   - Cart data STILL IN DATABASE (user_id = 19)


LOGIN AGAIN:
────────────

User enters phone + code
  ↓
Backend: POST /auth/verify-code
  ↓
Backend verifies code with Twilio
  ↓
Database: UPDATE users
          SET is_active = true,
              last_login = NOW()
          WHERE phone = '+13128059851'
  ↓
Backend finds user_id = 19 (SAME USER!)
  ↓
Backend creates NEW JWT token:
  {
    user_id: 19,     ← SAME user_id!
    market: "us",
    exp: (30 min from now)
  }
  ↓
Frontend: AsyncStorage.setItem('access_token', NEW_TOKEN)
  ↓
✅ User logged in
   - New token stored
   - is_active = true
   - Same user_id = 19


CHECK CART:
───────────

User opens cart
  ↓
Frontend: await cartService.getCart()
  ↓
Frontend sends: Authorization: Bearer {NEW_TOKEN}
  ↓
Backend decodes NEW_TOKEN:
  → user_id = 19 (SAME user_id!)
  ↓
Backend queries:
  SELECT * FROM cart_items
  WHERE cart_id IN (
    SELECT id FROM carts WHERE user_id = 19
  )
  ↓
Returns: Same items as before logout!
  - sku_id: 42, quantity: 2
  ↓
✅ CART PERSISTED! 🎉
```

---

## 🔑 Key Concepts Visualized

### 1. JWT Token = Temporary Key 🗝️

```
JWT Token Lifecycle:
────────────────────

[Created]           [Expires]
   │                   │
   ├───────30min───────┤
   │                   │
   ↓                   ↓
 Valid              Invalid
 (Works)            (Must re-login)

BUT: User data persists in database!

Database:
─────────
users (id: 19) ←─┬─ carts
                 ├─ wishlists
                 └─ orders

This NEVER expires! ✅
```

### 2. user_id = Permanent Identity 🆔

```
Different Tokens, Same User:
────────────────────────────

Login 1 (Oct 1):
  Token: eyJA...xyz1
  Contains: {user_id: 19, exp: ...}
                     ↓
Login 2 (Oct 15):         ┌─────┐
  Token: eyJB...abc2   ───→│ 19 │← Always same user_id!
  Contains: {user_id: 19}  └─────┘
                     ↓          ↑
Login 3 (Oct 30):               │
  Token: eyJC...def3   ─────────┘
  Contains: {user_id: 19}

All tokens → Same database records!
```

### 3. Foreign Keys = Data Linkage 🔗

```
Database Relationships:
───────────────────────

users.id = 19
    │
    ├── carts.user_id = 19
    │       │
    │       └── cart_items.cart_id = 5
    │              ├─ item 1
    │              └─ item 2
    │
    ├── wishlists.user_id = 19
    │       │
    │       └── wishlist_items.wishlist_id = 8
    │              ├─ item 1
    │              └─ item 2
    │
    └── orders.user_id = 19
            ├─ order #1001
            └─ order #1002

As long as user_id exists:
  ✅ All data accessible
  ✅ Survives logout
  ✅ Survives token expiration
  ✅ Syncs across devices
```

---

## 🎯 Summary

### What's Stored Where:

| Data           | Storage                      | Lifetime             |
| -------------- | ---------------------------- | -------------------- |
| JWT Token      | Frontend (AsyncStorage)      | 30 minutes           |
| user_id        | Database + JWT               | Forever              |
| Cart Items     | Database (linked to user_id) | Forever              |
| Wishlist Items | Database (linked to user_id) | Forever              |
| Orders         | Database (linked to user_id) | Forever              |
| is_active flag | Database                     | Controlled by logout |

### How It Works:

1. **Login** → Generate JWT with `user_id` → Store in AsyncStorage
2. **Every Request** → Send JWT → Decode to get `user_id` → Query database
3. **Add to Cart** → Save in database linked to `user_id` ✅
4. **Logout** → Set `is_active = false` → Delete token from AsyncStorage
5. **Login Again** → New JWT with same `user_id` → Access same cart ✅

### Why It's Secure:

1. **JWT expires** (30 min) → Must re-login regularly
2. **is_active flag** → Logout invalidates token immediately
3. **HTTPS** → Token encrypted in transit
4. **No token in database** → Can't be stolen from database breach
5. **Foreign keys** → Users can only access their own data

---

## ✅ You're All Set!

Your architecture is **production-ready** and follows **industry best practices**! 🚀

See:

- [`SESSION_MANAGEMENT_EXPLAINED.md`](./SESSION_MANAGEMENT_EXPLAINED.md) - Detailed explanation
- [`SESSION_QUICK_REFERENCE.md`](./SESSION_QUICK_REFERENCE.md) - Quick reference
- [`FRONTEND_CART_EXAMPLE.md`](./FRONTEND_CART_EXAMPLE.md) - Frontend code examples
