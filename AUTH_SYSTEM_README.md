# 🌍 Marque Multi-Market Authentication System

A comprehensive phone number-based authentication system supporting both **Kyrgyzstan (KG)** and **United States (US)** markets with separate databases, models, and business logic.

## 🚀 Features

### 📱 Phone Number Authentication

- **KG Market**: `+996 XXX XXX XXX` format
- **US Market**: `+1 (XXX) XXX-XXXX` format
- **SMS Verification**: 6-digit codes with market-specific expiry times
- **Rate Limiting**: Prevents abuse with configurable limits

### 🌍 Multi-Market Support

- **Separate Databases**: Independent databases for each market
- **Market Detection**: Automatic detection from phone numbers
- **Market Override**: Manual market selection via headers
- **Currency Support**: сом (KGS) for KG, $ (USD) for US
- **Language Support**: Russian for KG, English for US

### 🔐 Security Features

- **JWT Tokens**: Secure authentication tokens
- **Token Verification**: Real-time token validation
- **Rate Limiting**: Protection against brute force attacks
- **Input Validation**: Comprehensive request validation

## 🏗️ Architecture

### 📁 Project Structure

```
src/app_01/
├── db/
│   ├── market_db.py              # Multi-market database manager
│   ├── marque_db_kg.py          # KG database config
│   └── marque_db_us.py          # US database config
├── models/users/
│   ├── market_user.py           # Market-aware user models
│   ├── market_phone_verification.py  # Phone verification models
│   ├── market_user_address.py   # Address models
│   └── market_user_payment_method.py  # Payment method models
├── schemas/
│   └── auth.py                  # Pydantic schemas
├── services/
│   └── auth_service.py          # Business logic
├── routers/
│   └── auth_router.py           # FastAPI endpoints
├── tests/
│   ├── test_auth_models.py      # Model tests
│   └── test_auth_integration.py # Integration tests
├── config.py                    # Application settings
└── main.py                      # FastAPI application
```

### 🗄️ Database Schema

#### KG Market Tables

- `users` - User accounts with KG-specific fields
- `phone_verifications` - SMS verification codes
- `user_addresses` - Delivery addresses (KG format)
- `user_payment_methods` - Payment methods (Visa, Mastercard, Элкарт)
- `user_notifications` - User notifications

#### US Market Tables

- `users` - User accounts with US-specific fields
- `phone_verifications` - SMS verification codes
- `user_addresses` - Delivery addresses (US format)
- `user_payment_methods` - Payment methods (Visa, Mastercard, PayPal)
- `user_notifications` - User notifications

## 🚀 Quick Start

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database URLs
```

### 2. Database Setup

```bash
# Run migrations for KG market
alembic upgrade head

# Run migrations for US market
alembic upgrade head
```

### 3. Run Tests (TDD Approach)

```bash
# Run all tests
python run_tests.py

# Run specific test suites
pytest src/app_01/tests/test_auth_models.py -v
pytest src/app_01/tests/test_auth_integration.py -v
```

### 4. Start the API

```bash
# Development server
python -m src.app_01.main

# Production server
uvicorn src.app_01.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

### 🔑 Authentication Endpoints

#### Send Verification Code

```http
POST /api/v1/auth/send-code
Content-Type: application/json

{
  "phone_number": "+996505325311"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Verification code sent successfully",
  "phone_number": "+996 505 325 311",
  "market": "kg",
  "language": "ru",
  "expires_in_minutes": 10
}
```

#### Verify Phone Code

```http
POST /api/v1/auth/verify-code
Content-Type: application/json

{
  "phone_number": "+996505325311",
  "verification_code": "123456"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Phone number verified successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": 1,
  "market": "kg",
  "is_new_user": true
}
```

#### Get User Profile

```http
GET /api/v1/auth/profile
Authorization: Bearer <token>
```

**Response:**

```json
{
  "id": 1,
  "phone_number": "+996505325311",
  "formatted_phone": "+996 505 325 311",
  "full_name": "Анна Ахматова",
  "profile_image_url": null,
  "is_verified": true,
  "market": "kg",
  "language": "ru",
  "country": "Kyrgyzstan",
  "currency": "сом",
  "currency_code": "KGS",
  "last_login": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-15T09:00:00Z"
}
```

#### Update User Profile

```http
PUT /api/v1/auth/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "full_name": "Анна Петровна Ахматова",
  "profile_image_url": "https://example.com/profile.jpg"
}
```

#### Verify Token

```http
GET /api/v1/auth/verify-token
Authorization: Bearer <token>
```

#### Get Supported Markets

```http
GET /api/v1/auth/markets
```

**Response:**

