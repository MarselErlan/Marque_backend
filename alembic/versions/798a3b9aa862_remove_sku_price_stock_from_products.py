"""remove_sku_price_stock_from_products

Revision ID: 798a3b9aa862
Revises: a04176727d8f
Create Date: 2025-10-19 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '798a3b9aa862'
down_revision = 'a04176727d8f'
branch_labels = None
depends_on = None


def upgrade():
    # Remove sku_code, price, and stock_quantity from products table
    # These will be managed through the SKU variants table instead
    
    # Drop index first
    op.drop_index('ix_products_sku_code', table_name='products')
    
    # Drop columns
    op.drop_column('products', 'sku_code')
    op.drop_column('products', 'price')
    op.drop_column('products', 'stock_quantity')


def downgrade():
    # Re-add the columns if needed (for rollback)
    op.add_column('products', sa.Column('sku_code', sa.String(length=50), nullable=True))
    op.add_column('products', sa.Column('price', sa.Float(), nullable=True))
    op.add_column('products', sa.Column('stock_quantity', sa.Integer(), nullable=True))
    
    # Recreate index
    op.create_index('ix_products_sku_code', 'products', ['sku_code'], unique=True)
