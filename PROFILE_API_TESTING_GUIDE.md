# 🧪 Profile API Testing Guide

**How to test your complete profile APIs**

---

## 🚀 Quick Start Testing

### Option 1: Automatic Test Script

```bash
# Start the server in one terminal
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 -m uvicorn src.app_01.main:app --reload --port 8000

# In another terminal, run the test script
python3 test_profile_apis.py
```

The script will:

1. Ask for your phone number
2. Send SMS verification code
3. Ask you to enter the code
4. Test all profile endpoints automatically
5. Show you the results

---

## Option 2: Manual Testing with Postman

### Step 1: Start Server

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 -m uvicorn src.app_01.main:app --reload --port 8000
```

Visit http://localhost:8000/docs to see all endpoints.

---

### Step 2: Get Authentication Token

**1. Send Verification Code**

```http
POST http://localhost:8000/api/v1/auth/send-verification
Content-Type: application/json

{
  "phone": "+13128059851"
}
```

**2. Verify Code**

```http
POST http://localhost:8000/api/v1/auth/verify-code
Content-Type: application/json

{
  "phone": "+13128059851",
  "verification_code": "YOUR_CODE_HERE"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Phone verified successfully",
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 19,
    "name": "User +13128059851",
    "phone": "+13128059851"
  },
  "market": "us"
}
```

**Copy the `access_token` value!**

---

### Step 3: Test Profile Endpoints

For all requests below, add this header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN_HERE
```

---

#### ✅ Test 1: Get User Profile

```http
GET http://localhost:8000/api/v1/auth/profile
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**

```json
{
  "id": 19,
  "phone_number": "+13128059851",
  "full_name": "Анна Ахматова",
  "is_verified": true,
  "market": "us",
  "language": "en",
  "country": "United States"
}
```

**✅ PASS:** Status code 200, user data returned  
**❌ FAIL:** Status code 401, unauthorized

---

#### ✅ Test 2: Get Addresses

```http
GET http://localhost:8000/api/v1/profile/addresses
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**

```json
{
  "success": true,
  "addresses": [],
  "total": 0
}
```

**✅ PASS:** Status code 200, returns addresses array  
**❌ FAIL:** Status code 401 or 500

---

#### ✅ Test 3: Create Address

```http
POST http://localhost:8000/api/v1/profile/addresses
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "title": "Домашний адрес",
  "full_address": "ул. Юнусалиева, 34, кв. 12, Бишкек",
  "street": "ул. Юнусалиева",
  "building": "34",
  "apartment": "12",
  "city": "Бишкек",
  "postal_code": "720000",
  "country": "Kyrgyzstan",
  "is_default": true
}
```

**Expected Response:**

```json
{
  "success": true,
  "message": "Address created successfully",
  "address": {
    "id": 1,
    "title": "Домашний адрес",
    "full_address": "ул. Юнусалиева, 34, кв. 12, Бишкек",
    "is_default": true
  }
}
```

**✅ PASS:** Status code 201, address created  
**❌ FAIL:** Status code 500, database error

---

#### ✅ Test 4: Get Addresses Again

```http
GET http://localhost:8000/api/v1/profile/addresses
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**

```json
{
  "success": true,
  "addresses": [
    {
      "id": 1,
      "title": "Домашний адрес",
      "full_address": "ул. Юнусалиева, 34, кв. 12, Бишкек",
      "is_default": true
    }
  ],
  "total": 1
}
```

**✅ PASS:** Status code 200, address appears in list  
**❌ FAIL:** Address not in list

---

#### ✅ Test 5: Update Address

```http
PUT http://localhost:8000/api/v1/profile/addresses/1
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "title": "Рабочий адрес"
}
```

**Expected Response:**

```json
{
  "success": true,
  "message": "Address updated successfully",
  "address": {
    "id": 1,
    "title": "Рабочий адрес",
    "is_default": true
  }
}
```

**✅ PASS:** Status code 200, address updated  
**❌ FAIL:** Status code 404, address not found

---

#### ✅ Test 6: Get Payment Methods

```http
GET http://localhost:8000/api/v1/profile/payment-methods
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**

