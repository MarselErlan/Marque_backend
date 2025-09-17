# Marque E-commerce Backend

A FastAPI-based e-commerce backend for the Marque fashion/clothing platform.

## Project Structure

```
src/app_01/
├── db/                 # Database configuration and connection
├── models/             # SQLAlchemy models
├── routers/            # API route handlers
├── schemas/            # Pydantic schemas for request/response
├── services/           # Business logic
├── tests/              # Test files
└── utils/              # Utility functions
```

## Database Models

### Core Models

#### Product

Represents items in the catalog with the following fields:

- `id` (PK): Primary key
- `brand` (string): Product brand (e.g., "H&M")
- `title` (string): Product title
- `slug` (string, unique): URL-friendly identifier
- `description` (text): Product description
- `sold_count` (int, default=0): Number of units sold
- `rating_avg` (float): Average rating (0.0-5.0)
- `rating_count` (int, default=0): Number of reviews
- `attributes` (JSONB): Product attributes like gender, season, composition, article
- `created_at`, `updated_at`: Timestamps

#### SKU (Stock Keeping Unit)

Represents specific product variants:

- `id` (PK): Primary key
- `product_id` (FK): Reference to Product
- `sku_code` (string, unique): Unique SKU identifier (e.g., "Артикул/236412")
- `size` (string): Size (e.g., "RUS 40")
- `color` (string): Color (e.g., "black")
- `price` (decimal): Price in som
- `stock` (int): Available quantity
- `is_active` (bool): Whether SKU is active for sale

#### ProductAsset

Stores product images and videos:

- `id` (PK): Primary key
- `product_id` (FK): Reference to Product
- `url` (string): Asset URL
- `type` (string): "image" or "video"

#### Review

Product reviews and ratings:

- `id` (PK): Primary key
- `product_id` (FK): Reference to Product
- `user_id` (FK): Reference to User
- `rating` (int): Rating 1-5
- `text` (text): Review text
- `created_at`: Timestamp

### User Management

#### User

User accounts and authentication:

- `id` (PK): Primary key
- `email` (string, unique): User email
- `username` (string, unique): Username
- `hashed_password` (string): Encrypted password
- `full_name` (string): User's full name
- `is_active` (bool): Account status
- `is_verified` (bool): Email verification status
- `created_at`, `updated_at`: Timestamps

### Shopping & Orders

#### CartOrder

Shopping cart and order management:

- `id` (PK): Primary key
- `user_id` (FK): Reference to User
- `sku_id` (FK): Reference to SKU
- `quantity` (int): Quantity in cart/order
- `price` (decimal): Price at time of adding to cart
- `is_ordered` (bool): Whether item has been ordered
- `order_date` (datetime): When order was placed
- `created_at`, `updated_at`: Timestamps

### Analytics

#### Interaction

User behavior tracking:

- `id` (PK): Primary key
- `user_id` (FK, nullable): Reference to User (nullable for anonymous users)
- `product_id` (FK): Reference to Product
- `interaction_type` (string): Type of interaction ("view", "wishlist", "search", "click")
- `metadata` (string): Additional data (search query, page URL, etc.)
- `created_at`: Timestamp

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Set up database:

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:password@localhost/marque_db"

# Run migrations (after setting up Alembic)
alembic upgrade head
```

3. Run the example:

```bash
python example_usage.py
```

## Features

- ✅ Product catalog with brands, titles, descriptions
- ✅ SKU management with sizes, colors, pricing
- ✅ Product assets (images/videos)
- ✅ User reviews and ratings
- ✅ Shopping cart functionality
- ✅ Order management
- ✅ User interaction tracking
- ✅ Database relationships and constraints
- ✅ Alembic migration support

## API Endpoints (To be implemented)

- Product catalog browsing
- Product detail pages
- User authentication
- Shopping cart management
- Order processing
- Review system
- Search functionality
