# 🚀 Run Integration Tests - Quick Start

**Ready to test Cart & Wishlist APIs!**

---

## ⚡ Quick Commands

### 1. Install Dependencies (if needed)

```bash
pip install requests
```

### 2. Run Tests

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 test_cart_wishlist_integration.py
```

---

## 🎯 What Will Be Tested

| API                | Endpoints             | Status              |
| ------------------ | --------------------- | ------------------- |
| **Wishlist**       | 5 stateless endpoints | ✅ Ready            |
| **Cart (New)**     | 5 stateless endpoints | ✅ Ready            |
| **Cart (Legacy)**  | 6 JWT endpoints       | ✅ Ready (optional) |
| **Error Handling** | 3 error scenarios     | ✅ Ready            |

**Total:** Up to 19 endpoint tests!

---

## 📝 You'll Need

1. **Valid user_id** (e.g., 19)
2. **Valid product_id** (e.g., 1)
3. **Valid sku_id** (e.g., 1)

**Where to find them:**

```bash
# SSH into Railway or connect to your database
SELECT id FROM users LIMIT 1;      # Get user_id
SELECT id FROM products LIMIT 1;   # Get product_id
SELECT id FROM skus LIMIT 1;       # Get sku_id
```

---

## 🎬 Interactive Test Flow

When you run the script, you'll see:

```
🔧 CONFIGURATION
======================================================================
Use local server? [y/N]: N
Using: https://marquebackend-production.up.railway.app/api/v1
Enter test user_id (default: 19): 19
Enter test product_id (default: 1): 1
Enter test sku_id (default: 1): 1

======================================================================
  🧪 CART & WISHLIST INTEGRATION TESTS
======================================================================

⚠️  Press Enter to start tests (Ctrl+C to cancel)...

[Tests will run automatically]

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

## 🔍 What Gets Tested

### ✅ Wishlist Flow

1. Get empty wishlist
2. Add product → Verify added
3. Remove product → Verify removed
4. Clear wishlist → Verify empty

### ✅ Cart Flow (Stateless)

1. Get empty cart
2. Add SKU → Verify added
3. Update quantity → Verify updated
4. Remove item → Verify removed
5. Clear cart → Verify empty

### ✅ Cart Flow (JWT - Optional)

Same as above but using JWT tokens

### ✅ Error Handling

1. Invalid user_id → 404
2. Invalid product_id → 404
3. Missing field → 422

---

## 💡 Pro Tips

### Test Locally First

```bash
# Terminal 1: Start local server
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 -m uvicorn src.app_01.main:app --reload --port 8000

# Terminal 2: Run tests
python3 test_cart_wishlist_integration.py
# Choose "y" for local server
```

### Skip JWT Tests

```
Test legacy JWT endpoints? [y/N]: N
```

This skips SMS verification and JWT tests.

### Use Real Data

Update test IDs to use actual data from your database for more realistic testing.

---

## 📊 Expected Results

All tests should **PASS** if:

- ✅ Backend is running
- ✅ Database has test data
- ✅ All endpoints are correctly implemented
- ✅ No breaking changes in API

---

## 🐛 If Tests Fail

### 1. Check Backend Status

```bash
curl https://marquebackend-production.up.railway.app/health
```

### 2. Verify Test Data

```bash
# Check if user exists
curl -X POST https://marquebackend-production.up.railway.app/api/v1/wishlist/get \
  -H "Content-Type: application/json" \
  -d '{"user_id": 19}'
```

### 3. Check Backend Logs

Look for errors in Railway logs or terminal output.

---

## ✅ Success = Ready for Production!

When all tests pass:

1. ✅ Wishlist API is working
2. ✅ Cart API (stateless) is working
3. ✅ Cart API (JWT) is working
4. ✅ Error handling is correct

**You're ready to deploy and use the new APIs!** 🎉

---

## 📚 Full Documentation

- **Complete Guide:** `INTEGRATION_TESTING_GUIDE.md`
- **Cart API Update:** `CART_API_UPDATED_TO_STATELESS.md`
- **Backend Audit:** `BACKEND_API_AUDIT_REPORT.md`

---

## 🚀 Let's Test!

```bash
python3 test_cart_wishlist_integration.py
```

**Good luck!** 🍀
