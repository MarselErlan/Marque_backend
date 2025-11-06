"""
Alembic environment configuration for multi-market database migrations
"""

from logging.config import fileConfig
import os
import sys
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

from src.app_01.core.config import settings
from src.app_01.db import Base

# Import ALL models so Alembic can detect them
# Users
from src.app_01.models.users.user import User
from src.app_01.models.users.interaction import Interaction
from src.app_01.models.users.phone_verification import PhoneVerification
from src.app_01.models.users.user_address import UserAddress
from src.app_01.models.users.user_payment_method import UserPaymentMethod
from src.app_01.models.users.user_notification import UserNotification
from src.app_01.models.users.wishlist import Wishlist, WishlistItem

# Products
from src.app_01.models.products.product import Product
from src.app_01.models.products.brand import Brand
from src.app_01.models.products.category import Category, Subcategory
from src.app_01.models.products.sku import SKU
from src.app_01.models.products.product_asset import ProductAsset
from src.app_01.models.products.review import Review
from src.app_01.models.products.product_attribute import ProductAttribute
from src.app_01.models.products.product_filter import ProductFilter, ProductSeason, ProductMaterial, ProductStyle, ProductDiscount, ProductSearch

# Orders
from src.app_01.models.orders.cart_order import CartOrder
from src.app_01.models.orders.order import Order, OrderStatus
from src.app_01.models.orders.order_item import OrderItem
from src.app_01.models.orders.order_status_history import OrderStatusHistory
from src.app_01.models.orders.cart import Cart, CartItem

# Admins
from src.app_01.models.admins.admin import Admin
from src.app_01.models.admins.admin_log import AdminLog
from src.app_01.models.admins.order_management.order_admin_stats import OrderAdminStats
from src.app_01.models.admins.order_management.order_management_admin import OrderManagementAdmin

# Banners
from src.app_01.models.banners.banner import Banner

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

def get_url():
    """Get database URL from environment or config"""
    # Check if we want to target US database
    target_db = os.getenv("ALEMBIC_TARGET_DB", "KG")
    
    if target_db == "US":
        database_url = settings.database.url_us
        print("🚀 Targeting US database for migrations")
    else:
        database_url = settings.database.url_kg
        print("🚀 Targeting KG database for migrations")
    
    if not database_url:
        raise Exception(f"Database URL for {target_db} market not found in .env file or config")
    
    return database_url

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Create engine configuration
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()