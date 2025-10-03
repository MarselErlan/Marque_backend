# 🧪 Marque Test Suite

Comprehensive unit and integration tests for the Marque e-commerce platform.

## 📁 Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── unit/                    # Unit tests (fast, isolated)
│   ├── test_auth_router.py
│   ├── test_auth_service.py
│   ├── test_banner_router.py
│   ├── test_cart_router.py
│   ├── test_database_utils.py
│   ├── test_models.py
│   ├── test_product_router.py
│   ├── test_schemas.py
│   └── test_wishlist_router.py
├── integration/             # Integration tests (slower)
└── fixtures/                # Test data fixtures
```

## 🚀 Running Tests

### Run All Unit Tests

```bash
python run_unit_tests.py
```

### Run with pytest directly

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit -v

# Specific test file
pytest tests/unit/test_auth_service.py -v

# Specific test class
pytest tests/unit/test_auth_service.py::TestTokenGeneration -v

# Specific test function
pytest tests/unit/test_auth_service.py::TestTokenGeneration::test_create_access_token -v

# Run tests with coverage
pytest --cov=src/app_01 --cov-report=html

# Run tests matching a keyword
pytest -k "auth" -v

# Run tests with markers
pytest -m unit -v
pytest -m database -v
```

## 📊 Test Coverage

View coverage reports:

```bash
# Generate HTML coverage report
pytest --cov=src/app_01 --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🏷️ Test Markers

Tests are organized with markers for easy filtering:

- `@pytest.mark.unit` - Unit tests (fast, isolated)
- `@pytest.mark.integration` - Integration tests (slower)
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.database` - Database tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.products` - Product-related tests
- `@pytest.mark.banners` - Banner-related tests
- `@pytest.mark.cart` - Cart-related tests
- `@pytest.mark.wishlist` - Wishlist-related tests
- `@pytest.mark.slow` - Slow running tests

Example usage:

```bash
# Run only auth tests
pytest -m auth -v

# Run all except slow tests
pytest -m "not slow" -v
```

## 🧪 What's Tested

### Database Layer

✅ Market detection from phone numbers  
✅ Phone number formatting  
✅ Market configuration  
✅ Database manager operations

### Models

✅ User model creation (KG/US)  
✅ Banner model  
✅ Model validation  
✅ Model relationships

### Services

✅ JWT token generation/validation  
✅ Verification code generation  
✅ Phone number validation  
✅ Rate limiting  
✅ User profile operations

### API Endpoints

✅ Authentication endpoints  
✅ Product endpoints  
✅ Product search  
✅ Banner endpoints  
✅ Cart endpoints  
✅ Wishlist endpoints

### Schemas

✅ Request validation  
✅ Response serialization  
✅ Data type validation

## 🔧 Test Fixtures

Available fixtures in `conftest.py`:

### Database Fixtures

- `test_db_engine` - In-memory test database
- `db_session` - Database session for tests
- `client` - FastAPI test client

### Data Fixtures

- `sample_user_kg_data` - Sample KG user
- `sample_user_us_data` - Sample US user
- `sample_product_data` - Sample product
- `sample_banner_data` - Sample banner
- `sample_brand_data` - Sample brand
- `sample_category_data` - Sample category

### Auth Fixtures

- `mock_jwt_token` - Mock JWT token
- `auth_headers` - Authorization headers

### Market Fixtures

- `market` - Parametrized for both markets
- `kg_market` - KG market
- `us_market` - US market

## 📝 Writing Tests

### Unit Test Template

```python
import pytest

class TestFeatureName:
    """Test feature description"""

    def test_specific_behavior(self):
        """Test that specific behavior works"""
        # Arrange
        expected = "result"

        # Act
        actual = function_to_test()

        # Assert
        assert actual == expected
```

### Using Fixtures

```python
def test_with_database(db_session):
    """Test using database session"""
    user = UserKG(phone_number="+996555123456")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("phone,market", [
    ("+996555123456", Market.KG),
    ("+12125551234", Market.US),
])
def test_market_detection(phone, market):
    """Test market detection"""
    detected = detect_market_from_phone(phone)
    assert detected == market
```

### API Endpoint Tests

```python
def test_endpoint(client):
    """Test API endpoint"""
    response = client.get("/api/v1/endpoint")
    assert response.status_code == 200
    assert response.json()["key"] == "value"
```

## 🎯 Test Coverage Goals

Target coverage: **80%+**

Current coverage by component:

- Database utilities: ~90%
- Models: ~80%
- Services: ~75%
- Routers: ~70%
- Schemas: ~85%

## 🐛 Debugging Tests

### Run with verbose output

```bash
pytest -vv
```

### Show print statements

```bash
pytest -s
```

### Stop on first failure

```bash
pytest -x
```

### Run last failed tests

```bash
pytest --lf
```

### Run with debugger

```bash
pytest --pdb
```

## 📦 Test Dependencies

Required packages:

```
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
```

Install:

```bash
pip install pytest pytest-cov pytest-asyncio httpx
```

## 🔄 Continuous Integration

Tests run automatically on:

- Every commit
- Pull requests
- Before deployment

## 💡 Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests isolated** (no dependencies between tests)
3. **Use descriptive names** (`test_user_can_login_with_valid_credentials`)
4. **One assertion per test** (when possible)
5. **Use fixtures** for common setup
6. **Mock external dependencies** (SMS, email, etc.)
7. **Test edge cases** (empty strings, null values, etc.)
8. **Keep tests fast** (< 1 second per test)

## 📚 Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html)

---

**Happy Testing! 🎉**
