# 🔐 SQLAdmin User Creation Guide

## ❓ How to Create Admin Users

SQLAdmin **doesn't have a public signup page** by design (for security). Admin users must be created by:

1. Super Admins (via script)
2. Database administrators
3. Initial setup script

---

## 🚀 Method 1: Quick Create Script (Recommended)

### **Create Default Super Admin**

```bash
python create_admin.py --quick
```

**Default Credentials**:

- Username: `admin`
- Password: `admin123`
- Email: `admin@marque.com`
- Role: Super Admin (full access)

⚠️ **Change password immediately in production!**

---

## 👤 Method 2: Interactive Creation

### **Step 1: Run Interactive Script**

```bash
python create_admin.py
```

### **Step 2: Enter Admin Details**

```
👤 Username: john
🔒 Password: mySecurePass123
📧 Email: john@marque.com
📝 Full Name: John Smith

👔 Select Admin Role:
   1. Website Content Admin (manage products, reviews)
   2. Order Management Admin (manage orders)
   3. Super Admin (full access)
Enter choice (1-3, default: 1): 3
```

### **Step 3: Login**

```
✅ Admin user created successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ID:           1
Username:     john
Email:        john@marque.com
Full Name:    John Smith
Role:         super_admin
Super Admin:  True
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 Login at: http://localhost:8000/admin/login
   Username: john
   Password: mySecurePass123
```

---

## 🐍 Method 3: Python Code

### **In Python Script or Shell**

```python
from passlib.hash import bcrypt
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

# Get database session
db = next(db_manager.get_db_session(Market.KG))

# Create admin
admin = Admin(
    username="newadmin",
    email="newadmin@marque.com",
    hashed_password=bcrypt.hash("password123"),
    full_name="New Administrator",
    is_super_admin=True,
    is_active=True,
    admin_role="super_admin"
)

# Setup default permissions
admin.setup_default_permissions()

# Save
db.add(admin)
db.commit()
db.refresh(admin)

print(f"✅ Admin created: {admin.username}")
db.close()
```

---

## 📊 Method 4: Direct Database Access

### **Using PostgreSQL**

```sql
-- Connect to your database
psql -h metro.proxy.rlwy.net -U postgres -d railway -p 45504

-- Insert admin (password is "admin123" hashed with bcrypt)
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
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7TL.Y1wmy.',  -- "admin123"
    'Super Administrator',
    true,
    true,
    'super_admin',
    'orders.view,orders.update,orders.delete,products.create,products.update,products.delete,users.view,users.update,admins.create,admins.update',
    NOW()
);
```

⚠️ **Note**: The hashed password above is for "admin123". Generate your own with:

```python
from passlib.hash import bcrypt
print(bcrypt.hash("your_password_here"))
```

---

## 👥 Admin Roles Explained

### **1. Super Admin** 🔴

```python
admin_role="super_admin"
is_super_admin=True
```

**Permissions**:

- ✅ Full access to everything
- ✅ Manage orders
- ✅ Manage products
- ✅ Manage users
- ✅ Create/delete other admins
- ✅ Change system settings

**Use Case**: System administrators, founders, CTO

---

### **2. Website Content Admin** 🟢

```python
admin_role="website_content"
is_super_admin=False
```

**Permissions**:

- ✅ Create/edit products
- ✅ Manage product images
- ✅ Moderate reviews
- ✅ Manage categories
- ✅ Update product descriptions
- ❌ Cannot manage orders
- ❌ Cannot manage users
- ❌ Cannot create admins

**Use Case**: Content managers, marketing team, product managers

---

### **3. Order Management Admin** 🟡

```python
admin_role="order_management"
is_super_admin=False
```

**Permissions**:

- ✅ View orders
- ✅ Update order status
- ✅ Process refunds
- ✅ Export order data
- ✅ Contact customers
- ❌ Cannot manage products
- ❌ Cannot manage users
- ❌ Cannot create admins

**Use Case**: Customer service, operations team, fulfillment team

---

## 🔐 Access SQLAdmin Panel

### **1. Start Server**

```bash
uvicorn src.app_01.main:app --reload
```

### **2. Navigate to Admin Panel**

```
http://localhost:8000/admin
```

### **3. Login**

- Enter your username
- Enter your password
- Click "Sign In"

### **4. Access Granted**

You'll be redirected to the admin dashboard where you can:

- Manage products
- View orders
- Manage users
- View analytics

---

## ✅ Verification

### **Check Admin Was Created**

```bash
# Using Python
python -c "
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

db = next(db_manager.get_db_session(Market.KG))
admins = db.query(Admin).all()

print('Current Admins:')
for admin in admins:
    print(f'  - {admin.username} ({admin.email}) - {admin.admin_role}')
"
```

### **Test Login**

```bash
# Start server
uvicorn src.app_01.main:app --reload

# Open browser
open http://localhost:8000/admin/login

# Login with credentials:
# Username: admin
# Password: admin123
```

---

## 🛡️ Security Best Practices

### **1. Change Default Password**

If you used `--quick` mode, **immediately change the password**:

```python
from passlib.hash import bcrypt
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

db = next(db_manager.get_db_session(Market.KG))
admin = db.query(Admin).filter(Admin.username == "admin").first()
admin.hashed_password = bcrypt.hash("new_secure_password_here")
db.commit()
print("✅ Password changed!")
db.close()
```

