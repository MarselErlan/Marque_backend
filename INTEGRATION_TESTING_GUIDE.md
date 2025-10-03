# 🔗 Integration Testing Guide

## Overview

Integration tests verify that multiple components of the Marque e-commerce platform work together correctly. Unlike unit tests that test individual functions in isolation, integration tests test complete workflows and API endpoints.

---

## 📁 Test Structure

```
tests/integration/
├── __init__.py
├── conftest.py                      # Integration test fixtures
├── test_auth_flow.py                # Authentication workflows (14 tests)
├── test_product_api.py              # Product API endpoints (17 tests)
├── test_banner_api.py               # Banner API endpoints (11 tests)
├── test_cart_wishlist_api.py        # Cart & wishlist APIs (14 tests)
└── test_end_to_end_workflows.py     # Complete user journeys (27 tests)
```

**Total: 83 integration tests created**

---

## 🎯 What Integration Tests Cover

### 1. **Authentication Flow** (14 tests)

- ✅ Health check endpoint
- ✅ Supported markets endpoint
- ✅ Sending verification codes (KG & US)
- ✅ Verifying codes with validation
- ✅ Getting user profile with/without auth
- ✅ Token generation and validation
- ✅ Logout functionality
- ✅ Multi-market user workflows

### 2. **Product API** (17 tests)

- ✅ Product listing endpoint
- ✅ Product search with query validation
- ✅ Filtering by category, brand
- ✅ Search with multiple filters
- ✅ Product detail by ID
- ✅ Pagination handling
- ✅ Sort options (newest, popular, price, relevance)
- ✅ Database relationships (brand, category)

### 3. **Banner API** (11 tests)

- ✅ Banner listing endpoint
- ✅ Get banner by ID
- ✅ Filter by type (sale/model)
- ✅ Filter by active status
- ✅ Admin operations (create, update, delete)
- ✅ Authentication requirements
- ✅ Database integrity

### 4. **Cart & Wishlist** (14 tests)

- ✅ Cart operations require authentication
- ✅ Wishlist operations require authentication
- ✅ Adding/removing items
- ✅ Updating quantities
- ✅ Clearing cart/wishlist
- ✅ Authenticated vs non-authenticated access

### 5. **End-to-End Workflows** (27 tests)

- ✅ Complete user journey (browse → search → view)
- ✅ Guest user workflows
- ✅ Authenticated user workflows
- ✅ Search and filter combinations
- ✅ Market-specific functionality (KG/US)
- ✅ Error handling
- ✅ Database integrity checks
- ✅ Concurrent operations
- ✅ Pagination consistency
- ✅ Performance benchmarks

---

## 🧪 Running Integration Tests

### Run All Integration Tests:

```bash
pytest tests/integration/ -v
```

### Run Specific Test File:

```bash
# Auth tests
pytest tests/integration/test_auth_flow.py -v

# Product tests
pytest tests/integration/test_product_api.py -v

# Banner tests
pytest tests/integration/test_banner_api.py -v

# Cart & wishlist tests
pytest tests/integration/test_cart_wishlist_api.py -v

# End-to-end workflows
pytest tests/integration/test_end_to_end_workflows.py -v
```

### Run by Marker:

```bash
# Only integration tests
pytest -m integration -v

# Slow tests
pytest -m slow -v
```

### Run Specific Test Class:

```bash
pytest tests/integration/test_product_api.py::TestProductSearchAPI -v
```

### With Coverage:

```bash
pytest tests/integration/ --cov=src/app_01 --cov-report=html
```

---

## 🔧 Test Fixtures

### Available Fixtures (in `conftest.py`):

#### Database Fixtures:

- `test_db` - In-memory test database
- `api_client` - FastAPI test client

#### Sample Data:

- `sample_kg_user` - KG market user
- `sample_us_user` - US market user
- `sample_product` - Product with brand & category
- `sample_banner` - Active sale banner
- `sample_brand` - Nike brand
- `sample_category` - Shoes category

#### Authentication:

- `auth_token` - Valid JWT token
- `auth_headers` - Authorization headers

---

## 📝 Test Examples

### Example 1: Testing API Endpoint

```python
@pytest.mark.integration
def test_get_products_endpoint(api_client):
    """Test that products endpoint exists and works"""
    response = api_client.get("/api/v1/products")

    assert response.status_code != 404
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
```

### Example 2: Testing With Authentication

```python
@pytest.mark.integration
def test_get_cart_with_auth(api_client, auth_headers):
    """Test getting cart with authentication"""
    response = api_client.get("/api/v1/cart", headers=auth_headers)

    assert response.status_code in [200, 404]
```

### Example 3: Testing Database Operations

```python
@pytest.mark.integration
def test_product_in_database(test_db, sample_product):
    """Test that product is created in database"""
    from src.app_01.models.products.product import Product

    product = test_db.query(Product).filter_by(
        id=sample_product.id
    ).first()

    assert product is not None
    assert product.title == "Running Shoes"
```

### Example 4: Testing Complete Workflow

