# 🧪 Run Address API Test

## Quick Start

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
python3 test_addresses_live.py
```

## What This Test Does

1. **Authenticates** - Uses your phone number (+13128059851)
2. **Gets Addresses** - Shows existing addresses
3. **Creates Address** - Creates a new test address
4. **Verifies in DB** - Directly queries the database to confirm
5. **Gets Addresses Again** - Shows the new address in the list
6. **Updates Address** - Changes the title and makes it default
7. **Optionally Deletes** - Asks if you want to clean up

## Expected Flow

```
🧪 LIVE ADDRESS API TEST
==========================================================

STEP 1: AUTHENTICATION
==========================================================
ℹ️  Sending verification code to +13128059851...
✅ Verification code sent!

📱 Enter the verification code from SMS: 729724

ℹ️  Verifying code...
✅ Authentication successful!
ℹ️  User ID: 19
ℹ️  Market: us
ℹ️  Token: eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...

==========================================================
STEP 2: GET ADDRESSES (Initial State)
==========================================================
Status Code: 200
✅ Found 0 existing addresses

==========================================================
STEP 3: CREATE NEW ADDRESS
==========================================================
ℹ️  Creating address with data:
{
  "title": "Test Address - Live Test",
  "full_address": "ул. Тестовая, 123, кв. 45, Бишкек",
  "street": "ул. Тестовая",
  "building": "123",
  "apartment": "45",
  "city": "Бишкек",
  "postal_code": "720000",
  "country": "Kyrgyzstan",
  "is_default": false
}

Status Code: 201
✅ Address created with ID: 1

==========================================================
STEP 4: VERIFY IN DATABASE
==========================================================
ℹ️  Connecting to US database...
✅ Address found in database!

📊 Database Record:
   ID: 1
   User ID: 19
   Title: Test Address - Live Test
   Full Address: ул. Тестовая, 123, кв. 45, Бишкек
   Street: ул. Тестовая
   Building: 123
   Apartment: 45
   City: Бишкек
   Postal Code: 720000
   Country: Kyrgyzstan
   Is Default: False
   Is Active: True
   Created At: 2025-10-23 14:30:00

==========================================================
STEP 5: GET ADDRESSES (After Creation)
==========================================================
Status Code: 200
✅ Found 1 addresses

Addresses List:
  • ID 1: Test Address - Live Test
    ул. Тестовая, 123, кв. 45, Бишкек
    Default: False

==========================================================
STEP 6: UPDATE ADDRESS (ID: 1)
==========================================================
ℹ️  Updating address with:
{
  "title": "Updated Test Address",
  "is_default": true
}

Status Code: 200
✅ Address updated successfully!

==========================================================
STEP 7: DELETE ADDRESS (ID: 1)
==========================================================
🗑️  Delete test address 1? (y/n): y

Status Code: 200
✅ Address deleted successfully!

==========================================================
📊 TEST SUMMARY
==========================================================
✅ Authentication: SUCCESS
✅ GET addresses (initial): SUCCESS (0 found)
✅ CREATE address: SUCCESS
✅ Verify in database: SUCCESS
✅ GET addresses (after): SUCCESS (1 found)
✅ UPDATE address: SUCCESS

🎉 ADDRESS ID 1 WAS CREATED IN DATABASE!
   User ID: 19
   Market: us
   Phone: +13128059851
```

## What You'll See

### ✅ Success Indicators

- **201 Created** - Address created successfully
- **Database record** - Confirms it's actually in the DB
- **Address appears in GET** - Confirms API returns it

### ❌ If Something Fails

- **401 Unauthorized** - Token issue (re-run test)
- **500 Server Error** - Check server logs
- **Database error** - Check DATABASE_URL env vars

## Check Database Manually

After creating an address, you can check it manually:

```sql
-- For US market
SELECT * FROM user_addresses WHERE user_id = 19;

-- For KG market
SELECT * FROM user_addresses WHERE user_id = YOUR_USER_ID;
```

## Server Must Be Running

Before running the test, make sure the server is running:

```bash
# Start server (if not already running)
python3 -m uvicorn src.app_01.main:app --reload --port 8000

# In another terminal, run the test
python3 test_addresses_live.py
```

## Environment Variables

Make sure you have these set in your `.env` file:

```bash
# US Market Database
US_DATABASE_URL=postgresql://postgres:password@localhost:5432/marque_db_us

# KG Market Database
KG_DATABASE_URL=postgresql://postgres:password@localhost:5432/marque_db_kg

# Or use Railway production URLs
US_DATABASE_URL=postgresql://postgres:...@containers-us-west-123.railway.app:5432/railway
KG_DATABASE_URL=postgresql://postgres:...@containers-us-west-123.railway.app:5432/railway
```

## Testing All Endpoints

After you verify addresses work, you can test other endpoints:

### Payment Methods

```bash
# Similar test for payment methods
# test_payment_methods_live.py (to be created)
```

### Orders

```bash
# Test orders (requires existing orders in DB)
# test_orders_live.py (to be created)
```

### Notifications

```bash
# Test notifications
# test_notifications_live.py (to be created)
```

## Next Steps

1. ✅ **Run this test** - Verify addresses work
2. ✅ **Check database** - See the actual record
3. ✅ **Test frontend** - Connect your frontend to these APIs
4. ✅ **Deploy** - Push to Railway when ready

---

**Ready?** Just run:

```bash
python3 test_addresses_live.py
```
