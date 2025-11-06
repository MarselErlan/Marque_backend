# 🚀 Quick Start: Reset Migrations

## Problem You're Having

- Did many migrations
- API not saving data to database
- Need to start fresh

## Solution (3 Simple Steps)

### 1️⃣ Run the Reset Script

```bash
cd /Users/macbookpro/M4_Projects/Prodaction/Marque
source venv/bin/activate
python reset_migrations.py
```

When prompted, type `yes` to proceed.

### 2️⃣ Test Your API

```bash
# Start the server
uvicorn src.app_01.main:app --reload
```

In another terminal, test that data saves:

```bash
# Example: Register a user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "+996500123456", "password": "test123"}'

# Verify it was saved
sqlite3 databases/marque_kg.db "SELECT * FROM users;"
```

### 3️⃣ Done! 🎉

Your databases are now clean and your APIs should save data properly.

---

## What the Script Does

✅ **Backs up** your current databases to `databases/backups/`  
✅ **Deletes** all old migration files  
✅ **Deletes** the databases  
✅ **Creates** ONE fresh migration from your models  
✅ **Applies** it to both KG and US databases

## Need More Help?

See `MIGRATION_RESET_GUIDE.md` for:

- Troubleshooting
- Future model changes
- Database operations
- Restore from backup

---

## Common Issues After Reset

### Issue: Data still not saving

**Check these:**

1. **Are you calling commit?**

```python
db.add(new_item)
db.commit()  # ← Don't forget this!
db.refresh(new_item)
```

2. **Is there an exception?**

```python
try:
    db.add(new_item)
    db.commit()
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
    raise
```

3. **Using the right database?**

```python
# For KG users
market = detect_market_from_phone("+996500123456")  # → Market.KG
db = next(get_db(market))

# For US users
market = detect_market_from_phone("+15551234567")  # → Market.US
db = next(get_db(market))
```

### Issue: "Table already exists" error

**Fix:**

```bash
rm databases/marque_kg.db databases/marque_us.db
python reset_migrations.py
```

### Issue: Import errors during migration

The script already fixed this! All models are now imported in `alembic/env.py`.

---

## After Reset Is Complete

### ✅ Do This:

- Test all your API endpoints
- Populate sample data if needed: `python populate_databases.py`
- Run tests: `pytest tests/`

### ❌ Don't Do This:

- Don't manually delete migration files
- Don't edit migration files directly
- Don't forget to commit after db.add()

---

**Questions?** Check `MIGRATION_RESET_GUIDE.md` for detailed help! 📚
