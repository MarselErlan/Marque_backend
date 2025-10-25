# 🔍 Backend API Audit Report - Wishlist, Cart & Orders

**Date:** October 25, 2025  
**Status:** ✅ **PARTIALLY COMPLIANT** - Needs Cart API Update

---

## 📊 Executive Summary

| API          | Status              | Uses `user_id`    | Uses `product_id`     | Notes                                 |
| ------------ | ------------------- | ----------------- | --------------------- | ------------------------------------- |
| **Wishlist** | ✅ **PERFECT**      | ✅ Yes            | ✅ Yes                | **Stateless API - Fully updated!**    |
| **Cart**     | ⚠️ **NEEDS UPDATE** | ❌ No (uses JWT)  | ❌ No (uses `sku_id`) | Still using JWT token auth            |
| **Orders**   | ✅ **CORRECT**      | ✅ Yes (from JWT) | N/A                   | Orders use JWT (correct for security) |

---

## 1️⃣ Wishlist API - ✅ PERFECT (Stateless)

### ✅ **Status: FULLY UPDATED**

The wishlist API has been **completely updated** to use **stateless API** with `user_id` and `product_id`.

### 📁 File: `src/app_01/routers/wishlist_router.py`

### ✅ All Endpoints Accept `user_id` and `product_id`:

```python
# ✅ Get Wishlist
@router.post("/get", response_model=WishlistSchema)
def get_wishlist(request: GetWishlistRequest, db: Session = Depends(get_db)):
    """Get wishlist for a specific user"""
    return get_wishlist_by_user_id(request.user_id, db)

# ✅ Add to Wishlist
@router.post("/add", response_model=WishlistSchema)
def add_to_wishlist(request: AddToWishlistRequest, db: Session = Depends(get_db)):
    """Add product to user's wishlist"""
    # Verify user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    # Verify product exists
    product = db.query(Product).filter(Product.id == request.product_id).first()
    # Create wishlist item
    wishlist_item = WishlistItem(wishlist_id=wishlist.id, product_id=request.product_id)

# ✅ Remove from Wishlist
@router.post("/remove", response_model=WishlistSchema)
def remove_from_wishlist(request: RemoveFromWishlistRequest, db: Session = Depends(get_db)):
    """Remove product from user's wishlist"""
    # Uses request.user_id and request.product_id

# ✅ Clear Wishlist
@router.post("/clear", response_model=WishlistSchema)
def clear_wishlist(request: ClearWishlistRequest, db: Session = Depends(get_db)):
    """Clear all items from user's wishlist"""
    # Uses request.user_id
```

### ✅ Schemas (src/app_01/schemas/wishlist.py):

```python
class AddToWishlistRequest(BaseModel):
    user_id: int          # ✅ Accepts user_id
    product_id: int       # ✅ Accepts product_id

class RemoveFromWishlistRequest(BaseModel):
    user_id: int          # ✅ Accepts user_id
    product_id: int       # ✅ Accepts product_id

class GetWishlistRequest(BaseModel):
    user_id: int          # ✅ Accepts user_id

class ClearWishlistRequest(BaseModel):
    user_id: int          # ✅ Accepts user_id
```

### 🎯 **Wishlist API Verdict:** ✅ **100% COMPLIANT**

All wishlist endpoints accept `user_id` and `product_id` as required!

---

## 2️⃣ Cart API - ⚠️ **NEEDS UPDATE** (Still using JWT)

### ⚠️ **Status: NOT STATELESS - Still uses JWT token authentication**

The cart API is still using **JWT token authentication** instead of accepting `user_id` directly.

### 📁 File: `src/app_01/routers/cart_router.py`

### ❌ Current Implementation (JWT-based):

