# Marque API - Single Authentication System

## 🚀 **Clean Production API**

Your Marque project now has **ONE SINGLE** production-ready phone authentication system.

---

## 📁 **Current Clean Structure**

### ✅ **KEEP - Production API**

- `marque_api_production.py` - **Main production API** (port 8004)

### 🗑️ **REMOVED - Duplicate Systems**

- ~~`us_phone_auth.py`~~ - Demo version (deleted)
- ~~`us_phone_auth_sms.py`~~ - SMS version (deleted)
- ~~`us_phone_auth_verify.py`~~ - Twilio Verify version (deleted)
- ~~`demo_us_phone_auth.py`~~ - Demo script (deleted)
- ~~`test_phone_auth_complete.py`~~ - Test script (deleted)
- ~~All Twilio test scripts~~ - Cleanup complete

---

## 🎯 **Single API Endpoints**

### **Base URL**

```
http://127.0.0.1:8004
```

### **Authentication Flow**

1. **Send SMS**: `POST /api/v1/auth/send-verification`
2. **Verify Code**: `POST /api/v1/auth/verify-code`
3. **Get Profile**: `GET /api/v1/users/profile`

---

## 📱 **Postman Testing**

### **1. Health Check**

```
GET http://127.0.0.1:8004/health
```

### **2. Send Verification Code**

```
POST http://127.0.0.1:8004/api/v1/auth/send-verification
Content-Type: application/json

{
    "phone": "+13473926894"
}
```

### **3. Verify SMS Code**

```
POST http://127.0.0.1:8004/api/v1/auth/verify-code
Content-Type: application/json

{
    "phone": "+13473926894",
    "code": "123456"
}
```

### **4. Get User Profile**

```
GET http://127.0.0.1:8004/api/v1/users/profile
Authorization: Bearer <access_token>
```

---

## 🔧 **Running the API**

```bash
# Start the production API
source venv/bin/activate
python marque_api_production.py
```

**Server will start on**: `http://127.0.0.1:8004`

---

## 📚 **Documentation**

- **Swagger UI**: `http://127.0.0.1:8004/docs`
- **ReDoc**: `http://127.0.0.1:8004/redoc`
- **API Documentation**: `API_DOCUMENTATION.md`

---

## 🎉 **Clean & Ready!**

✅ **Single authentication system**  
✅ **Production-ready API**  
✅ **No duplicate logic**  
✅ **Clean codebase**  
✅ **Ready for Postman testing**

Your Marque API is now **clean, focused, and ready for production!** 🚀
