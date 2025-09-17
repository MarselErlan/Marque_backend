"""Initial migration for multi-market tables

Revision ID: 71d0a21d5609
Revises: 
Create Date: 2025-09-16 21:36:52.467375

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '71d0a21d5609'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('profile_image_url', sa.String(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('market', sa.String(length=10), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('hashed_password', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_phone_number'), 'users', ['phone_number'], unique=True)
    op.create_index(op.f('ix_users_market'), 'users', ['market'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create phone_verifications table
    op.create_table('phone_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('verification_code', sa.String(length=10), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('market', sa.String(length=10), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phone_verifications_id'), 'phone_verifications', ['id'], unique=False)
    op.create_index(op.f('ix_phone_verifications_user_id'), 'phone_verifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_phone_verifications_phone_number'), 'phone_verifications', ['phone_number'], unique=False)
    op.create_index(op.f('ix_phone_verifications_market'), 'phone_verifications', ['market'], unique=False)

    # Create user_addresses table
    op.create_table('user_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('address_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('full_address', sa.Text(), nullable=False),
        sa.Column('street', sa.String(length=200), nullable=True),
        sa.Column('building', sa.String(length=50), nullable=True),
        sa.Column('apartment', sa.String(length=20), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('district', sa.String(length=100), nullable=True),
        sa.Column('street_address', sa.String(length=200), nullable=True),
        sa.Column('street_number', sa.String(length=20), nullable=True),
        sa.Column('street_name', sa.String(length=200), nullable=True),
        sa.Column('apartment_unit', sa.String(length=20), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('market', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_addresses_id'), 'user_addresses', ['id'], unique=False)
    op.create_index(op.f('ix_user_addresses_user_id'), 'user_addresses', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_addresses_market'), 'user_addresses', ['market'], unique=False)

    # Create user_payment_methods table
    op.create_table('user_payment_methods',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('payment_type', sa.String(length=20), nullable=False),
        sa.Column('card_type', sa.String(length=20), nullable=True),
        sa.Column('card_number_masked', sa.String(length=20), nullable=True),
        sa.Column('card_holder_name', sa.String(length=100), nullable=True),
        sa.Column('expiry_month', sa.String(length=2), nullable=True),
        sa.Column('expiry_year', sa.String(length=4), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('paypal_email', sa.String(length=255), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('market', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_payment_methods_id'), 'user_payment_methods', ['id'], unique=False)
    op.create_index(op.f('ix_user_payment_methods_user_id'), 'user_payment_methods', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_payment_methods_market'), 'user_payment_methods', ['market'], unique=False)

    # Create user_notifications table
    op.create_table('user_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('notification_type', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('order_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_notifications_id'), 'user_notifications', ['id'], unique=False)
    op.create_index(op.f('ix_user_notifications_user_id'), 'user_notifications', ['user_id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_user_notifications_user_id'), table_name='user_notifications')
    op.drop_index(op.f('ix_user_notifications_id'), table_name='user_notifications')
    op.drop_table('user_notifications')
    
    op.drop_index(op.f('ix_user_payment_methods_market'), table_name='user_payment_methods')
    op.drop_index(op.f('ix_user_payment_methods_user_id'), table_name='user_payment_methods')
    op.drop_index(op.f('ix_user_payment_methods_id'), table_name='user_payment_methods')
    op.drop_table('user_payment_methods')
    
    op.drop_index(op.f('ix_user_addresses_market'), table_name='user_addresses')
    op.drop_index(op.f('ix_user_addresses_user_id'), table_name='user_addresses')
    op.drop_index(op.f('ix_user_addresses_id'), table_name='user_addresses')
    op.drop_table('user_addresses')
    
    op.drop_index(op.f('ix_phone_verifications_market'), table_name='phone_verifications')
    op.drop_index(op.f('ix_phone_verifications_phone_number'), table_name='phone_verifications')
    op.drop_index(op.f('ix_phone_verifications_user_id'), table_name='phone_verifications')
    op.drop_index(op.f('ix_phone_verifications_id'), table_name='phone_verifications')
    op.drop_table('phone_verifications')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_market'), table_name='users')
    op.drop_index(op.f('ix_users_phone_number'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')