```python
# ❌ Get Cart - Uses JWT token
@router.get("/", response_model=CartSchema)
def get_cart(
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)  # ❌ JWT
):
    user_id = current_user.user_id  # Extracted from JWT token

# ❌ Add to Cart - Uses JWT token + sku_id (not product_id)
@router.post("/items", response_model=CartSchema)
def add_to_cart(
    request: AddToCartRequest,  # Contains sku_id, quantity
    db: Session = Depends(get_db),
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)  # ❌ JWT
):
    user_id = current_user.user_id  # Extracted from JWT token
```

### ❌ Cart Schema (src/app_01/schemas/cart.py):

```python
class AddToCartRequest(BaseModel):
    sku_id: int           # ❌ Uses sku_id (not product_id)
    quantity: int = 1
    # ❌ Missing: user_id
```

### 🔧 **What Needs to Change:**

#### Option 1: **Make Cart Stateless (Like Wishlist)**

Update cart to accept `user_id` directly:

```python
# ✅ Proposed: Stateless Cart API
class AddToCartRequest(BaseModel):
    user_id: int          # ✅ Add user_id
    product_id: int       # ✅ Change from sku_id to product_id (or keep sku_id)
    quantity: int = 1

@router.post("/add", response_model=CartSchema)
def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db)):
    """Add product to cart (stateless)"""
    user = db.query(User).filter(User.id == request.user_id).first()
    # ... rest of logic
```

#### Option 2: **Keep Cart JWT-based (Recommended for Security)**

**Why?** Cart operations are more sensitive (involve purchases) and should be protected by JWT.

In this case, **no changes needed** - cart correctly uses JWT authentication.

### 🎯 **Cart API Verdict:** ⚠️ **Decision Required**

**Question:** Should cart be **stateless** (like wishlist) or **JWT-protected** (like orders)?

**Recommendation:** **Keep JWT-protected** for better security, since cart leads to payment.

---

## 3️⃣ Orders API - ✅ CORRECT (JWT-protected)

### ✅ **Status: CORRECT - Uses JWT authentication (appropriate for orders)**

Orders API correctly uses **JWT token authentication** for security.

### 📁 File: `src/app_01/routers/profile_router.py`

### ✅ All Order Endpoints Use JWT + extract `user_id`:

```python
# ✅ Get User Orders
@router.get("/orders")
def get_user_orders(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),  # ✅ JWT
    db: Session = Depends(get_db)
):
    query = db.query(Order).filter(Order.user_id == current_user.user_id)  # ✅ Uses user_id from JWT

# ✅ Get Order Details
@router.get("/orders/{order_id}")
def get_order_details(
    order_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),  # ✅ JWT
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.user_id  # ✅ Uses user_id from JWT
    ).first()

# ✅ Cancel Order
@router.post("/orders/{order_id}/cancel")
def cancel_order(
    order_id: int,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),  # ✅ JWT
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.user_id  # ✅ Uses user_id from JWT
    ).first()
```

### 🎯 **Orders API Verdict:** ✅ **100% CORRECT**

Orders correctly use JWT authentication and extract `user_id` from the token. This is the **right approach** for sensitive operations like viewing/canceling orders.

---

## 📊 Comparison: Wishlist vs Cart vs Orders

| Feature                  | Wishlist         | Cart                  | Orders            |
| ------------------------ | ---------------- | --------------------- | ----------------- |
| **Authentication**       | None (stateless) | JWT token             | JWT token         |
| **Accepts `user_id`**    | ✅ Yes (in body) | ❌ No (from JWT)      | ✅ Yes (from JWT) |
| **Accepts `product_id`** | ✅ Yes           | ❌ No (uses `sku_id`) | N/A               |
| **Security Level**       | Low (public)     | High (protected)      | High (protected)  |
| **Recommended**          | ✅ Stateless OK  | ✅ JWT better         | ✅ JWT correct    |

---

## 🔍 Detailed API Comparison

### Wishlist (Stateless):

```javascript
// ✅ No JWT required
POST /api/v1/wishlist/add
Body: {
  "user_id": 19,
  "product_id": 123
}
```

### Cart (JWT-protected):

