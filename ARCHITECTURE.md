# 🏗️ Marque E-commerce Backend - Architecture Documentation

## 📋 Overview

This document outlines the comprehensive architecture of the Marque e-commerce backend system, designed to support multi-market operations with clean separation of concerns, scalability, and maintainability.

## 🎯 Architecture Principles

### 1. **Clean Architecture**

- **Domain-Driven Design (DDD)**: Business logic separated from infrastructure
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Single Responsibility**: Each component has one reason to change

### 2. **Multi-Market Support**

- **Market Isolation**: Separate databases and configurations per market
- **Market Detection**: Automatic routing based on phone numbers/domains
- **Localization**: Language, currency, and format support per market

### 3. **Scalability & Performance**

- **Horizontal Scaling**: Stateless services for easy scaling
- **Caching Strategy**: Redis for session and data caching
- **Database Optimization**: Proper indexing and query optimization

## 🏛️ Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    🌐 Presentation Layer                    │
│  FastAPI Routes, Middleware, Authentication, CORS, etc.     │
├─────────────────────────────────────────────────────────────┤
│                    🔧 Application Layer                     │
│  Services, Use Cases, Business Logic, Validation           │
├─────────────────────────────────────────────────────────────┤
│                    🏢 Domain Layer                          │
│  Models, Entities, Value Objects, Business Rules           │
├─────────────────────────────────────────────────────────────┤
│                    🗄️ Infrastructure Layer                 │
│  Database, External APIs, File Storage, Email, SMS         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
src/app_01/
├── 📁 core/                    # Core business logic
│   ├── config/                 # Configuration management
│   ├── exceptions/              # Custom exceptions
│   ├── middleware/              # Custom middleware
│   ├── security/               # Security utilities
│   └── utils/                  # Core utilities
├── 📁 domain/                  # Domain models and business rules
│   ├── entities/               # Domain entities
│   ├── value_objects/          # Value objects
│   ├── repositories/           # Repository interfaces
│   └── services/               # Domain services
├── 📁 infrastructure/          # Infrastructure implementations
│   ├── database/               # Database configurations
│   ├── external/               # External service integrations
│   ├── storage/                # File storage
│   └── messaging/              # Email, SMS, notifications
├── 📁 application/             # Application services
│   ├── services/               # Application services
│   ├── use_cases/              # Use case implementations
│   ├── dto/                    # Data Transfer Objects
│   └── interfaces/             # Service interfaces
├── 📁 presentation/            # API layer
│   ├── api/                    # FastAPI routes
│   ├── middleware/              # Request/Response middleware
│   ├── schemas/                # Pydantic schemas
│   └── dependencies/            # Dependency injection
├── 📁 admin/                   # Admin interface
│   ├── views/                  # SQLAdmin views
│   ├── auth/                   # Admin authentication
│   └── permissions/            # Permission management
└── 📁 tests/                   # Test suites
    ├── unit/                   # Unit tests
    ├── integration/            # Integration tests
    ├── e2e/                    # End-to-end tests
    └── fixtures/               # Test fixtures
```

## 🔧 Core Components

### 1. **Configuration Management**

```python
# core/config/settings.py
class Settings:
    # Database configurations
    DATABASE_URL_KG: str
    DATABASE_URL_US: str

    # Security settings
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Market configurations
    SUPPORTED_MARKETS: List[str]
    DEFAULT_MARKET: str

    # External services
    REDIS_URL: str
    SMS_SERVICE_URL: str
    EMAIL_SERVICE_URL: str
```

### 2. **Dependency Injection Container**

```python
# core/container.py
class Container:
    def __init__(self):
        self._services = {}
        self._singletons = {}

    def register(self, interface, implementation, singleton=False):
        """Register a service implementation"""

    def get(self, interface):
        """Get service instance"""

    def wire(self, modules):
        """Wire dependencies to modules"""
```

### 3. **Repository Pattern**

```python
# domain/repositories/user_repository.py
class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_phone(self, phone: str, market: Market) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass
```

### 4. **Service Layer**

```python
# application/services/user_service.py
class UserService:
    def __init__(self, user_repo: UserRepository, auth_service: AuthService):
        self.user_repo = user_repo
        self.auth_service = auth_service

    async def register_user(self, phone: str, market: Market) -> UserRegistrationResult:
        """Register new user with phone verification"""

    async def verify_phone(self, phone: str, code: str) -> VerificationResult:
        """Verify phone number with SMS code"""
```

## 🌍 Multi-Market Architecture

### Market Detection Strategy

```python
# core/market_detection.py
class MarketDetector:
    @staticmethod
    def detect_from_phone(phone: str) -> Market:
        """Detect market from phone number"""

    @staticmethod
    def detect_from_domain(domain: str) -> Market:
        """Detect market from domain"""

    @staticmethod
    def detect_from_header(headers: dict) -> Market:
        """Detect market from request headers"""
