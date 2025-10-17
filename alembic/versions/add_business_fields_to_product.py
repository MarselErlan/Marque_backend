"""add_business_fields_to_product

Revision ID: business_fields_001
Revises: bd96af0580b1
Create Date: 2025-10-17

Description:
    - Added view_count for analytics
    - Added is_new, is_trending flags for product curation
    - Added meta_title, meta_description, meta_keywords for SEO
    - Added tags for better discoverability
    - Added low_stock_threshold for inventory management
    - Added indexes on important columns for performance
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON


# revision identifiers, used by Alembic.
revision = 'business_fields_001'
down_revision = 'bd96af0580b1'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('products', sa.Column('view_count', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('products', sa.Column('is_new', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('products', sa.Column('is_trending', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('products', sa.Column('meta_title', sa.String(length=255), nullable=True))
    op.add_column('products', sa.Column('meta_description', sa.Text(), nullable=True))
    op.add_column('products', sa.Column('meta_keywords', sa.Text(), nullable=True))
    op.add_column('products', sa.Column('tags', JSON, nullable=True))
    op.add_column('products', sa.Column('low_stock_threshold', sa.Integer(), nullable=True, server_default='5'))
    
    # Add indexes for performance (some may already exist, wrapped in try/except in raw SQL)
    # These indexes dramatically improve query performance for common operations
    op.create_index('idx_product_title', 'products', ['title'], unique=False, if_not_exists=True)
    op.create_index('idx_product_sold_count', 'products', ['sold_count'], unique=False, if_not_exists=True)
    op.create_index('idx_product_rating_avg', 'products', ['rating_avg'], unique=False, if_not_exists=True)
    op.create_index('idx_product_is_active', 'products', ['is_active'], unique=False, if_not_exists=True)
    op.create_index('idx_product_is_featured', 'products', ['is_featured'], unique=False, if_not_exists=True)
    op.create_index('idx_product_created_at', 'products', ['created_at'], unique=False, if_not_exists=True)
    
    # Composite indexes for common query patterns
    op.create_index('idx_product_active_featured', 'products', ['is_active', 'is_featured'], unique=False, if_not_exists=True)
    op.create_index('idx_product_category_active', 'products', ['category_id', 'is_active'], unique=False, if_not_exists=True)
    op.create_index('idx_product_subcategory_active', 'products', ['subcategory_id', 'is_active'], unique=False, if_not_exists=True)
    op.create_index('idx_product_brand_active', 'products', ['brand_id', 'is_active'], unique=False, if_not_exists=True)
    
    # Descending indexes for sorting (PostgreSQL specific)
    op.execute('CREATE INDEX IF NOT EXISTS idx_product_sold_count_desc ON products (sold_count DESC)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_product_rating_desc ON products (rating_avg DESC)')
    op.execute('CREATE INDEX IF NOT EXISTS idx_product_created_desc ON products (created_at DESC)')
    
    # Update existing products: set default values for new columns
    op.execute("UPDATE products SET view_count = 0 WHERE view_count IS NULL")
    op.execute("UPDATE products SET is_new = true WHERE is_new IS NULL")
    op.execute("UPDATE products SET is_trending = false WHERE is_trending IS NULL")
    op.execute("UPDATE products SET low_stock_threshold = 5 WHERE low_stock_threshold IS NULL")
    
    # Auto-populate meta fields from existing data (basic SEO)
    op.execute("""
        UPDATE products 
        SET meta_title = title 
        WHERE meta_title IS NULL AND title IS NOT NULL
    """)
    op.execute("""
        UPDATE products 
        SET meta_description = SUBSTRING(description, 1, 160) 
        WHERE meta_description IS NULL AND description IS NOT NULL
    """)
    
    # Make NOT NULL after setting defaults
    op.alter_column('products', 'view_count', nullable=False)
    op.alter_column('products', 'is_new', nullable=False)
    op.alter_column('products', 'is_trending', nullable=False)
    op.alter_column('products', 'low_stock_threshold', nullable=False)


def downgrade():
    # Remove indexes
    op.drop_index('idx_product_created_desc', table_name='products', if_exists=True)
    op.drop_index('idx_product_rating_desc', table_name='products', if_exists=True)
    op.drop_index('idx_product_sold_count_desc', table_name='products', if_exists=True)
    op.drop_index('idx_product_brand_active', table_name='products', if_exists=True)
    op.drop_index('idx_product_subcategory_active', table_name='products', if_exists=True)
    op.drop_index('idx_product_category_active', table_name='products', if_exists=True)
    op.drop_index('idx_product_active_featured', table_name='products', if_exists=True)
    op.drop_index('idx_product_created_at', table_name='products', if_exists=True)
    op.drop_index('idx_product_is_featured', table_name='products', if_exists=True)
    op.drop_index('idx_product_is_active', table_name='products', if_exists=True)
    op.drop_index('idx_product_rating_avg', table_name='products', if_exists=True)
    op.drop_index('idx_product_sold_count', table_name='products', if_exists=True)
    op.drop_index('idx_product_title', table_name='products', if_exists=True)
    
    # Remove columns
    op.drop_column('products', 'low_stock_threshold')
    op.drop_column('products', 'tags')
    op.drop_column('products', 'meta_keywords')
    op.drop_column('products', 'meta_description')
    op.drop_column('products', 'meta_title')
    op.drop_column('products', 'is_trending')
    op.drop_column('products', 'is_new')
    op.drop_column('products', 'view_count')

