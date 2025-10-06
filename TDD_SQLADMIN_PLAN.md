# 🧪 TDD Plan: SQLAdmin Integration at /admin

## 📋 Current State Analysis

### ✅ What Exists:

- ✅ Admin views defined (`admin_app.py`, `sqladmin_views.py`)
- ✅ Separate admin app (`main_admin.py` on port 8001)
- ✅ Admin models (Product, SKU, User, etc.)
- ✅ Authentication backend for admin

### ❌ What's Missing:

- ❌ **Admin NOT integrated into main app**
- ❌ **No /admin route in main FastAPI app**
- ❌ **No multi-market support in admin**
- ❌ **No tests for admin functionality**
- ❌ **Admin uses old single-database approach**

---

## 🎯 TDD Goals

### Phase 1: Write Tests First ✅

1. Test admin authentication
2. Test admin views access
3. Test CRUD operations for each model
4. Test multi-market data separation
5. Test permissions and authorization

### Phase 2: Implement Features ✅

1. Integrate admin into main app at `/admin`
2. Add multi-market support
3. Implement proper authentication
4. Create admin views for all models
5. Add market-specific filtering

### Phase 3: Refine & Document ✅

1. Add comprehensive tests
2. Document admin usage
3. Create admin user guide
4. Performance optimization

---

## 📝 Test Structure (TDD)

```
tests/
├── admin/
│   ├── __init__.py
│   ├── conftest.py                    # Admin test fixtures
│   ├── test_admin_auth.py            # Authentication tests
│   ├── test_admin_integration.py     # Integration with main app
│   ├── test_admin_product_views.py   # Product management tests
│   ├── test_admin_user_views.py      # User management tests
│   ├── test_admin_order_views.py     # Order management tests
│   ├── test_admin_multimarket.py     # Multi-market tests
│   └── test_admin_permissions.py     # Permission tests
```

---

## 🧪 Test Cases (Write These First!)

### 1. Admin Authentication Tests (`test_admin_auth.py`)

```python
# Test 1: Admin login with correct credentials
def test_admin_login_success(admin_client):
    """GIVEN valid admin credentials
    WHEN POST to /admin/login
    THEN return 200 and set auth cookie"""
    pass  # RED - Write test first

# Test 2: Admin login with wrong credentials
def test_admin_login_failure(admin_client):
    """GIVEN invalid credentials
    WHEN POST to /admin/login
    THEN return 401 unauthorized"""
    pass  # RED

# Test 3: Access admin without authentication
def test_admin_requires_auth(client):
    """GIVEN no authentication
    WHEN GET /admin/
    THEN redirect to login"""
    pass  # RED

# Test 4: Admin logout
def test_admin_logout(authenticated_admin_client):
    """GIVEN authenticated admin
    WHEN POST to /admin/logout
    THEN clear session and redirect"""
    pass  # RED
```

### 2. Admin Integration Tests (`test_admin_integration.py`)

```python
# Test 5: Admin accessible at /admin
def test_admin_route_exists(client):
    """GIVEN main FastAPI app
    WHEN GET /admin/
    THEN return 200 or redirect to login"""
    pass  # RED

# Test 6: Admin separate from API
def test_admin_separate_from_api(client):
    """GIVEN main app
    WHEN access /admin and /api/v1
    THEN both work independently"""
    pass  # RED

# Test 7: Admin uses correct database
def test_admin_uses_correct_db(authenticated_admin_client):
    """GIVEN authenticated admin
    WHEN access admin views
    THEN use correct market database"""
    pass  # RED
```

### 3. Product Management Tests (`test_admin_product_views.py`)

```python
# Test 8: List products in admin
def test_admin_list_products(authenticated_admin_client):
    """GIVEN authenticated admin
    WHEN GET /admin/product/list
    THEN return all products with pagination"""
    pass  # RED

# Test 9: Create product via admin
def test_admin_create_product(authenticated_admin_client):
    """GIVEN authenticated admin
    WHEN POST new product data
    THEN create product and return success"""
    pass  # RED

# Test 10: Edit product via admin
def test_admin_edit_product(authenticated_admin_client, sample_product):
    """GIVEN existing product
    WHEN PUT updated data
    THEN update product"""
    pass  # RED

# Test 11: Delete product via admin
def test_admin_delete_product(authenticated_admin_client, sample_product):
    """GIVEN existing product
    WHEN DELETE request
    THEN soft delete or hard delete product"""
    pass  # RED

# Test 12: Bulk product operations
def test_admin_bulk_product_update(authenticated_admin_client):
    """GIVEN multiple products
    WHEN bulk update request
    THEN update all selected products"""
    pass  # RED
```

### 4. User Management Tests (`test_admin_user_views.py`)

```python
# Test 13: List users
def test_admin_list_users(authenticated_admin_client):
    """GIVEN authenticated admin
    WHEN GET /admin/user/list
    THEN return all users with pagination"""
    pass  # RED

# Test 14: View user details
def test_admin_view_user_details(authenticated_admin_client, sample_user):
    """GIVEN existing user
    WHEN GET user details
    THEN return full user profile"""
    pass  # RED

# Test 15: Ban/unban user
def test_admin_ban_user(authenticated_admin_client, sample_user):
    """GIVEN active user
    WHEN ban action
    THEN set is_active=False"""
    pass  # RED

# Test 16: View user orders
def test_admin_view_user_orders(authenticated_admin_client, sample_user):
    """GIVEN user with orders
    WHEN view user orders
    THEN return all user's orders"""
    pass  # RED
```

### 5. Multi-Market Tests (`test_admin_multimarket.py`)

