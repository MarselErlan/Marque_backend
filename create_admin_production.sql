-- Create admin user in production database
-- Username: admin_marque
-- Password: python123

INSERT INTO admins (
    username, 
    email, 
    hashed_password, 
    full_name, 
    is_super_admin, 
    is_active, 
    admin_role,
    permissions,
    created_at
) VALUES (
    'admin',
    'admin@marque.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7TL.Y1wmy.',
    'Super Administrator',
    true,
    true,
    'super_admin',
    '{"orders": ["view", "update", "delete"], "products": ["create", "update", "delete"], "users": ["view", "update"], "admins": ["create", "update"]}',
    NOW()
)
ON CONFLICT (username) DO NOTHING;

-- Verify admin was created
SELECT id, username, email, is_super_admin, admin_role, is_active 
FROM admins 
WHERE username = 'admin';
