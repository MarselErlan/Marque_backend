# 🧪 Integration Testing Guide - Cart & Wishlist APIs

**Date:** October 25, 2025  
**Purpose:** Test stateless Cart and Wishlist APIs

---

## 📋 What Gets Tested

### ✅ **Wishlist API** (5 endpoints)

1. Get Wishlist - `POST /wishlist/get`
2. Add to Wishlist - `POST /wishlist/add`
3. Get Wishlist (verify item added) - `POST /wishlist/get`
4. Remove from Wishlist - `POST /wishlist/remove`
5. Clear Wishlist - `POST /wishlist/clear`

### ✅ **Cart API - Stateless** (5 endpoints)

1. Get Cart - `POST /cart/get`
2. Add to Cart - `POST /cart/add`
3. Update Cart Item - `POST /cart/update`
4. Remove from Cart - `POST /cart/remove`
5. Clear Cart - `POST /cart/clear`

### ✅ **Cart API - Legacy JWT** (6 endpoints - Optional)

1. Get Cart - `GET /cart/` (JWT)
2. Add to Cart - `POST /cart/items` (JWT)
3. Get Cart Items - `GET /cart/items` (JWT)
4. Update Cart Item - `PUT /cart/items/{id}` (JWT)
5. Delete Cart Item - `DELETE /cart/items/{id}` (JWT)
6. Clear Cart - `DELETE /cart/` (JWT)

### ✅ **Error Handling** (3 scenarios)

1. Invalid user_id → 404
2. Invalid product_id → 404
3. Missing required field → 422

---

## 🚀 Quick Start

### Step 1: Install Requirements

```bash
pip install requests
```

### Step 2: Configure Test Data

Open `test_cart_wishlist_integration.py` and update:

```python
TEST_USER_ID = 19       # Your test user ID
TEST_PRODUCT_ID = 1     # A valid product ID in your database
TEST_SKU_ID = 1         # A valid SKU ID in your database
```

### Step 3: Run Tests

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 test_cart_wishlist_integration.py
```

---

## 📝 Interactive Prompts

The test script will ask you:

### 1. **Server Selection**

```
Use local server? [y/N]:
```

- `y` → Test against `http://localhost:8000`
- `N` → Test against production (Railway)

### 2. **Test User ID**

```
Enter test user_id (default: 19):
```

Enter a valid user_id from your database

### 3. **Test Product ID**

```
Enter test product_id (default: 1):
```

Enter a valid product_id

### 4. **Test SKU ID**

```
Enter test sku_id (default: 1):
```

Enter a valid sku_id

### 5. **JWT Tests (Optional)**

```
Test legacy JWT endpoints? (requires SMS verification) [y/N]:
```

- `y` → Will prompt for phone number and SMS code
- `N` → Skip JWT tests

---

## 📊 Example Output

```
======================================================================
  🧪 CART & WISHLIST INTEGRATION TESTS
======================================================================

📍 Testing against: https://marquebackend-production.up.railway.app/api/v1
👤 Test User ID: 19
📦 Test Product ID: 1
🏷️  Test SKU ID: 1

======================================================================
  WISHLIST API TESTS (Stateless)
======================================================================

🧪 TEST: 1. Get Wishlist (should be empty or existing)
----------------------------------------------------------------------

📤 Request: POST https://marquebackend-production.up.railway.app/api/v1/wishlist/get
📦 Body: {
  "user_id": 19
}

📥 Response: 200
📄 Data: {
  "id": 1,
  "user_id": 19,
  "items": []
}

✅ SUCCESS: Get wishlist works!
📊 Initial wishlist has 0 items

🧪 TEST: 2. Add Product to Wishlist
----------------------------------------------------------------------

📤 Request: POST https://marquebackend-production.up.railway.app/api/v1/wishlist/add
📦 Body: {
  "user_id": 19,
  "product_id": 1
}

📥 Response: 200
📄 Data: {
  "id": 1,
  "user_id": 19,
  "items": [
    {
      "id": 1,
      "product": {
        "id": "1",
        "name": "Product Name",
        "price": 29.99
      }
    }
  ]
}

✅ SUCCESS: Add to wishlist works!
📊 Wishlist now has 1 items

[... more tests ...]

======================================================================
  TEST SUMMARY
======================================================================

✅ PASSED    - wishlist
✅ PASSED    - cart_stateless
✅ PASSED    - cart_jwt
✅ PASSED    - error_handling

======================================================================
  TOTAL: 4/4 test suites passed
======================================================================

🎉 All tests passed! APIs are working correctly!
```

---

## 🔍 What Each Test Does

### Wishlist Tests

```python
# Test 1: Get empty wishlist
POST /wishlist/get
Body: {"user_id": 19}
Expected: 200 OK, empty items array

# Test 2: Add product to wishlist
POST /wishlist/add
Body: {"user_id": 19, "product_id": 1}
Expected: 200 OK, wishlist with 1 item

# Test 3: Verify item added
POST /wishlist/get
Body: {"user_id": 19}
Expected: 200 OK, wishlist with 1 item

# Test 4: Remove product
POST /wishlist/remove
Body: {"user_id": 19, "product_id": 1}
Expected: 200 OK, empty wishlist

# Test 5: Clear wishlist
POST /wishlist/clear
Body: {"user_id": 19}
Expected: 200 OK, empty wishlist
```