```javascript
// ✅ JWT required in header
POST /api/v1/cart/items
Headers: {
  "Authorization": "Bearer <token>"
}
Body: {
  "sku_id": 456,
  "quantity": 1
}
// user_id extracted from JWT token
```

### Orders (JWT-protected):

```javascript
// ✅ JWT required in header
GET /api/v1/profile/orders
Headers: {
  "Authorization": "Bearer <token>"
}
// user_id extracted from JWT token
```

---

## 🎯 Recommendations

### ✅ **Keep As Is:**

1. **Wishlist** - Stateless API is perfect ✅
2. **Orders** - JWT authentication is correct ✅

### ⚠️ **Decision Required: Cart API**

**Option A: Make Cart Stateless (like Wishlist)**

**Pros:**

- ✅ Consistent with wishlist API
- ✅ Easier frontend integration
- ✅ No token management needed

**Cons:**

- ❌ Less secure (anyone with `user_id` can modify cart)
- ❌ No authentication verification
- ❌ Potential for abuse

**Option B: Keep Cart JWT-protected (RECOMMENDED)**

**Pros:**

- ✅ More secure (requires valid login)
- ✅ Prevents unauthorized cart modifications
- ✅ Consistent with orders API (both involve purchases)

**Cons:**

- ⚠️ Requires token management on frontend
- ⚠️ Inconsistent with wishlist API

---

## 🚀 If You Want to Update Cart to Stateless:

### Step 1: Update Cart Schema

```python
# File: src/app_01/schemas/cart.py

class AddToCartRequest(BaseModel):
    user_id: int          # ✅ Add this
    sku_id: int
    quantity: int = 1

class RemoveFromCartRequest(BaseModel):
    user_id: int          # ✅ Add this
    cart_item_id: int

class GetCartRequest(BaseModel):
    user_id: int          # ✅ Add this

class ClearCartRequest(BaseModel):
    user_id: int          # ✅ Add this
```

### Step 2: Update Cart Router

```python
# File: src/app_01/routers/cart_router.py

@router.post("/get", response_model=CartSchema)
def get_cart(request: GetCartRequest, db: Session = Depends(get_db)):
    """Get cart for specific user (stateless)"""
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = db.query(Cart).filter(Cart.user_id == request.user_id).first()
    # ... rest of logic

@router.post("/add", response_model=CartSchema)
def add_to_cart(request: AddToCartRequest, db: Session = Depends(get_db)):
    """Add to cart (stateless)"""
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    cart = db.query(Cart).filter(Cart.user_id == request.user_id).first()
    # ... rest of logic
```

### Step 3: Keep Legacy Endpoints

```python
# Keep old JWT endpoints for backward compatibility
@router.get("/", response_model=CartSchema)
def get_cart_legacy(db: Session = Depends(get_db),
                    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)):
    """Legacy JWT-based cart endpoint"""
    return get_cart(GetCartRequest(user_id=current_user.user_id), db)
```

---

## 📋 Summary

### ✅ What's Working:

- **Wishlist API** - 100% stateless with `user_id` + `product_id` ✅
- **Orders API** - Correctly JWT-protected with `user_id` from token ✅

### ⚠️ What Needs Decision:

- **Cart API** - Currently JWT-protected, but could be made stateless like wishlist

### 🎯 Final Recommendation:

**Option 1 (RECOMMENDED):** **Keep cart JWT-protected**

- More secure
- Consistent with orders
- Better for e-commerce

**Option 2:** **Make cart stateless**

- Consistent with wishlist
- Easier frontend
- Less secure

**Your Choice!** 🤔

---

## 📞 Next Steps

1. **Decide:** Should cart be stateless or JWT-protected?
2. **Update:** If stateless, follow the update steps above
3. **Test:** Verify all APIs work with frontend
4. **Deploy:** Push changes to production

---

**Created:** October 25, 2025  
**Status:** ✅ Wishlist perfect, ⚠️ Cart needs decision, ✅ Orders correct
