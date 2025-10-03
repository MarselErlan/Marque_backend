# 📊 Code Coverage Analysis & Improvement Plan

## 🎯 Current Coverage Status

**Overall Coverage:** **34%** (1,755 / 4,727 statements)

```
██████████░░░░░░░░░░░░░░░░░░░░░░ 34%
```

---

## 📈 Coverage by Category

### 🟢 **Excellent Coverage (>75%)**

| Module                          | Coverage | Statements | Priority |
| ------------------------------- | -------- | ---------- | -------- |
| **main.py**                     | 88%      | 53         | ✅ Good  |
| **db/**init**.py**              | 100%     | 2          | ✅ Good  |
| **db/market_db.py**             | 81%      | 93         | ✅ Good  |
| **models/**init**.py**          | 100%     | 5          | ✅ Good  |
| **models/products/**init**.py** | 100%     | 9          | ✅ Good  |
| **models/banners/**init**.py**  | 100%     | 2          | ✅ Good  |
| **models/users/interaction.py** | 94%      | 16         | ✅ Good  |
| **models/orders/cart_order.py** | 80%      | 30         | ✅ Good  |
| **models/admins/admin_log.py**  | 81%      | 26         | ✅ Good  |
| **models/products/brand.py**    | 79%      | 42         | ✅ Good  |
| **models/products/category.py** | 83%      | 59         | ✅ Good  |
| **models/products/review.py**   | 78%      | 32         | ✅ Good  |
| **core/config.py**              | 76%      | 130        | ✅ Good  |

### 🟡 **Moderate Coverage (50-75%)**

| Module                                    | Coverage | Statements | Priority  |
| ----------------------------------------- | -------- | ---------- | --------- |
| **models/users/user.py**                  | 74%      | 38         | 🔶 Medium |
| **models/users/user_address.py**          | 71%      | 45         | 🔶 Medium |
| **models/products/sku.py**                | 68%      | 35         | 🔶 Medium |
| **models/orders/order.py**                | 67%      | 89         | 🔶 Medium |
| **models/orders/order_status_history.py** | 68%      | 29         | 🔶 Medium |
| **models/products/product_asset.py**      | 65%      | 29         | 🔶 Medium |
| **models/banners/banner.py**              | 63%      | 35         | 🔶 Medium |
| **models/users/market_user.py**           | 59%      | 136        | 🔶 Medium |
| **models/users/user_notification.py**     | 54%      | 55         | 🔶 Medium |
| **models/users/phone_verification.py**    | 53%      | 53         | 🔶 Medium |
| **models/products/product_filter.py**     | 55%      | 135        | 🔶 Medium |

### 🔴 **Low Coverage (<50%) - PRIORITY**

| Module                                        | Coverage | Statements | Priority        |
| --------------------------------------------- | -------- | ---------- | --------------- |
| **routers/auth_router.py**                    | 42%      | 116        | 🔥 **HIGH**     |
| **models/users/market_phone_verification.py** | 48%      | 122        | 🔥 **HIGH**     |
| **models/users/user_payment_method.py**       | 48%      | 56         | 🔥 **HIGH**     |
| **models/products/product.py**                | 46%      | 155        | 🔥 **HIGH**     |
| **models/admins/admin.py**                    | 40%      | 66         | 🔥 **HIGH**     |
| **routers/banner_router.py**                  | 33%      | 90         | 🔥 **HIGH**     |
| **routers/cart_router.py**                    | 20%      | 64         | 🔥 **CRITICAL** |

### ⚫ **No Coverage (0%) - CRITICAL**

| Module                                         | Statements | Priority                      |
| ---------------------------------------------- | ---------- | ----------------------------- |
| **routers/auth.py**                            | 124        | 🔥 **CRITICAL**               |
| **models/orders/cart.py**                      | 20         | 🔥 **CRITICAL**               |
| **models/users/wishlist.py**                   | 19         | 🔥 **CRITICAL**               |
| **models/users/market_user_address.py**        | 141        | 🔥 **CRITICAL**               |
| **models/users/market_user_payment_method.py** | 185        | 🔥 **CRITICAL**               |
| **admin/** (all files)                         | 362        | ⚠️ Low (admin panel)          |
| **core/container.py**                          | 130        | ⚠️ Low (dependency injection) |
| **core/exceptions.py**                         | 104        | ⚠️ Low (error handling)       |
| **core/middleware.py**                         | 160        | ⚠️ Low (middleware)           |

---

## 🎯 Priority Improvement Plan

### **Phase 1: Critical Routers (Immediate Impact)** 🔥

**Target:** Bring router coverage from 20-42% → 70%+

#### 1.1 Auth Router (42% → 75%)

**File:** `src/app_01/routers/auth_router.py` (116 statements)  
**Missing:** 69 statements

**Tests Needed:**

- [ ] Test all auth endpoints with valid data
- [ ] Test error cases (invalid phone, expired codes)
- [ ] Test rate limiting
- [ ] Test token generation and validation
- [ ] Test logout flow
- [ ] Test profile updates

**Estimated:** 15-20 new tests

---

#### 1.2 Cart Router (20% → 70%)

**File:** `src/app_01/routers/cart_router.py` (64 statements)  
**Missing:** 48 statements

**Tests Needed:**

- [ ] Test add to cart (valid/invalid products)
- [ ] Test update quantity (positive/negative/zero)
- [ ] Test remove from cart
- [ ] Test get cart (empty/with items)
- [ ] Test clear cart
- [ ] Test authentication requirements

**Estimated:** 12-15 new tests

---

#### 1.3 Banner Router (33% → 70%)

**File:** `src/app_01/routers/banner_router.py` (90 statements)  
**Missing:** 57 statements

**Tests Needed:**

- [ ] Test get all banners (with filters)
- [ ] Test get banner by ID
- [ ] Test create banner (admin)
- [ ] Test update banner (admin)
- [ ] Test delete banner (admin)
- [ ] Test banner type filtering
- [ ] Test active/inactive filtering

**Estimated:** 10-12 new tests

---

### **Phase 2: Core Models (Foundation)** 🏗️

**Target:** Bring critical model coverage from 0-46% → 70%+

#### 2.1 Cart & Wishlist Models (0% → 70%)

**Files:**

- `src/app_01/models/orders/cart.py` (20 statements)
- `src/app_01/models/users/wishlist.py` (19 statements)

**Tests Needed:**

- [ ] Test cart creation and relationships
- [ ] Test cart item addition/removal
- [ ] Test wishlist creation and relationships
- [ ] Test wishlist item addition/removal
- [ ] Test model properties and methods

**Estimated:** 10-12 new tests

---

#### 2.2 Product Model (46% → 75%)

**File:** `src/app_01/models/products/product.py` (155 statements)  
**Missing:** 70 statements

**Tests Needed:**

- [ ] Test product creation with all fields
- [ ] Test product relationships (brand, category, SKUs)
- [ ] Test product properties (price calculations, stock status)
- [ ] Test product search and filtering
- [ ] Test product validation

**Estimated:** 15-18 new tests

---

#### 2.3 Market-Specific Models (0-48% → 60%)

**Files:**

- `market_user_address.py` (141 statements, 0%)
- `market_user_payment_method.py` (185 statements, 0%)
- `market_phone_verification.py` (122 statements, 48%)

**Tests Needed:**

- [ ] Test address creation for KG/US markets
- [ ] Test address validation per market
- [ ] Test payment method creation
- [ ] Test phone verification flow
- [ ] Test market-specific formatting

**Estimated:** 20-25 new tests

---

### **Phase 3: Service Layer** ⚙️

**Target:** Bring service coverage from 15% → 70%+

#### 3.1 Auth Service (15% → 75%)

**File:** `src/app_01/services/auth_service.py` (161 statements)  
**Missing:** 132 statements

**Tests Needed:**

- [ ] Test send_verification_code with valid phone
- [ ] Test verify_code with correct/incorrect codes
- [ ] Test create_access_token
- [ ] Test get_current_user
- [ ] Test refresh_token
- [ ] Test market detection logic
- [ ] Test rate limiting
- [ ] Test error handling

**Estimated:** 18-22 new tests

---

### **Phase 4: Integration Tests** 🔗

**Target:** Fix remaining 25 errors and improve integration coverage

#### 4.1 Fix Integration Test Fixtures

**Issues:**

- Database session management
- Mock data generation
- Test isolation

**Actions:**

- [ ] Refactor `test_db` fixture in integration conftest
- [ ] Add proper setup/teardown
- [ ] Create helper functions for test data
- [ ] Ensure proper transaction handling

**Estimated:** 3-5 fixture improvements

---

#### 4.2 Complete End-to-End Scenarios

**Tests Needed:**

- [ ] Complete purchase flow (browse → cart → checkout)
- [ ] Complete wishlist flow
- [ ] Multi-market user journeys
- [ ] Search → filter → detail flow
- [ ] Admin panel workflows

**Estimated:** 10-12 new integration tests

---

## 📊 Coverage Goals

### Short-term (1-2 days)

| Component         | Current | Target | Impact     |
| ----------------- | ------- | ------ | ---------- |
| **Routers**       | 20-42%  | 70%    | High       |
| **Cart/Wishlist** | 0%      | 70%    | Critical   |
| **Overall**       | 34%     | 50%    | +16 points |

### Medium-term (1 week)

| Component    | Current | Target | Impact     |
| ------------ | ------- | ------ | ---------- |
| **Models**   | 0-74%   | 70%    | High       |
| **Services** | 15%     | 70%    | High       |
| **Overall**  | 34%     | 65%    | +31 points |

### Long-term (2 weeks)

| Component        | Current | Target  | Impact     |
| ---------------- | ------- | ------- | ---------- |
| **All Routers**  | 20-42%  | 80%     | High       |
| **All Models**   | 0-94%   | 75%     | High       |
| **All Services** | 15%     | 80%     | High       |
| **Overall**      | 34%     | **80%** | +46 points |

---

## 🎯 Quick Wins (Immediate Actions)

### 1. Cart Router Tests (2 hours)

```bash
# Create: tests/unit/test_cart_router_coverage.py
# Add 12 tests for cart operations
# Expected coverage: 20% → 70% (+50 points)
```

### 2. Wishlist Model Tests (1 hour)

```bash
# Add to: tests/unit/test_models.py
# Add 8 tests for wishlist operations
# Expected coverage: 0% → 70% (+70 points)
```

### 3. Cart Model Tests (1 hour)

```bash
# Add to: tests/unit/test_models.py
# Add 8 tests for cart operations
# Expected coverage: 0% → 70% (+70 points)
```

### 4. Auth Router Tests (3 hours)

```bash
# Enhance: tests/unit/test_auth_router.py
# Add 15 more tests for missing paths
# Expected coverage: 42% → 75% (+33 points)
```

**Total Time:** ~7 hours  
**Expected Overall Impact:** 34% → 45% (+11 points)

---

## 📝 Test Templates

### Router Test Template

```python
def test_endpoint_success(client):
    """Test successful endpoint response"""
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
    assert "expected_field" in response.json()

def test_endpoint_validation_error(client):
    """Test endpoint with invalid data"""
    response = client.post("/api/v1/endpoint", json={})
    assert response.status_code == 422

def test_endpoint_not_found(client):
    """Test endpoint with non-existent ID"""
    response = client.get("/api/v1/endpoint/999999")
    assert response.status_code == 404

def test_endpoint_authentication_required(client):
    """Test endpoint requires authentication"""
    response = client.post("/api/v1/endpoint")
    assert response.status_code in [401, 403]
```

### Model Test Template

```python
def test_model_creation(db_session):
    """Test model can be created"""
    obj = ModelClass(field1="value1", field2="value2")
    db_session.add(obj)
    db_session.commit()

    assert obj.id is not None
    assert obj.field1 == "value1"

def test_model_relationship(db_session, related_obj):
    """Test model relationships work"""
    obj = ModelClass(field1="value1")
    obj.related = related_obj
    db_session.add(obj)
    db_session.commit()

    assert obj.related.id == related_obj.id

def test_model_validation(db_session):
    """Test model validation"""
    with pytest.raises(ValidationError):
        obj = ModelClass(invalid_field="bad_value")
        db_session.add(obj)
        db_session.commit()
```

---

## 🚀 Execution Plan

### Week 1: Critical Coverage (Phase 1 & 2)

**Monday-Tuesday:** Auth Router + Cart Router tests  
**Wednesday-Thursday:** Cart/Wishlist Model tests  
**Friday:** Product Model tests

**Expected:** 34% → 50% coverage (+16 points)

---

### Week 2: Services & Integration (Phase 3 & 4)

**Monday-Wednesday:** Auth Service tests + Market-specific models  
**Thursday-Friday:** Integration test fixes + end-to-end scenarios

**Expected:** 50% → 65% coverage (+15 points)

---

### Week 3: Polish & Reach 80%

**Monday-Wednesday:** Remaining router tests  
**Thursday-Friday:** Edge cases + error handling

**Expected:** 65% → 80% coverage (+15 points)

---

## 📊 Success Metrics

### Daily Tracking

- [ ] Coverage increase by at least 2% per day
- [ ] No new failing tests introduced
- [ ] All new tests pass consistently

### Weekly Goals

- [ ] Week 1: 50% coverage (from 34%)
- [ ] Week 2: 65% coverage (from 50%)
- [ ] Week 3: 80% coverage (from 65%)

### Quality Gates

- [ ] All critical paths covered (auth, cart, checkout)
- [ ] All public APIs have tests
- [ ] All models have basic CRUD tests
- [ ] No module below 50% coverage
- [ ] Integration tests all passing

---

## 💡 Best Practices

1. **Write tests for bug fixes** - Every bug should have a test
2. **Test edge cases** - Empty lists, null values, boundary conditions
3. **Test error paths** - Not just happy paths
4. **Use fixtures** - Reuse test data setup
5. **Keep tests isolated** - Each test should be independent
6. **Test behavior, not implementation** - Focus on what, not how
7. **Maintain tests** - Update tests when requirements change

---

## 🎊 Expected Outcomes

After completing this plan:

✅ **80% overall code coverage**  
✅ **All critical paths tested**  
✅ **Integration tests stable**  
✅ **No module below 50% coverage**  
✅ **Production-ready test suite**  
✅ **Confident deployments**  
✅ **Fast feedback on changes**

---

**Status:** 📋 Plan Ready  
**Start Date:** October 3, 2025  
**Estimated Completion:** October 24, 2025 (3 weeks)  
**Current Coverage:** 34%  
**Target Coverage:** 80%
