"""Add banners table for main page

Revision ID: 6994966bbf08
Revises: 88ebdddde521
Create Date: 2025-10-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6994966bbf08'
down_revision = '88ebdddde521'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create banners table
    op.create_table(
        'banners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('banner_type', sa.Enum('SALE', 'MODEL', name='bannertype'), nullable=False),
        sa.Column('link_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index(op.f('ix_banners_id'), 'banners', ['id'], unique=False)
    op.create_index(op.f('ix_banners_banner_type'), 'banners', ['banner_type'], unique=False)
    op.create_index(op.f('ix_banners_is_active'), 'banners', ['is_active'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_banners_is_active'), table_name='banners')
    op.drop_index(op.f('ix_banners_banner_type'), table_name='banners')
    op.drop_index(op.f('ix_banners_id'), table_name='banners')
    
    # Drop table
    op.drop_table('banners')
    
    # Drop enum type
    op.execute('DROP TYPE bannertype')
