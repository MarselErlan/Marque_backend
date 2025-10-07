"""add_market_columns_to_user

Revision ID: 22ed994e8125
Revises: bd96af0580b1
Create Date: 2025-10-06 19:21:27.372989

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '22ed994e8125'
down_revision = 'bd96af0580b1'
branch_labels = None
depends_on = None


def upgrade():
    # Add market-related columns to users table
    op.add_column('users', sa.Column('market', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('language', sa.String(length=10), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True))
    
    # Set default market to 'kg' for existing users
    op.execute("UPDATE users SET market = 'kg', language = 'ru', country = 'Kyrgyzstan' WHERE market IS NULL")
    
    # Create indexes for better query performance
    op.create_index('ix_users_market', 'users', ['market'])


def downgrade():
    # Remove indexes
    op.drop_index('ix_users_market', 'users')
    
    # Remove columns
    op.drop_column('users', 'country')
    op.drop_column('users', 'language')
    op.drop_column('users', 'market')