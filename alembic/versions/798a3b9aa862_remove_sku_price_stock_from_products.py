"""add_sku_code_to_products

Revision ID: 798a3b9aa862
Revises: a04176727d8f
Create Date: 2025-10-19 23:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '798a3b9aa862'
down_revision = 'a04176727d8f'
branch_labels = None
depends_on = None


def upgrade():
    # Add sku_code to products table (base SKU for product)
    # SKU variants will auto-generate their codes as: {base_sku_code}-{size}-{color}
    
    # Add column as nullable first
    op.add_column('products', sa.Column('sku_code', sa.String(length=50), nullable=True))
    
    # Set default values for existing products
    op.execute("""
        UPDATE products 
        SET sku_code = 'SKU-' || id
        WHERE sku_code IS NULL
    """)
    
    # Make column non-nullable
    op.alter_column('products', 'sku_code', nullable=False)
    
    # Create unique index
    op.create_index('ix_products_sku_code', 'products', ['sku_code'], unique=True)


def downgrade():
    # Remove sku_code if needed (for rollback)
    op.drop_index('ix_products_sku_code', table_name='products')
    op.drop_column('products', 'sku_code')