### **2. Use Strong Passwords**

- Minimum 12 characters
- Mix of uppercase, lowercase, numbers, symbols
- No dictionary words
- Use a password manager

### **3. Limit Super Admin Accounts**

- Only create super admin accounts for trusted personnel
- Use role-based access (content admin, order admin) for most users
- Regularly audit admin accounts

### **4. Enable 2FA (Future)**

Consider adding two-factor authentication in production.

### **5. Monitor Admin Activity**

All admin actions are logged in the `admin_logs` table:

```python
from src.app_01.models.admins.admin_log import AdminLog

db = next(db_manager.get_db_session(Market.KG))
logs = db.query(AdminLog).order_by(AdminLog.created_at.desc()).limit(10).all()

for log in logs:
    print(f"{log.created_at}: {log.admin.username} - {log.action}")
```

---

## 🔧 Troubleshooting

### **Issue: "Username already exists"**

```
❌ Error: Username 'admin' already exists!
```

**Solution**: Use a different username or delete the existing admin:

```python
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

db = next(db_manager.get_db_session(Market.KG))
admin = db.query(Admin).filter(Admin.username == "admin").first()
db.delete(admin)
db.commit()
print("✅ Admin deleted")
db.close()
```

### **Issue: "Email already exists"**

```
❌ Error: Email 'admin@marque.com' already exists!
```

**Solution**: Use a different email address.

### **Issue: "Cannot login with created credentials"**

**Check**:

1. Username is correct (case-sensitive)
2. Password is correct
3. Admin is active (`is_active=True`)
4. Database is correct (KG vs US market)

**Verify**:

```python
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin
from passlib.hash import bcrypt

db = next(db_manager.get_db_session(Market.KG))
admin = db.query(Admin).filter(Admin.username == "your_username").first()

if admin:
    print(f"Admin found: {admin.username}")
    print(f"Is active: {admin.is_active}")
    print(f"Email: {admin.email}")

    # Test password
    test_password = "your_password"
    is_valid = bcrypt.verify(test_password, admin.hashed_password)
    print(f"Password valid: {is_valid}")
else:
    print("Admin not found")
```

### **Issue: "Permission denied"**

**Cause**: Your admin role doesn't have permission for that action.

**Solution**: Either:

1. Use a super admin account
2. Grant permissions to your admin role
3. Change your role to super_admin

```python
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

db = next(db_manager.get_db_session(Market.KG))
admin = db.query(Admin).filter(Admin.username == "your_username").first()

# Make super admin
admin.is_super_admin = True
admin.admin_role = "super_admin"
admin.setup_default_permissions()

db.commit()
print("✅ Now a super admin!")
db.close()
```

---

## 📋 Complete Example

Here's a complete workflow:

```bash
# 1. Create first super admin
python create_admin.py --quick

# 2. Start server
uvicorn src.app_01.main:app --reload

# 3. Login
# Go to: http://localhost:8000/admin/login
# Username: admin
# Password: admin123

# 4. Change password (in Python shell)
python -c "
from passlib.hash import bcrypt
from src.app_01.db.market_db import db_manager, Market
from src.app_01.models.admins.admin import Admin

db = next(db_manager.get_db_session(Market.KG))
admin = db.query(Admin).filter(Admin.username == 'admin').first()
admin.hashed_password = bcrypt.hash('my_new_secure_password')
db.commit()
print('✅ Password changed!')
db.close()
"

# 5. Create content admin for your team
python create_admin.py
# Follow prompts to create content admin accounts
```

---

## 🚀 Production Deployment

### **Railway / Production**

**Option 1: SSH into server and run script**

```bash
# SSH to Railway
railway shell

# Run script
python create_admin.py --quick

# Change password immediately
```

**Option 2: Add to deployment script**

```python
# add_to_startup.py
import os
if os.getenv("CREATE_DEFAULT_ADMIN") == "true":
    from create_admin import quick_create_super_admin
    quick_create_super_admin()
```

**Option 3: Use Railway CLI**

```bash
railway run python create_admin.py --quick
```

---

## 📚 Script Reference

### **create_admin.py**

```bash
# Interactive mode (asks for details)
python create_admin.py

# Quick mode (default super admin)
python create_admin.py --quick

# Help
python create_admin.py --help
```

### **Functions Available**:

```python
from create_admin import create_admin

# Create custom admin
create_admin(
    username="john",
    password="secure123",
    email="john@company.com",
    full_name="John Smith",
    is_super_admin=True,
    admin_role="super_admin"
)
```

---

## ✅ Summary

**To create an admin user**:

1. **Quick Way** (for testing):

   ```bash
   python create_admin.py --quick
   # Username: admin, Password: admin123
   ```

2. **Secure Way** (for production):

   ```bash
   python create_admin.py
   # Follow prompts, use strong password
   ```

3. **Login**:
   ```
   http://localhost:8000/admin/login
   ```

**Security**:

- ✅ No public signup (secure by design)
- ✅ Password hashing with bcrypt
- ✅ Role-based access control
- ✅ Activity logging
- ✅ Session management

---

**Need help?** Check:

- `src/app_01/models/admins/admin.py` - Admin model
- `src/app_01/admin/sqladmin_views.py` - Authentication backend
- `tests/admin/test_admin_auth.py` - Admin auth tests

**Your admin panel is secure and ready to use!** 🔐✅