### Cart Tests (Stateless)

```python
# Test 1: Get empty cart
POST /cart/get
Body: {"user_id": 19}
Expected: 200 OK, empty items array

# Test 2: Add SKU to cart
POST /cart/add
Body: {"user_id": 19, "sku_id": 1, "quantity": 2}
Expected: 200 OK, cart with 1 item, quantity 2

# Test 3: Verify item added
POST /cart/get
Body: {"user_id": 19}
Expected: 200 OK, cart with 1 item

# Test 4: Update quantity
POST /cart/update
Body: {"user_id": 19, "cart_item_id": 1, "quantity": 5}
Expected: 200 OK, cart item quantity updated to 5

# Test 5: Remove item
POST /cart/remove
Body: {"user_id": 19, "cart_item_id": 1}
Expected: 200 OK, empty cart

# Test 6: Clear cart
POST /cart/clear
Body: {"user_id": 19}
Expected: 200 OK, empty cart
```

### Error Handling Tests

```python
# Test 1: Invalid user_id
POST /wishlist/get
Body: {"user_id": 999999}
Expected: 404 Not Found

# Test 2: Invalid product_id
POST /wishlist/add
Body: {"user_id": 19, "product_id": 999999}
Expected: 404 Not Found

# Test 3: Missing user_id
POST /cart/add
Body: {"sku_id": 1, "quantity": 1}
Expected: 422 Unprocessable Entity
```

---

## 🐛 Troubleshooting

### Issue 1: Connection Error

```
Failed to connect to server
```

**Solution:**

- Check if backend is running
- Verify BASE_URL is correct
- Check network connection

```bash
# Test connection
curl https://marquebackend-production.up.railway.app/health
```

### Issue 2: 404 User Not Found

```
❌ ERROR: User not found
```

**Solution:**

- Use a valid user_id from your database
- Check database has test user

```sql
-- Check users in database
SELECT id, phone_number FROM users LIMIT 5;
```

### Issue 3: 404 Product Not Found

```
❌ ERROR: Product not found
```

**Solution:**

- Use a valid product_id
- Check database has products

```sql
-- Check products in database
SELECT id, title FROM products LIMIT 5;
```

### Issue 4: 404 SKU Not Found

```
❌ ERROR: SKU not found
```

**Solution:**

- Use a valid sku_id
- Check database has SKUs

```sql
-- Check SKUs in database
SELECT id, product_id FROM skus LIMIT 5;
```

---

## 📈 Advanced Testing

### Test Against Local Server

```bash
# Start local server first
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 -m uvicorn src.app_01.main:app --reload --port 8000

# In another terminal, run tests
python3 test_cart_wishlist_integration.py
# Choose "y" when asked "Use local server?"
```

### Test with Custom Data

Edit `test_cart_wishlist_integration.py`:

```python
# Use specific test data
TEST_USER_ID = 42
TEST_PRODUCT_ID = 123
TEST_SKU_ID = 456
```

### Test Multiple Users

Run the script multiple times with different user_ids:

```bash
# User 1
python3 test_cart_wishlist_integration.py
# Enter: 19

# User 2
python3 test_cart_wishlist_integration.py
# Enter: 20
```

---

## 🔄 Continuous Integration

### Add to CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.9"
      - name: Install dependencies
        run: pip install requests
      - name: Run integration tests
        run: python3 test_cart_wishlist_integration.py
        env:
          TEST_USER_ID: 19
          TEST_PRODUCT_ID: 1
          TEST_SKU_ID: 1
```

---

## 📋 Checklist

Before running tests:

- [ ] Backend is deployed and running
- [ ] Database has test data (users, products, SKUs)
- [ ] You have valid test user_id, product_id, sku_id
- [ ] Python 3.x is installed
- [ ] `requests` library is installed

After tests pass:

- [ ] All wishlist endpoints work ✅
- [ ] All cart stateless endpoints work ✅
- [ ] Legacy JWT endpoints work (if tested) ✅
- [ ] Error handling is correct ✅
- [ ] Ready for production! 🚀

---

## 📞 Support

If tests fail:

1. Check error messages in console
2. Verify test data (user_id, product_id, sku_id) exists
3. Check backend logs
4. Review BACKEND_API_AUDIT_REPORT.md
5. Review CART_API_UPDATED_TO_STATELESS.md

---

## ✅ Success Criteria

Tests are successful when:

- ✅ All test suites pass (4/4 or 3/3 without JWT)
- ✅ No 500 errors
- ✅ 404 errors only for invalid data
- ✅ 422 errors only for missing fields
- ✅ Cart and wishlist operations complete correctly

---

**Created:** October 25, 2025  
**Status:** ✅ Ready to test!
