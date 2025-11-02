# Database Connection Flow - Complete Guide

## 📊 Architecture Overview

Your application uses a **Multi-Market Database System** with **2 separate PostgreSQL databases**:

```
┌─────────────────────────────────────────────────────────────────┐
│                     MARQUE APPLICATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐       │
│  │   KG Database    │              │   US Database    │       │
│  │  (Kyrgyzstan)    │              │ (United States)  │       │
│  ├──────────────────┤              ├──────────────────┤       │
│  │ Phone: +996xxx   │              │ Phone: +1xxx     │       │
│  │ Currency: сом    │              │ Currency: $      │       │
│  │ Language: ru     │              │ Language: en     │       │
│  └──────────────────┘              └──────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 1. Configuration Level

### File: `.env` (Environment Variables)

```bash
# Database connection strings
DATABASE_URL_MARQUE_KG=postgresql://user:pass@host:5432/marque_kg_db
DATABASE_URL_MARQUE_US=postgresql://user:pass@host:5432/marque_us_db
```

### File: `src/app_01/core/config.py`

```python
class DatabaseConfig(BaseSettings):
    """Loads database URLs from environment"""
    url_kg: str = os.getenv("DATABASE_URL_MARQUE_KG", "...")
    url_us: str = os.getenv("DATABASE_URL_MARQUE_US", "...")
```

**Purpose:** Store the actual database connection strings.

---

## 🏗️ 2. Database Manager Level

### File: `src/app_01/db/market_db.py`

#### A. Market Enum (Lines 23-26)

```python
class Market(Enum):
    """Supported markets"""
    KG = "kg"  # Kyrgyzstan
    US = "us"  # United States
```

#### B. MarketDatabaseManager Class (Lines 79-153)

```python
class MarketDatabaseManager:
    def __init__(self):
        self.engines: Dict[Market, Any] = {}           # Database engines
        self.session_factories: Dict[Market, Any] = {} # Session factories
        self._initialize_databases()

    def _setup_market_database(self, market: Market):
        """Setup database for specific market"""

        # 🎯 SELECT DATABASE URL BASED ON MARKET
        if market == Market.KG:
            database_url = settings.database.url_kg  # KG database URL
        else:  # US
            database_url = settings.database.url_us  # US database URL

        # Create engine with connection pool
        engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            ...
        )
        self.engines[market] = engine

        # Create session factory
        SessionLocal = sessionmaker(bind=engine)
        self.session_factories[market] = SessionLocal

    def get_session_factory(self, market: Market):
        """🎯 GET SESSION FOR SPECIFIC MARKET"""
        return self.session_factories[market]
```

#### C. Global Instance (Line 155)

```python
# Single global instance that manages both databases
db_manager = MarketDatabaseManager()
```

#### D. Market Detection (Lines 180-198)

```python
def detect_market_from_phone(phone_number: str) -> Market:
    """
    🎯 THIS IS THE KEY FUNCTION!
    Determines which database to use based on phone number
    """
    clean_phone = phone_number.replace(" ", "").replace("-", "")

    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    # 📞 PHONE NUMBER → MARKET DETECTION
    if clean_phone.startswith("+996"):
        return Market.KG  # → Use KG database
    elif clean_phone.startswith("+1"):
        return Market.US  # → Use US database
    else:
        raise ValueError(f"Cannot detect market: {phone_number}")
```

---

## 🔐 3. Authentication Flow (Where Market is Set)

### File: `src/app_01/services/auth_service.py`

```python
def send_verification_code(self, request: PhoneLoginRequest, market_hint: str = None) -> SendVerificationResponse:
    """
    Step 1: User requests verification code
    """
    # 🎯 DETECT MARKET FROM PHONE NUMBER
    detected_market = detect_market_from_phone(request.phone)

    # Get the correct database for this market
    session_factory = db_manager.get_session_factory(detected_market)

    with session_factory() as db:
        # Look up or create user in THIS market's database
        user = user_model.get_by_phone(db, request.phone)
        if not user:
            user = user_model.create_user(db, request.phone)

        # ... send verification code


def verify_code(self, request: VerifyCodeRequest) -> VerifyCodeResponse:
    """
    Step 2: User enters verification code
    """
    # 🎯 DETECT MARKET FROM PHONE NUMBER AGAIN
    market = detect_market_from_phone(request.phone)
    session_factory = db_manager.get_session_factory(market)

    with session_factory() as db:
        # Look up user in correct market's database
        user = user_model.get_by_phone(db, request.phone)

        # ✅ CREATE JWT TOKEN WITH MARKET INFO
        access_token = self._create_access_token(user.id, market.value)
        #                                                  ↑
        #                                            MARKET IS STORED IN TOKEN!

        return VerifyCodeResponse(
            access_token=access_token,
            user=UserSchema(id=str(user.id), ...),
            market=market.value  # "kg" or "us"
        )


