"""add_product_image_columns

Revision ID: 8f7297e45fcb
Revises: 1bdb7f450f83
Create Date: 2025-10-14 01:13:55.864047

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f7297e45fcb'
down_revision = '1bdb7f450f83'
branch_labels = None
depends_on = None


def upgrade():
    # Add main_image column to products table
    op.add_column('products', sa.Column('main_image', sa.String(length=500), nullable=True))
    
    # Add additional_images JSON column to products table
    op.add_column('products', sa.Column('additional_images', sa.JSON(), nullable=True))


def downgrade():
    # Remove additional_images column
    op.drop_column('products', 'additional_images')
    
    # Remove main_image column
    op.drop_column('products', 'main_image')