```json
{
  "success": true,
  "payment_methods": [],
  "total": 0
}
```

**✅ PASS:** Status code 200, returns empty array  
**❌ FAIL:** Status code 500

---

#### ✅ Test 7: Create Payment Method

```http
POST http://localhost:8000/api/v1/profile/payment-methods
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "card_number": "4111111111111111",
  "card_holder_name": "ANNA AKHMATOVA",
  "expiry_month": "12",
  "expiry_year": "2028",
  "is_default": true
}
```

**Expected Response:**

```json
{
  "success": true,
  "message": "Payment method added successfully",
  "payment_method": {
    "id": 1,
    "card_type": "visa",
    "card_number_masked": "1111",
    "is_default": true
  }
}
```

**✅ PASS:** Status code 201, payment method created  
**❌ FAIL:** Status code 500

---

#### ✅ Test 8: Get Orders

```http
GET http://localhost:8000/api/v1/profile/orders
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**

```json
{
  "success": true,
  "orders": [],
  "total": 0,
  "has_more": false
}
```

**✅ PASS:** Status code 200, returns orders array  
**❌ FAIL:** Status code 500

---

#### ✅ Test 9: Get Notifications

```http
GET http://localhost:8000/api/v1/profile/notifications
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**

```json
{
  "success": true,
  "notifications": [],
  "total": 0,
  "unread_count": 0
}
```

**✅ PASS:** Status code 200, returns notifications array  
**❌ FAIL:** Status code 500

---

#### ✅ Test 10: Delete Address

```http
DELETE http://localhost:8000/api/v1/profile/addresses/1
Authorization: Bearer YOUR_TOKEN
```

**Expected Response:**

```json
{
  "success": true,
  "message": "Address deleted successfully"
}
```

**✅ PASS:** Status code 200, address deleted  
**❌ FAIL:** Status code 404 or 500

---

## 🎯 Success Criteria

All tests should return:

- ✅ **Status 200/201** - Success
- ✅ **JSON Response** - With proper structure
- ✅ **Data Persistence** - Created data appears in GET requests

---

## 🐛 Troubleshooting

### Error: 401 Unauthorized

**Problem:** Token is missing or invalid  
**Solution:** Get a new token by verifying SMS code again

### Error: 500 Internal Server Error

**Problem:** Database or server error  
**Solution:** Check server logs in terminal:

```bash
# Look for error messages in the server terminal
```

### Error: 404 Not Found

**Problem:** Endpoint doesn't exist or wrong ID  
**Solution:**

- Check endpoint URL spelling
- Check if resource ID exists

### Error: Connection Refused

**Problem:** Server not running  
**Solution:**

```bash
python3 -m uvicorn src.app_01.main:app --reload --port 8000
```

---

## 📊 Test Results Template

Copy this and fill in your results:

```
PROFILE API TEST RESULTS
Date: _______________

✅/❌ Test 1: Get Profile -
✅/❌ Test 2: Get Addresses -
✅/❌ Test 3: Create Address -
✅/❌ Test 4: Get Addresses (after create) -
✅/❌ Test 5: Update Address -
✅/❌ Test 6: Get Payment Methods -
✅/❌ Test 7: Create Payment Method -
✅/❌ Test 8: Get Orders -
✅/❌ Test 9: Get Notifications -
✅/❌ Test 10: Delete Address -

Overall: ___/10 tests passed

Notes:
_________________________________
_________________________________
_________________________________
```

---

## 🚀 Next Steps After Testing

Once all tests pass:

1. ✅ **Deploy to Railway**

   ```bash
   git add .
   git commit -m "feat: Add profile management APIs"
   git push origin main
   ```

2. ✅ **Update Frontend**

   - Use the API endpoints in your frontend code
   - See `PROFILE_API_COMPLETE_GUIDE.md` for examples

3. ✅ **Test Production**
   - Test all endpoints on Railway URL
   - `https://marquebackend-production.up.railway.app/api/v1`

---

**Created:** October 23, 2025  
**Ready to test!** 🎉
