# 📋 Admin Logging System

## Overview

Comprehensive logging system for tracking admin actions, errors, and debugging issues in the admin panel.

## Features

### ✅ What Gets Logged

1. **Admin Actions**

   - Login/Logout
   - Create/Update/Delete operations
   - View/Export operations
   - IP address and user agent

2. **Errors**

   - Full error traceback
   - Context of the error
   - Admin who encountered it
   - Timestamp and IP

3. **Request Details**
   - HTTP method and path
   - Response status
   - Request duration
   - User agent

## Components

### 1. Admin Logger Utility (`src/app_01/utils/admin_logger.py`)

Comprehensive logging utility with methods for:

- `log_action()` - Log any admin action
- `log_error()` - Log errors with full traceback
- `log_login()` - Log login attempts
- `log_logout()` - Log logouts
- `log_create()` - Log entity creation
- `log_update()` - Log entity updates
- `log_delete()` - Log entity deletion

### 2. Admin Log Database Model (`src/app_01/models/admins/admin_log.py`)

Stores logs in database with fields:

- `admin_id` - Who performed the action
- `action` - What was done (create, update, delete, etc.)
- `entity_type` - Type of entity (product, order, banner, etc.)
- `entity_id` - ID of the affected entity
- `description` - Human-readable description
- `ip_address` - IP address
- `user_agent` - Browser information
- `created_at` - Timestamp

### 3. Admin Log Admin View (`src/app_01/admin/admin_log_admin_views.py`)

View logs in the admin panel:

- Search by action, entity type, description, IP
- Filter by admin, action type, entity type, date
- Export logs to CSV
- **Read-only** (logs cannot be edited for integrity)
- Emoji-based action indicators (✅ login, ❌ failed, etc.)

### 4. Logging Middleware (`src/app_01/middleware/admin_logging_middleware.py`)

Automatically logs all admin requests:

- Request method, path, and duration
- Response status codes
- IP addresses and user agents
- Errors with full tracebacks

## Log Files

### 1. `admin_activity.log`

All admin actions and requests

```
2025-10-12 14:30:15 - admin_logger - INFO - Admin 1 - create banner #15 - Создан hero баннер
2025-10-12 14:31:22 - admin_logger - INFO - Admin Request: POST /admin/banner/create - Status: 200 - Duration: 0.45s
```

### 2. `admin_errors.log`

Detailed error information

```
===============================================================================
Admin Error Log
Time: 2025-10-12 14:35:10
Admin ID: 1
Context: Creating banner
Entity: banner #None
IP: 192.168.1.100
Error Type: TypeError
Error Message: 'NoneType' object is not subscriptable
Traceback:
... full traceback ...
===============================================================================
```

## Usage Examples

### Basic Logging in Endpoints

```python
from src.app_01.utils.admin_logger import AdminLogger

@router.post("/admin/banner/create")
def create_banner(banner_data: BannerCreate, db: Session = Depends(get_db)):
    try:
        # Create banner
        banner = Banner(**banner_data.dict())
        db.add(banner)
        db.commit()

        # Log success
        AdminLogger.log_create(
            db=db,
            admin_id=current_admin.id,  # Get from auth
            entity_type="banner",
            entity_id=banner.id,
            description=f"Создан баннер '{banner.title}'",
            ip_address=request.client.host
        )

        return banner

    except Exception as error:
        # Log error
        AdminLogger.log_error(
            db=db,
            admin_id=current_admin.id,
            error=error,
            context="Creating banner",
            entity_type="banner",
            ip_address=request.client.host
        )
        raise
```

### Logging Login/Logout

```python
# Login success
AdminLogger.log_login(
    db=db,
    admin_id=admin.id,
    success=True,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)

# Login failed
AdminLogger.log_login(
    db=db,
    admin_id=admin.id,
    success=False,
    ip_address=request.client.host
)

# Logout
AdminLogger.log_logout(
    db=db,
    admin_id=admin.id,
    ip_address=request.client.host
)
```

### Logging Updates with Changes

```python
# Track what changed
changes = {"title": "New Title", "is_active": True}

AdminLogger.log_update(
    db=db,
    admin_id=current_admin.id,
    entity_type="product",
    entity_id=product.id,
    changes=changes,
    ip_address=request.client.host
)
```

### Getting Admin Activity

```python
# Get recent logs for a specific admin
logs = AdminLogger.get_admin_activity(
    db=db,
    admin_id=1,
    limit=100
)

# Get all login attempts
logs = AdminLogger.get_admin_activity(
    db=db,
    action="login_success",
    limit=50
)

# Get all product operations
logs = AdminLogger.get_admin_activity(
    db=db,
    entity_type="product",
    limit=100
)
```

