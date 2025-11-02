# Manual End-to-End Testing Guide

**Purpose:** Verify frontend can create orders that save to the database

---

## 🚀 Quick Test Steps

### 1. Start Backend

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
uvicorn src.app_01.main:app --reload --port 8000
```

**Verify:** Open http://localhost:8000/docs - you should see FastAPI documentation

---

### 2. Start Frontend

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/marque_frontend
npm run dev
```

**Verify:** Open http://localhost:3000 - you should see the homepage

---

### 3. Test Order Creation Flow

#### A. Login/Register

1. Go to http://localhost:3000
2. Click "Login" or "Register"
3. Use phone: `+996700123456`
4. Complete verification

#### B. Add Products to Cart

1. Browse products
2. Click on a product
3. Select size and color
4. Click "Add to Cart"
5. Repeat for 1-2 more products

#### C. Go to Cart

1. Click cart icon in header
2. Verify items are displayed
3. Check subtotal calculation

#### D. Create Order

1. Fill in order form:
   - **Name:** Your Name
   - **Phone:** +996700123456
   - **Address:** Юнусалиева, 40, кв. 10
   - **City:** Бишкек
   - **Payment:** Card or Cash
2. Click "Place Order" / "Оформить заказ"
3. Wait for success message
4. Note the **order number** (e.g., #1001)

---

### 4. Verify Order in Database

Run this Python script to check:

```python
python3 << 'EOF'
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.orders.order import Order
from src.app_01.models.orders.order_item import OrderItem

SessionLocal = db_manager.get_session_factory(Market.KG)
db = SessionLocal()

# Get all orders
orders = db.query(Order).order_by(Order.created_at.desc()).limit(5).all()

print("\n🔍 Recent Orders in Database:")
print("="*60)

for order in orders:
    print(f"\n📦 Order #{order.order_number}")
    print(f"   Customer: {order.customer_name}")
    print(f"   Phone: {order.customer_phone}")
    print(f"   Address: {order.delivery_address}")
    print(f"   Payment: {order.payment_method}")
    print(f"   Status: {order.status.value}")
    print(f"   Total: {order.total_amount} {order.currency}")
    print(f"   Created: {order.created_at}")

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    print(f"   Items ({len(items)}):")
    for item in items:
        print(f"      - {item.product_name} ({item.size}/{item.color}) x{item.quantity} = {item.total_price} KGS")

db.close()
EOF
```

---

## ✅ What to Verify

### Frontend

- [ ] Can login/register
- [ ] Can add products to cart
- [ ] Cart updates correctly
- [ ] Can fill order form
- [ ] Order submission works
- [ ] Success message shows order number
- [ ] Cart clears after order

### Backend API

- [ ] POST /api/v1/orders/create responds with 200
- [ ] Returns order number
- [ ] Returns order details
- [ ] Includes order items

### Database

- [ ] Order record exists
- [ ] Has correct customer info
- [ ] Has correct address
- [ ] Has payment_method saved
- [ ] Order items are linked
- [ ] Stock was reduced
- [ ] Cart was cleared

---

## 🔧 Troubleshooting

### Backend Not Starting

```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
pkill -f uvicorn

# Start again
uvicorn src.app_01.main:app --reload --port 8000
```

### Frontend Not Starting

```bash
# Check if port is in use
lsof -i :3000

# Kill existing process
kill -9 $(lsof -t -i:3000)

# Start again
npm run dev
```

### Database Connection Error

```bash
# Check database is running
psql -h localhost -U your_user -d marque_kg

# Check .env file has correct DATABASE_URL
cat .env | grep DATABASE_URL
```

### No Orders in Database

1. Check backend logs for errors
2. Verify authentication token is valid
3. Check cart has items before checkout
4. Verify SKU has stock available

---

## 📊 Expected Results

### Successful Order Creation:

```
✅ Frontend shows: "Order placed successfully! Order #1001"
✅ Backend returns: 200 OK with order data
✅ Database contains: Order record with items
✅ Cart is cleared
✅ Stock is reduced
```

### Order Record Should Include:

- ✅ order_number: "#1001"
- ✅ customer_name: "Your Name"
- ✅ customer_phone: "+996700123456"
- ✅ delivery_address: "Юнусалиева, 40, кв. 10"
- ✅ payment_method: "card" or "cash"
- ✅ status: "pending"
- ✅ subtotal: Calculated amount
- ✅ shipping_cost: 0 or 150 KGS
- ✅ total_amount: Subtotal + Shipping
- ✅ currency: "KGS"
- ✅ Order items with product details

---

## 🎯 Quick Verification Command

```bash
# One command to check latest order
cd /Users/macbookpro/M4_Projects/Prodaction/Marque && python -c "
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.orders.order import Order
from src.app_01.models.orders.order_item import OrderItem

SessionLocal = db_manager.get_session_factory(Market.KG)
db = SessionLocal()

order = db.query(Order).order_by(Order.created_at.desc()).first()

if order:
    print(f'✅ Latest Order: {order.order_number}')
    print(f'   Customer: {order.customer_name}')
    print(f'   Payment: {order.payment_method}')
    print(f'   Total: {order.total_amount} {order.currency}')
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).count()
    print(f'   Items: {items}')
else:
    print('❌ No orders found')

db.close()
"
```

---

## 🚀 Ready to Test!

1. Start both backend and frontend
2. Create an order through the UI
3. Run verification script
4. Confirm order is in database

**Expected time:** 3-5 minutes

---

**Status:** Ready for testing  
**Date:** November 2, 2025