def _create_access_token(self, user_id: int, market: str) -> str:
    """Create JWT token"""
    to_encode = {
        "sub": str(user_id),  # User ID
        "market": market,      # 🎯 MARKET STORED IN TOKEN!
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

**Result:** JWT token contains:

```json
{
  "sub": "19", // User ID
  "market": "us", // 🎯 Which database this user belongs to
  "exp": 1730506363
}
```

---

## 🛒 4. Using Database in Endpoints (OLD vs NEW)

### ❌ OLD WAY (Before Fix) - `order_router.py`

```python
@router.post("/create")
async def create_order(
    request: CreateOrderRequest,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token),
    db: Session = Depends(get_db)  # ❌ PROBLEM: Always defaults to KG!
):
    # This ALWAYS connected to KG database, even for US users!
    user_id = current_user.user_id
    order = db.query(Order).filter(Order.user_id == user_id).first()
```

**Problem:**

```
User logs in with +13128059851
↓
Backend: Phone starts with +1 → Market.US
↓
Token created: {user_id: 19, market: "us"}
↓
User saved in US database with ID 19
↓
User places order
↓
order_router uses Depends(get_db) → Defaults to Market.KG ❌
↓
Looks for user_id 19 in KG database
↓
❌ USER NOT FOUND! (ID 19 only exists in US database)
```

### ✅ NEW WAY (After Fix) - `order_router.py`

```python
@router.post("/create")
async def create_order(
    request: CreateOrderRequest,
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
    # ✅ No more Depends(get_db) with default!
):
    try:
        user_id = current_user.user_id

        # ✅ EXTRACT MARKET FROM TOKEN
        user_market = Market(current_user.market.value) if current_user.market else Market.KG
        #                    ↑
        #           Token has: market="us"

        # ✅ GET THE CORRECT DATABASE SESSION
        from ..db.market_db import db_manager
        SessionLocal = db_manager.get_session_factory(user_market)
        #                                              ↑
        #                                     Market.US → US database!

        db = SessionLocal()

        # ✅ NOW QUERIES US DATABASE (where user_id 19 exists!)
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()

        # ... create order ...

    finally:
        db.close()
```

**Solution:**

```
User logs in with +13128059851
↓
Token: {user_id: 19, market: "us"}
↓
User places order
↓
order_router extracts market from token → Market.US ✅
↓
Gets US database session
↓
Looks for user_id 19 in US database
↓
✅ USER FOUND! Order created successfully!
```

---

## 📋 5. Complete Request Flow

### Example: User +13128059851 Places Order

```
1. LOGIN PHASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend: User enters +13128059851
    ↓
Backend (auth_service.py):
    ↓
    detect_market_from_phone("+13128059851")
    → phone starts with "+1"
    → return Market.US
    ↓
    db_manager.get_session_factory(Market.US)
    → Get US database session
    ↓
    Query US database:
        user = db.query(User).filter(phone="+13128059851").first()
    → Found user_id: 19
    ↓
    Create JWT token:
        {
            "sub": "19",
            "market": "us",  ← MARKET STORED!
            "exp": ...
        }
    ↓
Frontend: Stores token in localStorage

2. ORDER CREATION PHASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Frontend: User clicks "Place Order"
    ↓
    Sends request with JWT token in Authorization header
    ↓
Backend (order_router.py):
    ↓
    get_current_user_from_token()
    → Decodes JWT
    → Returns: VerifyTokenResponse(
          user_id=19,
          market=MarketEnum.US  ← MARKET FROM TOKEN!
      )
    ↓
    Extract market from token:
        user_market = Market(current_user.market.value)
        → Market.US
    ↓
    Get session for US database:
        SessionLocal = db_manager.get_session_factory(Market.US)
        db = SessionLocal()
    ↓
    Query US database:
        cart = db.query(Cart).filter(user_id=19).first()
        ✅ FOUND! (because we're querying US database)
    ↓
    Create order in US database
    ↓
    Return success
    ↓
Frontend: Shows "Order placed successfully!"
```

---

## 🎯 6. How to Get Database Session in Your Code

### Option 1: Using Market from Token (✅ Recommended for user-specific operations)

```python
from fastapi import Depends
from ..routers.auth_router import get_current_user_from_token
from ..schemas.auth import VerifyTokenResponse
from ..db.market_db import Market, db_manager

@router.post("/my-endpoint")
async def my_endpoint(
    current_user: VerifyTokenResponse = Depends(get_current_user_from_token)
):
    # ✅ Extract market from user's token
    user_market = Market(current_user.market.value)

    # ✅ Get session for user's market
    SessionLocal = db_manager.get_session_factory(user_market)
    db = SessionLocal()

    try:
        # Use db for queries
        user = db.query(User).filter(User.id == current_user.user_id).first()
        return {"user": user}
    finally:
        db.close()
```

### Option 2: Using Depends with Specific Market (for admin/system operations)

```python
from ..db.market_db import Market, get_db

@router.get("/kg-stats")
async def get_kg_stats(
    db: Session = Depends(lambda: get_db(Market.KG))
):
    # Always uses KG database
    count = db.query(Order).count()
    return {"kg_orders": count}

@router.get("/us-stats")
async def get_us_stats(
    db: Session = Depends(lambda: get_db(Market.US))
):
    # Always uses US database
    count = db.query(Order).count()
    return {"us_orders": count}
```

### Option 3: Direct Market Detection from Phone

```python
from ..db.market_db import detect_market_from_phone, db_manager

def process_phone_order(phone: str):
    # Detect market from phone number
    market = detect_market_from_phone(phone)

    # Get session for that market
    SessionLocal = db_manager.get_session_factory(market)
    db = SessionLocal()

    try:
        user = db.query(User).filter(User.phone_number == phone).first()
        # ...
    finally:
        db.close()
```

---

## 🔍 7. Debugging: Check Which Database You're Using

### In Your Code:

```python
# Check current user's market
print(f"User market: {current_user.market}")
print(f"User ID: {current_user.user_id}")

# Check database URL
user_market = Market(current_user.market.value)
engine = db_manager.get_engine(user_market)
print(f"Database URL: {engine.url}")
```

### In Terminal:

```bash
# Check both databases
cd /Users/macbookpro/M4_Projects/Prodaction/Marque

python -c "
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.users.user import User

# Check KG database
print('KG Database:')
kg_db = db_manager.get_session_factory(Market.KG)()
kg_users = kg_db.query(User).filter(User.phone_number == '+13128059851').all()
for u in kg_users:
    print(f'  User ID {u.id}: {u.phone_number}')
kg_db.close()

# Check US database
print('\nUS Database:')
us_db = db_manager.get_session_factory(Market.US)()
us_users = us_db.query(User).filter(User.phone_number == '+13128059851').all()
for u in us_users:
    print(f'  User ID {u.id}: {u.phone_number}')
us_db.close()
"
```

---

## 📝 8. Key Files Summary

| File                                  | Purpose          | Responsibility                             |
| ------------------------------------- | ---------------- | ------------------------------------------ |
| `src/app_01/core/config.py`           | Configuration    | Loads database URLs from `.env`            |
| `src/app_01/db/market_db.py`          | Database Manager | Manages connections to both databases      |
| `src/app_01/services/auth_service.py` | Authentication   | Detects market, creates tokens with market |
| `src/app_01/routers/order_router.py`  | Order API        | Uses market from token to get correct DB   |
| `src/app_01/routers/auth_router.py`   | Auth API         | Verifies tokens, returns user + market     |

---

## ✅ 9. Best Practices

### ✅ DO:

- Use `current_user.market` from JWT token for user-specific operations
- Always extract market from token when user is involved
- Close database sessions in `finally` blocks
- Use `db_manager.get_session_factory(market)` to get sessions

### ❌ DON'T:

- Don't use `Depends(get_db)` without market parameter for user operations
- Don't hardcode `Market.KG` or `Market.US`
- Don't assume all users are in one database
- Don't forget to close database sessions

---

## 🎯 Quick Reference

```python
# ✅ Get session for current user's market
user_market = Market(current_user.market.value)
SessionLocal = db_manager.get_session_factory(user_market)
db = SessionLocal()

# ✅ Detect market from phone
market = detect_market_from_phone("+13128059851")  # → Market.US

# ✅ Get config for market
from ..db.market_db import MarketConfig
config = MarketConfig.get_config(Market.US)
print(config["currency"])  # → "$"

# ✅ Check if phone is from specific market
phone = "+13128059851"
if phone.startswith("+1"):
    # US user
elif phone.startswith("+996"):
    # KG user
```

---

**Summary:** The database connection is determined by the **phone number prefix** during login, stored in the **JWT token's `market` field**, and extracted when making database queries to connect to the **correct market's database**.