## Viewing Logs in Admin Panel

1. **Login to Admin Panel**: `https://marquebackend-production.up.railway.app/admin`

2. **Navigate to Logs**:

   - Sidebar → "Система" → "Логи активности"

3. **Filter Logs**:

   - By admin user
   - By action type (login, create, update, delete, error)
   - By entity type (product, order, banner, etc.)
   - By date range
   - By IP address

4. **Search Logs**:

   - Search in descriptions
   - Search by IP address
   - Search by action type

5. **Export Logs**:
   - Click "Export" button
   - Download as CSV for analysis

## Action Types

| Action          | Emoji | Description             |
| --------------- | ----- | ----------------------- |
| `login_success` | ✅    | Successful login        |
| `login_failed`  | ❌    | Failed login attempt    |
| `logout`        | 🚪    | User logged out         |
| `create`        | ➕    | Created new entity      |
| `update`        | ✏️    | Updated existing entity |
| `delete`        | 🗑️    | Deleted entity          |
| `view`          | 👁️    | Viewed entity details   |
| `export`        | 📤    | Exported data           |
| `import`        | 📥    | Imported data           |
| `error`         | ⚠️    | Error occurred          |

## Entity Types

| Type       | Russian      | Example             |
| ---------- | ------------ | ------------------- |
| `product`  | Товар        | Product operations  |
| `order`    | Заказ        | Order management    |
| `user`     | Пользователь | User operations     |
| `banner`   | Баннер       | Banner management   |
| `category` | Категория    | Category operations |
| `brand`    | Бренд        | Brand management    |
| `review`   | Отзыв        | Review moderation   |

## Debugging with Logs

### Finding Recent Errors

1. Go to Admin Panel → "Логи активности"
2. Filter by action = "error"
3. Sort by date (newest first)
4. View full error details

### Tracking User Actions

1. Filter by specific `admin_id`
2. See all actions performed by that admin
3. Track create/update/delete operations

### Monitoring System Activity

1. Export logs to CSV
2. Analyze in Excel/Google Sheets
3. Look for patterns:
   - Peak usage times
   - Most common errors
   - Frequently accessed entities

### Investigating Issues

1. **When:** Check timestamp of the error
2. **Who:** See which admin encountered it
3. **What:** View the action being performed
4. **Where:** Check the entity type and ID
5. **Why:** Read full error message and traceback
6. **How:** Review request details (IP, user agent)

## Log Retention

- **Database**: Logs stored indefinitely (can set up cleanup job)
- **Files**: Rotate weekly (can configure in logging settings)
- **Export**: CSV exports for archival

## Security Considerations

- Logs are **read-only** in admin panel
- Only admins can view logs
- Logs include IP addresses for security auditing
- Failed login attempts are logged for security monitoring
- Sensitive data (passwords) should NOT be logged

## Configuration

### Enable Middleware

Add to `main.py`:

```python
from src.app_01.middleware.admin_logging_middleware import AdminLoggingMiddleware

app.add_middleware(AdminLoggingMiddleware)
```

### Configure Log Files

Edit `src/app_01/utils/admin_logger.py`:

```python
# Change log file names
admin_log_handler = logging.FileHandler("path/to/admin_activity.log")
error_log_handler = logging.FileHandler("path/to/admin_errors.log")

# Change log levels
logger.setLevel(logging.DEBUG)  # More verbose
logger.setLevel(logging.WARNING)  # Less verbose
```

## Benefits

✅ **Debugging**: Quickly find and fix errors with full tracebacks  
✅ **Audit Trail**: Track all admin actions for compliance  
✅ **Security**: Monitor failed login attempts and suspicious activity  
✅ **Analytics**: Understand admin usage patterns  
✅ **Troubleshooting**: Reproduce issues by reviewing logs  
✅ **Accountability**: Know who did what and when

## Next Steps

1. **Deploy the logging system** to production
2. **Test it** by performing admin actions
3. **View logs** in the admin panel
4. **Set up alerts** for critical errors (optional)
5. **Regular review** of logs for security and performance

---

## Quick Reference

### Import Logger

```python
from src.app_01.utils.admin_logger import AdminLogger
```

### Log Action

```python
AdminLogger.log_action(db, admin_id, "action", "entity_type", entity_id, "description", ip, user_agent)
```

### Log Error

```python
AdminLogger.log_error(db, admin_id, error, "context", "entity_type", entity_id, ip)
```

### Get Logs

```python
logs = AdminLogger.get_admin_activity(db, admin_id, "action", "entity_type", limit)
```

---

**Status**: ✅ **READY TO USE**

The logging system is fully configured and ready to help you debug and monitor your admin panel!