```python
# Test 17: Filter by market
def test_admin_filter_by_market(authenticated_admin_client):
    """GIVEN data in KG and US markets
    WHEN filter by market
    THEN show only selected market data"""
    pass  # RED

# Test 18: Switch market context
def test_admin_switch_market(authenticated_admin_client):
    """GIVEN admin in KG market
    WHEN switch to US market
    THEN show US data"""
    pass  # RED

# Test 19: Create product for specific market
def test_admin_create_product_for_market(authenticated_admin_client):
    """GIVEN market selection
    WHEN create product
    THEN create in selected market database"""
    pass  # RED

# Test 20: Prevent cross-market data leaks
def test_admin_no_cross_market_data(authenticated_admin_client):
    """GIVEN KG market products
    WHEN viewing US market
    THEN don't show KG products"""
    pass  # RED
```

### 6. Order Management Tests (`test_admin_order_views.py`)

```python
# Test 21: List orders
def test_admin_list_orders(authenticated_admin_client):
    """GIVEN orders in database
    WHEN GET /admin/order/list
    THEN return all orders with status"""
    pass  # RED

# Test 22: Update order status
def test_admin_update_order_status(authenticated_admin_client, sample_order):
    """GIVEN pending order
    WHEN update status to shipped
    THEN update order and notify user"""
    pass  # RED

# Test 23: View order details
def test_admin_view_order_details(authenticated_admin_client, sample_order):
    """GIVEN order with items
    WHEN GET order details
    THEN return full order info with items"""
    pass  # RED

# Test 24: Cancel order
def test_admin_cancel_order(authenticated_admin_client, sample_order):
    """GIVEN active order
    WHEN cancel order
    THEN update status and restore stock"""
    pass  # RED
```

### 7. Permission Tests (`test_admin_permissions.py`)

```python
# Test 25: Super admin has all permissions
def test_super_admin_full_access(authenticated_super_admin):
    """GIVEN super admin user
    WHEN access any admin view
    THEN allow access"""
    pass  # RED

# Test 26: Content admin limited permissions
def test_content_admin_limited_access(authenticated_content_admin):
    """GIVEN content admin
    WHEN access product views
    THEN allow, but deny user management"""
    pass  # RED

# Test 27: Read-only admin
def test_readonly_admin_no_edit(authenticated_readonly_admin):
    """GIVEN readonly admin
    WHEN attempt to edit
    THEN deny edit but allow view"""
    pass  # RED
```

---

## 🚀 Implementation Steps (After Tests)

### Step 1: Test Fixtures (`tests/admin/conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def admin_client():
    """Create test client for admin routes"""
    # TODO: Implement
    pass

@pytest.fixture
def authenticated_admin_client(admin_client):
    """Create authenticated admin test client"""
    # TODO: Implement
    pass

@pytest.fixture
def sample_admin_user(test_db):
    """Create sample admin user"""
    # TODO: Implement
    pass

@pytest.fixture
def sample_product(test_db):
    """Create sample product for testing"""
    # TODO: Implement
    pass

@pytest.fixture
def sample_order(test_db, sample_user, sample_product):
    """Create sample order for testing"""
    # TODO: Implement
    pass
```

### Step 2: Integrate Admin into Main App

**File: `src/app_01/main.py`**

```python
from .admin.admin_app import create_sqladmin_app

# After creating FastAPI app...
# Add SQLAdmin
admin = create_sqladmin_app(app)
```

### Step 3: Update Admin for Multi-Market

**File: `src/app_01/admin/multimarket_admin.py`**

```python
from sqladmin import ModelView
from sqlalchemy import select

class MultiMarketModelView(ModelView):
    """Base view with multi-market support"""

    def get_query(self, **kwargs):
        """Override to filter by current market"""
        query = super().get_query(**kwargs)
        market = self.get_current_market()
        # Add market filter
        return query

    def get_current_market(self):
        """Get current market from session or header"""
        # TODO: Implement
        pass
```

### Step 4: Create Admin Models

**Files to create/update:**

- `src/app_01/models/admins/admin.py` - Admin user model
- `src/app_01/models/admins/admin_session.py` - Admin sessions
- `src/app_01/models/admins/admin_permission.py` - Permissions

### Step 5: Update Admin Views

Update all admin views to support:

- Multi-market data
- Proper permissions
- Audit logging
- Russian translations

---

## 📊 Success Criteria

### Tests Must Pass:

- [ ] All 27 test cases pass
- [ ] 100% test coverage for admin code
- [ ] No flaky tests
- [ ] Fast test execution (<10 seconds)

### Features Must Work:

- [ ] Admin accessible at `/admin`
- [ ] Secure authentication
- [ ] Multi-market support
- [ ] CRUD operations for all models
- [ ] Proper permissions
- [ ] Audit logging

### Code Quality:

- [ ] No linter errors
- [ ] Type hints everywhere
- [ ] Comprehensive docstrings
- [ ] Clean, maintainable code

---

## 🎯 Next Action

**START HERE:**

1. **Create test structure**:

   ```bash
   mkdir -p tests/admin
   touch tests/admin/__init__.py
   touch tests/admin/conftest.py
   touch tests/admin/test_admin_auth.py
   ```

2. **Write first failing test** (RED):

   ```bash
   # Edit tests/admin/test_admin_auth.py
   # Add test_admin_login_success (it will fail)
   ```

3. **Run test to see it fail**:

   ```bash
   pytest tests/admin/test_admin_auth.py::test_admin_login_success -v
   ```

4. **Implement minimum code to pass** (GREEN)

5. **Refactor** (REFACTOR)

6. **Repeat for next test**

---

## 📚 Resources

- SQLAdmin Docs: https://aminalaee.dev/sqladmin/
- FastAPI Admin: https://fastapi.tiangolo.com/advanced/admin/
- TDD Best Practices: Red → Green → Refactor

---

**Ready to start TDD? Let's write the first test!** 🚀
