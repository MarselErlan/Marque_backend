# Migration Reset Guide

## Problem

You've done many migrations and your API is not saving data to the database properly. This is a common issue when:

- Migrations get out of sync with models
- Multiple migrations conflict with each other
- Database schema doesn't match your model definitions

## Solution: Reset Migrations from Scratch

### What This Will Do

1. ✅ Backup your current databases (to `databases/backups/`)
2. ✅ Delete all migration files
3. ✅ Delete all databases
4. ✅ Create ONE fresh initial migration from your current models
5. ✅ Apply the clean migration to both KG and US databases

### Prerequisites

Make sure you have:

- [ ] All your models properly defined in `src/app_01/models/`
- [ ] All models imported in `alembic/env.py`
- [ ] Your `.env` file configured with database URLs
- [ ] Virtual environment activated

### Step-by-Step Instructions

#### Step 1: Activate Virtual Environment

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
```

#### Step 2: Run the Reset Script

```bash
python reset_migrations.py
```

The script will:

- Ask for confirmation (type `yes` to proceed)
- Show progress for each step
- Create backups automatically
- Generate fresh migration
- Apply to both databases

#### Step 3: Verify Everything Works

Start your server:

```bash
uvicorn src.app_01.main:app --reload
```

Test an API endpoint that saves data:

```bash
# Example: Create a user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+996500123456",
    "password": "testpass123"
  }'
```

Check if data was saved:

```bash
# Use SQLite browser or command line
sqlite3 databases/marque_kg.db "SELECT * FROM users;"
```

#### Step 4: Populate Sample Data (Optional)

If you need sample data for testing:

```bash
python populate_databases.py
```

### Troubleshooting

#### Problem: "Module not found" errors during migration

**Solution:** Make sure all models are imported in `alembic/env.py`:

```python
# In alembic/env.py
from src.app_01.models.users import user, wishlist, market_user
from src.app_01.models.products import product, brand, category, sku, product_asset
from src.app_01.models.orders import order, order_item, cart, cart_order
from src.app_01.models.banners import banner
from src.app_01.models.admins import admin, admin_log
```

#### Problem: "Table already exists" errors

**Solution:** The databases weren't fully deleted. Manually delete:

```bash
rm databases/marque_kg.db
rm databases/marque_us.db
rm databases/marque_kg.db-wal
rm databases/marque_kg.db-shm
rm databases/marque_us.db-wal
rm databases/marque_us.db-shm
```

Then run the script again.

#### Problem: Data not saving after reset

**Possible causes:**

1. **No commit after add:** Make sure you're calling `db.commit()` after `db.add()`
2. **Transaction rollback:** Check for exceptions that might rollback transactions
3. **Wrong database session:** Ensure you're using the correct market database
4. **Model validation errors:** Check FastAPI logs for Pydantic validation errors

**Debug steps:**

```python
# In your API endpoint
try:
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(f"✓ Saved user with id: {new_user.id}")
except Exception as e:
    print(f"✗ Error saving: {e}")
    db.rollback()
    raise
```

### After Migration Reset

#### ✅ Do This:

- Test all your API endpoints
- Verify data is saving to database
- Check that queries are returning correct data
- Run your test suite: `pytest tests/`

#### ❌ Don't Do This:

- Don't make model changes and expect them to auto-apply (run `alembic revision --autogenerate` for new changes)
- Don't delete migration files manually (use proper Alembic commands)
- Don't edit migration files directly unless you know what you're doing

### Making Future Model Changes

When you need to change your models:

```bash
# 1. Edit your model files (e.g., src/app_01/models/users/user.py)

# 2. Create a migration for the change
alembic revision --autogenerate -m "add email field to user"

# 3. Apply to KG database
alembic upgrade head

# 4. Apply to US database
ALEMBIC_TARGET_DB=US alembic upgrade head
```

### Checking Migration Status

```bash
# Check current migration version
alembic current

# See migration history
alembic history

# See pending migrations
alembic heads
```

### If You Need to Restore Backup

Your backups are in `databases/backups/` with timestamps:

```bash
# List backups
ls -lh databases/backups/

# Restore a backup (example)
cp databases/backups/marque_kg.db.backup_20250106_143022 databases/marque_kg.db
```

### Common Database Operations

```bash
# View all tables in database
sqlite3 databases/marque_kg.db ".tables"

# View table schema
sqlite3 databases/marque_kg.db ".schema users"

# Query data
sqlite3 databases/marque_kg.db "SELECT * FROM users LIMIT 5;"

# Count records
sqlite3 databases/marque_kg.db "SELECT COUNT(*) FROM products;"
```

### Need Help?

If you're still having issues:

1. Check the FastAPI logs for errors
2. Look at `alembic/versions/` to see your migration file
3. Verify your model definitions match what you expect
4. Check that your database connection strings in `.env` are correct

---

## Quick Reference

| Task                   | Command                                            |
| ---------------------- | -------------------------------------------------- |
| Reset migrations       | `python reset_migrations.py`                       |
| Create new migration   | `alembic revision --autogenerate -m "description"` |
| Apply migration (KG)   | `alembic upgrade head`                             |
| Apply migration (US)   | `ALEMBIC_TARGET_DB=US alembic upgrade head`        |
| Rollback migration     | `alembic downgrade -1`                             |
| Check current version  | `alembic current`                                  |
| View migration history | `alembic history`                                  |

---

**Good luck! 🚀**