```

### Market-Specific Configurations

```python
# core/config/market_config.py
class MarketConfig:
    KG_CONFIG = {
        "currency": "сом",
        "currency_code": "KGS",
        "language": "ru",
        "phone_prefix": "+996",
        "timezone": "Asia/Bishkek",
        "tax_rate": 0.12,
        "shipping_zones": ["Бишкек", "Ош", "Джалал-Абад"]
    }

    US_CONFIG = {
        "currency": "$",
        "currency_code": "USD",
        "language": "en",
        "phone_prefix": "+1",
        "timezone": "America/New_York",
        "tax_rate": 0.08,
        "shipping_zones": ["Continental US", "Alaska", "Hawaii"]
    }
```

## 🔐 Security Architecture

### Authentication & Authorization

```python
# core/security/auth.py
class AuthManager:
    def create_access_token(self, user_id: int, market: Market) -> str:
        """Create JWT access token"""

    def verify_token(self, token: str) -> TokenPayload:
        """Verify and decode JWT token"""

    def refresh_token(self, refresh_token: str) -> str:
        """Refresh access token"""
```

### Rate Limiting

```python
# core/middleware/rate_limiting.py
class RateLimiter:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check if request is within rate limit"""
```

## 📊 Data Architecture

### Database Strategy

```python
# infrastructure/database/manager.py
class DatabaseManager:
    def __init__(self):
        self.engines = {}
        self.session_factories = {}

    def get_session(self, market: Market) -> AsyncSession:
        """Get database session for market"""

    def get_engine(self, market: Market) -> AsyncEngine:
        """Get database engine for market"""
```

### Repository Implementations

```python
# infrastructure/database/repositories/user_repository_impl.py
class UserRepositoryImpl(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Create user in database"""

    async def get_by_phone(self, phone: str, market: Market) -> Optional[User]:
        """Get user by phone number"""
```

## 🚀 API Architecture

### Route Organization

```python
# presentation/api/v1/routes.py
router = APIRouter(prefix="/api/v1")

# Authentication routes
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# User routes
router.include_router(user_router, prefix="/users", tags=["Users"])

# Product routes
router.include_router(product_router, prefix="/products", tags=["Products"])

# Order routes
router.include_router(order_router, prefix="/orders", tags=["Orders"])
```

### Middleware Stack

```python
# presentation/middleware/stack.py
def setup_middleware(app: FastAPI):
    # CORS middleware
    app.add_middleware(CORSMiddleware, ...)

    # Rate limiting middleware
    app.add_middleware(RateLimitMiddleware, ...)

    # Request logging middleware
    app.add_middleware(LoggingMiddleware, ...)

    # Market detection middleware
    app.add_middleware(MarketDetectionMiddleware, ...)
```

## 🧪 Testing Architecture

### Test Organization

```python
# tests/conftest.py
@pytest.fixture
async def test_db_session():
    """Test database session"""

@pytest.fixture
def test_client():
    """Test FastAPI client"""

@pytest.fixture
def mock_auth_service():
    """Mock authentication service"""
```

### Test Categories

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete user workflows
- **Performance Tests**: Test system performance under load

## 📈 Monitoring & Observability

### Health Checks

```python
# core/health/checker.py
class HealthChecker:
    async def check_database(self, market: Market) -> HealthStatus:
        """Check database connectivity"""

    async def check_redis(self) -> HealthStatus:
        """Check Redis connectivity"""

    async def check_external_services(self) -> HealthStatus:
        """Check external service availability"""
```

### Logging Strategy

```python
# core/logging/logger.py
class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def log_request(self, request: Request, response: Response):
        """Log HTTP request/response"""

    def log_business_event(self, event: str, data: dict):
        """Log business events"""
```

## 🔄 Deployment Architecture

### Environment Configuration

```yaml
# docker-compose.yml
version: "3.8"
services:
  app:
    build: .
    environment:
      - DATABASE_URL_KG=${DATABASE_URL_KG}
      - DATABASE_URL_US=${DATABASE_URL_US}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - redis
      - postgres-kg
      - postgres-us

  redis:
    image: redis:alpine

  postgres-kg:
    image: postgres:13
    environment:
      - POSTGRES_DB=marque_kg

  postgres-us:
    image: postgres:13
    environment:
      - POSTGRES_DB=marque_us
```

## 🎯 Benefits of This Architecture

### 1. **Maintainability**

- Clear separation of concerns
- Easy to modify individual components
- Consistent patterns throughout

### 2. **Testability**

- Dependency injection enables easy mocking
- Clear interfaces for testing
- Isolated components for unit testing

### 3. **Scalability**

- Stateless services for horizontal scaling
- Database per market for isolation
- Caching layer for performance

### 4. **Flexibility**

- Easy to add new markets
- Pluggable components
- Configuration-driven behavior

### 5. **Security**

- Centralized authentication/authorization
- Rate limiting and input validation
- Secure by default patterns

## 🚀 Next Steps

1. **Implement Core Components**: Start with configuration management and dependency injection
2. **Refactor Existing Code**: Gradually move to new architecture
3. **Add Monitoring**: Implement health checks and logging
4. **Performance Optimization**: Add caching and optimize queries
5. **Documentation**: Create API documentation and deployment guides

This architecture provides a solid foundation for building a scalable, maintainable, and secure e-commerce platform that can grow with your business needs.