```json
{
  "supported_markets": [
    {
      "market": "kg",
      "country": "Kyrgyzstan",
      "currency": "сом",
      "currency_code": "KGS",
      "language": "ru",
      "phone_prefix": "+996",
      "phone_format": "+996 XXX XXX XXX"
    },
    {
      "market": "us",
      "country": "United States",
      "currency": "$",
      "currency_code": "USD",
      "language": "en",
      "phone_prefix": "+1",
      "phone_format": "+1 (XXX) XXX-XXXX"
    }
  ],
  "default_market": "kg"
}
```

## 🌍 Market Differences

### 📱 Phone Numbers

| Market | Format              | Example             | Validation      |
| ------ | ------------------- | ------------------- | --------------- |
| KG     | `+996 XXX XXX XXX`  | `+996 505 325 311`  | 13 digits total |
| US     | `+1 (XXX) XXX-XXXX` | `+1 (555) 123-4567` | 12 digits total |

### 💰 Currencies

| Market | Currency | Code | Format     |
| ------ | -------- | ---- | ---------- |
| KG     | сом      | KGS  | `2999 сом` |
| US     | $        | USD  | `$29.99`   |

### 🏠 Addresses

| Market | Fields                                    | Example                                               |
| ------ | ----------------------------------------- | ----------------------------------------------------- |
| KG     | Street, Building, Apartment, City, Region | `ул. Юнусалиева, 34, кв. 12, Бишкек, Чуйская область` |
| US     | Street Address, City, State, ZIP Code     | `123 Main St, New York, NY 10001`                     |

### 💳 Payment Methods

| Market | Supported Methods                                               |
| ------ | --------------------------------------------------------------- |
| KG     | Visa, Mastercard, Элкарт, Cash on Delivery, Bank Transfer       |
| US     | Visa, Mastercard, Amex, Discover, PayPal, Apple Pay, Google Pay |

## 🧪 Testing

### TDD Approach

The system follows Test-Driven Development (TDD) principles:

1. **Write Tests First** - Tests define expected behavior
2. **Implement Features** - Code is written to pass tests
3. **Refactor** - Code is improved while maintaining test coverage

### Test Structure

- **Model Tests** - Test database models and business logic
- **Integration Tests** - Test complete API workflows
- **Coverage Reports** - Ensure comprehensive test coverage

### Running Tests

```bash
# Run all tests with coverage
python run_tests.py

# Run specific test files
pytest src/app_01/tests/test_auth_models.py -v
pytest src/app_01/tests/test_auth_integration.py -v

# Run with coverage report
pytest src/app_01/tests/ --cov=src.app_01 --cov-report=html
```

## 🔧 Configuration

### Environment Variables

```bash
# Database URLs
DATABASE_URL_MARQUE_KG=postgresql://user:password@localhost/marque_kg_db
DATABASE_URL_MARQUE_US=postgresql://user:password@localhost/marque_us_db

# JWT Settings
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMS Settings (Production)
SMS_API_KEY=your-sms-api-key
SMS_API_URL=https://api.sms-provider.com

# Rate Limiting
MAX_VERIFICATION_ATTEMPTS=3
VERIFICATION_ATTEMPTS_WINDOW=15
```

### Market Configuration

Markets are configured in `src/app_01/db/market_db.py`:

```python
KG_CONFIG = {
    "currency": "сом",
    "currency_code": "KGS",
    "phone_prefix": "+996",
    "language": "ru",
    "country": "Kyrgyzstan",
    "tax_rate": 0.12,
    # ... more settings
}

US_CONFIG = {
    "currency": "$",
    "currency_code": "USD",
    "phone_prefix": "+1",
    "language": "en",
    "country": "United States",
    "tax_rate": 0.08,
    # ... more settings
}
```

## 🚀 Deployment

### Production Checklist

- [ ] Set strong JWT secret key
- [ ] Configure production database URLs
- [ ] Set up SMS service provider
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Run database migrations
- [ ] Deploy with HTTPS
- [ ] Set up rate limiting
- [ ] Configure backup strategies

### Docker Support

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

CMD ["uvicorn", "src.app_01.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Monitoring

### Health Checks

```http
GET /health
GET /api/v1/auth/health
```

### Logging

The system includes comprehensive logging:

- Authentication events
- Error tracking
- Performance metrics
- Market-specific analytics

## 🤝 Contributing

### Development Workflow

1. Write tests first (TDD)
2. Implement features to pass tests
3. Ensure all tests pass
4. Add documentation
5. Submit pull request

### Code Standards

- Follow PEP 8 style guide
- Use type hints
- Write comprehensive docstrings
- Maintain test coverage above 90%

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

---

**Built with ❤️ for multi-market e-commerce applications**
