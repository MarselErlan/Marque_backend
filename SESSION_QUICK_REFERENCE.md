# 🎯 Session Management - Quick Reference Card

> **TL;DR**: You don't need session tokens! Your system already works perfectly!

---

## ✅ What Your System Does Right Now

| Feature             | How It Works                     | Where It's Stored            |
| ------------------- | -------------------------------- | ---------------------------- |
| **Login**           | JWT token created with `user_id` | Frontend only (AsyncStorage) |
| **Cart**            | Linked to `user_id` in database  | Database (permanent)         |
| **Wishlist**        | Linked to `user_id` in database  | Database (permanent)         |
| **Orders**          | Linked to `user_id` in database  | Database (permanent)         |
| **Session Control** | `is_active` flag in users table  | Database                     |

---

## 🔄 Complete User Journey

```
📱 ADD TO CART
--------------
User clicks "Add to Cart"
  ↓
Frontend sends: Authorization: Bearer {JWT_TOKEN}
  ↓
Backend decodes JWT → user_id = 19
  ↓
Backend saves: INSERT INTO cart_items (cart_id, sku_id, quantity)
                WHERE cart.user_id = 19
  ↓
✅ SAVED IN DATABASE PERMANENTLY


🚪 LOGOUT
---------
User clicks "Logout"
  ↓
Backend updates: UPDATE users SET is_active = false WHERE id = 19
  ↓
Frontend deletes token
  ↓
✅ SESSION ENDED (but cart data still in database!)


🔓 LOGIN AGAIN
--------------
User enters phone + code
  ↓
Backend updates: UPDATE users SET is_active = true WHERE id = 19
  ↓
Backend creates NEW JWT token (still contains user_id = 19)
  ↓
Frontend stores new token
  ↓
User opens cart
  ↓
Backend queries: SELECT * FROM cart_items
                 WHERE cart_id IN (SELECT id FROM carts WHERE user_id = 19)
  ↓
✅ SAME CART ITEMS RETURNED!
```

---

## 🎯 Key Principles

### 1. JWT Token = Temporary Access Key

```javascript
// JWT Token (stored in frontend):
{
  "user_id": 19,      // 👈 This identifies the user
  "market": "us",
  "exp": 1729703400   // 👈 Expires in 30 minutes
}
```

- ✅ Contains `user_id` to identify user
- ✅ Short-lived (30 minutes)
- ✅ Decoded on every request
- ❌ NOT stored in database

### 2. Database = Permanent Storage

```sql
-- Everything linked to user_id:

carts (user_id: 19)
  └─ cart_items
      ├─ sku_id: 42, quantity: 2
      └─ sku_id: 88, quantity: 1

wishlists (user_id: 19)
  └─ wishlist_items
      ├─ product_id: 15
      └─ product_id: 27

orders (user_id: 19)
  └─ order_items
      ├─ order #1001
      └─ order #1002
```

- ✅ All data linked via `user_id`
- ✅ Persists forever
- ✅ Survives logout/login/token expiration

### 3. is_active = Session Control

```python
# User table:
{
  "id": 19,
  "phone": "+13128059851",
  "is_active": true  # 👈 Controls if token works!
}

# Login: is_active = true  → token works ✅
# Logout: is_active = false → token rejected ❌
```

---

## 📋 Your Implementation Checklist

### Backend (Already Done ✅)

- [x] JWT contains `user_id`
- [x] Cart has `user_id` foreign key
- [x] Wishlist has `user_id` foreign key
- [x] Orders have `user_id` foreign key
- [x] All endpoints use `get_current_user_from_token()`
- [x] Logout sets `is_active = false`

### Frontend (What You Need)

```javascript
// 1. Store token after login
await AsyncStorage.setItem("access_token", token);

// 2. Send token with every request
const token = await AsyncStorage.getItem("access_token");
fetch(url, {
  headers: {
    Authorization: `Bearer ${token}`,
    "X-Market": "us",
  },
});

// 3. Handle token expiration
if (response.status === 401) {
  // Token expired → redirect to login
  navigation.navigate("Login");
}

// 4. Logout properly
await fetch("/auth/logout", {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
});
await AsyncStorage.removeItem("access_token");
navigation.navigate("Login");
```

---

## 🧪 Quick Test Commands

### Test Cart Persistence:

```bash
# 1. Login
curl -X POST https://api.com/auth/verify-code \
  -H "Content-Type: application/json" \
  -H "X-Market: us" \
  -d '{"phone": "+13128059851", "verification_code": "123456"}'

# Save the access_token from response

# 2. Add to cart
curl -X POST https://api.com/cart/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Market: us" \
  -H "Content-Type: application/json" \
  -d '{"sku_id": 1, "quantity": 2}'

# 3. Check cart
curl -X GET https://api.com/cart \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Market: us"

# 4. Logout
curl -X POST https://api.com/auth/logout \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-Market: us"

# 5. Login again (get NEW token)
curl -X POST https://api.com/auth/verify-code \
  -H "Content-Type: application/json" \
  -H "X-Market: us" \
  -d '{"phone": "+13128059851", "verification_code": "654321"}'

# Save the NEW access_token

# 6. Check cart with NEW token
curl -X GET https://api.com/cart \
  -H "Authorization: Bearer NEW_TOKEN" \
  -H "X-Market: us"

# ✅ Cart items still there!
```

---

## 🎯 Common Scenarios

### Scenario 1: User adds items, logs out, logs back in

**Result**: ✅ Cart items preserved (linked to user_id in database)

### Scenario 2: Token expires while shopping

**Result**: ✅ Cart items saved, user re-logins, continues shopping

### Scenario 3: User closes app for a week

**Result**: ✅ Cart items still there when they return

### Scenario 4: User switches devices

**Result**: ✅ Cart syncs (same phone number → same user_id)

---

## ⚠️ Common Mistakes to Avoid

### ❌ DON'T: Store user data in frontend state only

```javascript
// ❌ WRONG
const [cart, setCart] = useState([]);
// Cart lost when app closes!
```

### ✅ DO: Always fetch from backend

```javascript
// ✅ CORRECT
const cart = await fetch("/cart", {
  headers: { Authorization: `Bearer ${token}` },
});
// Cart always from database!
```

### ❌ DON'T: Try to store token in database

```python
# ❌ WRONG
class User:
    access_token = Column(String)  # Don't do this!
```

### ✅ DO: Use JWT + is_active flag

```python
# ✅ CORRECT
class User:
    is_active = Column(Boolean)  # Controls session!
```

---

## 🔑 Key Takeaways

1. **JWT Token** = Temporary key (30 min), contains `user_id`
2. **Database** = Permanent storage, links everything via `user_id`
3. **is_active** = Session control flag
4. **Frontend** = Stores token, sends with every request
5. **Backend** = Decodes token → gets `user_id` → queries database

---

## 📚 Full Documentation

Read [`SESSION_MANAGEMENT_EXPLAINED.md`](./SESSION_MANAGEMENT_EXPLAINED.md) for detailed explanation.

---

## ✅ You're Ready!

Your system is **correctly implemented** and follows **industry best practices**!

Just implement the frontend part (storing/sending token) and you're good to go! 🚀