```python
@pytest.mark.integration
def test_complete_shopping_flow(api_client, auth_headers, sample_product):
    """Test complete shopping workflow"""
    # 1. Browse products
    response = api_client.get("/api/v1/products")
    assert response.status_code == 200

    # 2. Search for specific product
    response = api_client.get("/api/v1/products/search?q=shoes")
    assert response.status_code == 200

    # 3. Add to cart
    response = api_client.post(
        "/api/v1/cart/items",
        headers=auth_headers,
        json={
            "product_id": sample_product.id,
            "quantity": 1
        }
    )
    assert response.status_code in [200, 201]
```

---

## 🎭 Test Categories

### By Component:

- **API Tests** - Test HTTP endpoints
- **Database Tests** - Test data persistence
- **Auth Tests** - Test authentication/authorization
- **Workflow Tests** - Test complete user journeys

### By Speed:

- **Fast** - Tests without external dependencies (< 1s)
- **Slow** - Tests with database/network calls (marked with `@pytest.mark.slow`)

### By Reliability:

- **Deterministic** - Always produce same result
- **Flaky** - May fail intermittently (should be fixed or removed)

---

## 🚀 Integration Test Patterns

### 1. **Arrange-Act-Assert (AAA)**

```python
def test_example(api_client):
    # Arrange
    data = {"key": "value"}

    # Act
    response = api_client.post("/endpoint", json=data)

    # Assert
    assert response.status_code == 200
```

### 2. **Happy Path Testing**

```python
def test_successful_search(api_client):
    """Test successful product search"""
    response = api_client.get("/api/v1/products/search?q=shoes")

    assert response.status_code == 200
    assert "results" in response.json()
```

### 3. **Error Path Testing**

```python
def test_search_without_query(api_client):
    """Test search fails without query"""
    response = api_client.get("/api/v1/products/search")

    assert response.status_code == 422
```

### 4. **Authorization Testing**

```python
def test_protected_endpoint_without_auth(api_client):
    """Test protected endpoint requires auth"""
    response = api_client.get("/api/v1/cart")

    assert response.status_code in [401, 403]
```

---

## 📊 Test Coverage Goals

### Current Status:

- **83 integration tests created**
- **Test coverage areas:**
  - Auth: 14 tests
  - Products: 17 tests
  - Banners: 11 tests
  - Cart/Wishlist: 14 tests
  - E2E Workflows: 27 tests

### Target Coverage:

- ✅ All public API endpoints tested
- ✅ Happy paths covered
- ✅ Error cases handled
- ✅ Authentication verified
- ✅ Database relationships checked
- ⏳ Performance benchmarks (in progress)

---

## 🐛 Debugging Integration Tests

### View Full Error Details:

```bash
pytest tests/integration/ -v --tb=long
```

### Stop on First Failure:

```bash
pytest tests/integration/ -x
```

### Run Specific Failed Test:

```bash
pytest tests/integration/test_product_api.py::TestProductSearchAPI::test_search_with_valid_query -v
```

### Print Debug Output:

```python
def test_example(api_client):
    response = api_client.get("/api/v1/products")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    assert response.status_code == 200
```

Then run with `-s` flag:

```bash
pytest tests/integration/ -v -s
```

---

## 💡 Best Practices

### ✅ Do's:

1. **Test complete workflows** - Not just individual functions
2. **Use realistic data** - Sample data should mirror production
3. **Test error cases** - Not just happy paths
4. **Keep tests independent** - Each test should run in isolation
5. **Use fixtures** - Don't duplicate setup code
6. **Test with authentication** - Verify security
7. **Check response structure** - Not just status codes

### ❌ Don'ts:

1. **Don't test implementation details** - Test behavior
2. **Don't make external API calls** - Mock them
3. **Don't depend on test order** - Tests should be independent
4. **Don't ignore slow tests** - Mark them and run separately
5. **Don't test everything** - Focus on critical paths

---

## 🔄 Continuous Integration

### GitHub Actions Example:

```yaml
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
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v --cov
```

---

## 📈 Performance Testing

### Benchmark Tests:

```python
@pytest.mark.slow
@pytest.mark.integration
def test_search_performance(api_client):
    """Test search response time"""
    import time

    start = time.time()
    response = api_client.get("/api/v1/products/search?q=test")
    end = time.time()

    # Should respond within 2 seconds
    assert (end - start) < 2.0
    assert response.status_code == 200
```

---

## 🎯 Summary

Integration tests ensure your application components work together correctly:

✅ **83 comprehensive integration tests**  
✅ **Cover all major features** (auth, products, banners, cart, wishlist)  
✅ **Test complete workflows** (guest browsing, authenticated shopping)  
✅ **Verify API endpoints** (requests, responses, errors)  
✅ **Check database operations** (CRUD, relationships)  
✅ **Test authentication** (protected routes, tokens)  
✅ **Include performance tests** (response times)

---

## 📚 Additional Resources

- **Unit Tests**: `tests/unit/` - Test individual functions
- **Test Documentation**: `tests/README.md` - General testing guide
- **API Documentation**: `API_DOCUMENTATION.md` - API endpoints
- **Product Search Guide**: `PRODUCT_SEARCH_GUIDE.md` - Search feature docs

---

**Integration testing ensures your application works as a cohesive system!** 🚀
