# 🚀 Frontend Integration - Start Here!

> Complete guides to connect your React Native/React app with the Marque backend

---

## 📚 Choose Your Guide

### 1. 🎯 **Quick Start** (Recommended)

**File**: [`COPY_PASTE_FRONTEND_CODE.md`](./COPY_PASTE_FRONTEND_CODE.md)

**Best for**: Developers who want to start quickly

**What's inside**:

- ✅ Complete, working code ready to copy-paste
- ✅ 7 files you can drop into your project
- ✅ No explanations, just code
- ✅ Login, Profile, Addresses screens
- ⏱️ **Time**: 10 minutes

---

### 2. 📖 **Complete Guide**

**File**: [`FRONTEND_INTEGRATION_GUIDE.md`](./FRONTEND_INTEGRATION_GUIDE.md)

**Best for**: Developers who want to understand everything

**What's inside**:

- 📡 All API endpoints explained
- 🔐 Authentication flow diagram
- 💻 Complete implementation examples
- 🔑 Token management best practices
- ⚠️ Error handling utilities
- 📱 Full screen implementations
- 🔄 Navigation setup
- ⏱️ **Time**: 30-60 minutes

---

### 3. ⚡ **Quick Reference**

**File**: [`FRONTEND_QUICK_REFERENCE.md`](./FRONTEND_QUICK_REFERENCE.md)

**Best for**: Quick lookups while coding

**What's inside**:

- 📋 API endpoints cheat sheet
- 💡 Code snippets
- 🔑 Common patterns
- ⚠️ Error codes
- 📱 Phone number formats
- ⏱️ **Time**: 5 minutes to scan

---

### 4. 🔐 **Session Management** (NEW!)

**File**: [`SESSION_MANAGEMENT_EXPLAINED.md`](./SESSION_MANAGEMENT_EXPLAINED.md)

**Best for**: Understanding how cart/wishlist/orders persist

**What's inside**:

- 🔑 How JWT tokens work
- 💾 How data persists in database
- 🔄 Cart/wishlist across login sessions
- 🛡️ Security best practices
- 🧪 Testing scenarios
- ⏱️ **Time**: 20 minutes

---

### 5. 🎯 **Quick Session Reference**

**File**: [`SESSION_QUICK_REFERENCE.md`](./SESSION_QUICK_REFERENCE.md)

**Best for**: Quick answers about session management

**What's inside**:

- ✅ What's stored where
- 🔄 Complete user journey
- 📋 Implementation checklist
- 🧪 Test commands
- ⏱️ **Time**: 5 minutes

---

### 6. 🛒 **Cart/Wishlist Example**

**File**: [`FRONTEND_CART_EXAMPLE.md`](./FRONTEND_CART_EXAMPLE.md)

**Best for**: Copy-paste cart and wishlist implementation

**What's inside**:

- 🛒 Complete CartScreen code
- ❤️ Complete WishlistScreen code
- 🔧 API service functions
- ✅ Data persistence examples
- ⏱️ **Time**: 15 minutes

---

### 7. 🏗️ **Architecture Diagram**

**File**: [`ARCHITECTURE_DIAGRAM.md`](./ARCHITECTURE_DIAGRAM.md)

**Best for**: Visual learners who want to see the big picture

**What's inside**:

- 📊 Complete system architecture
- 🔄 User flow diagrams
- 🗝️ JWT token lifecycle
- 🔗 Database relationships
- ⏱️ **Time**: 10 minutes

---

## 🎯 Recommended Path

### For Beginners:

1. Read **SESSION_MANAGEMENT_EXPLAINED.md** (understand how it works) ⭐
2. Read **FRONTEND_INTEGRATION_GUIDE.md** (understand concepts)
3. Use **COPY_PASTE_FRONTEND_CODE.md** (implement)
4. Copy from **FRONTEND_CART_EXAMPLE.md** (implement cart/wishlist)
5. Keep **FRONTEND_QUICK_REFERENCE.md** open (reference)

### For Experienced Developers:

1. Scan **SESSION_QUICK_REFERENCE.md** (understand session management) ⭐
2. Scan **FRONTEND_QUICK_REFERENCE.md** (understand APIs)
3. Copy from **COPY_PASTE_FRONTEND_CODE.md** (implement quickly)
4. Copy from **FRONTEND_CART_EXAMPLE.md** (implement cart/wishlist)
5. Check **ARCHITECTURE_DIAGRAM.md** if needed (visual reference)

### If You Have Questions About Data Persistence:

1. **"Will cart/wishlist be lost after logout?"**
   → Read **SESSION_MANAGEMENT_EXPLAINED.md** ✅
2. **"Do I need session tokens?"**
   → No! Read **SESSION_QUICK_REFERENCE.md** ✅
3. **"How does order processing work?"**
   → See **ARCHITECTURE_DIAGRAM.md** ✅

---

## 📋 What You'll Build

### ✅ Complete Features:

- 📱 **Phone Authentication** (SMS verification with Twilio)
- 👤 **User Profile** (view/edit profile)
- 📍 **Address Management** (CRUD operations)
- 💳 **Payment Methods** (view/add/delete)
- 📦 **Order Management** (view/cancel orders)
- 🔔 **Notifications** (view/mark as read)
- 🚪 **Logout** (proper user state management)

### 🔐 Security:

- JWT token authentication
- Secure token storage
- Automatic token expiration handling
- Proper logout (sets is_active = false in database)

### 🌍 Multi-Market Support:

- 🇰🇬 **Kyrgyzstan** (+996 numbers)
- 🇺🇸 **United States** (+1 numbers)
- Automatic market detection

---

## 🚀 Production URL

```
https://marquebackend-production.up.railway.app/api/v1
```

---

## 📦 Required Packages

### React Native:

```bash
npm install @react-native-async-storage/async-storage
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
```

### React (Web):

```bash
npm install axios
# or use fetch (built-in)
```

---

## 🧪 Testing

### Test Account:

- **Phone**: `+13128059851` (US) or `+996700123456` (KG)
- **Code**: You'll receive SMS via Twilio

### Quick Test:

```bash
# Backend health check
curl https://marquebackend-production.up.railway.app/health

# Expected: {"status":"healthy"}
```

---

## 🎨 Complete API Overview

### Authentication (4 endpoints)

- `POST /auth/send-verification` - Send SMS code
- `POST /auth/verify-code` - Login/signup
- `GET /auth/profile` - Get user profile
- `PUT /auth/profile` - Update profile
- `POST /auth/logout` - Logout

### Addresses (4 endpoints)

- `GET /profile/addresses` - List addresses
- `POST /profile/addresses` - Create address
- `PUT /profile/addresses/{id}` - Update address
- `DELETE /profile/addresses/{id}` - Delete address

### Payment Methods (4 endpoints)

- `GET /profile/payment-methods` - List payments
- `POST /profile/payment-methods` - Add payment
- `PUT /profile/payment-methods/{id}` - Update payment
- `DELETE /profile/payment-methods/{id}` - Delete payment

### Orders (3 endpoints)

- `GET /profile/orders` - List orders
- `GET /profile/orders/{id}` - Get order details
- `POST /profile/orders/{id}/cancel` - Cancel order

### Notifications (3 endpoints)

- `GET /profile/notifications` - List notifications
- `PUT /profile/notifications/{id}/read` - Mark as read
- `PUT /profile/notifications/read-all` - Mark all read

**Total**: 18 endpoints ✅

---

## 📱 User Flow

```
1. User opens app
   ↓
2. User enters phone number → Backend sends SMS code
   ↓
3. User enters code → Backend verifies via Twilio
   ↓
4. Backend creates/updates user → Returns JWT token
   ↓
5. App stores token → Navigates to home
   ↓
6. All API calls include token in Authorization header
   ↓
7. User logs out → Backend sets is_active = false
```

---

## 🎯 Quick Start (5 steps)

1. **Copy API config**:

   ```javascript
   // Copy from COPY_PASTE_FRONTEND_CODE.md
   const API_BASE_URL =
     "https://marquebackend-production.up.railway.app/api/v1";
   ```

2. **Copy authService.js**:

   - Handles login/logout
   - Manages token storage

3. **Copy profileService.js**:

   - Handles addresses, orders, etc.

4. **Copy LoginScreen.js**:

   - Phone input → Code verification

5. **Test it**:
   ```bash
   npm start
   # Enter your phone number
   # Enter code from SMS
   # ✅ You're logged in!
   ```

---

## ⚠️ Common Issues

### Issue 1: "Network request failed"

**Solution**: Check if backend is running:

```bash
curl https://marquebackend-production.up.railway.app/health
```

### Issue 2: "Token expired"

**Solution**: Tokens expire after 30 minutes. Login again.

### Issue 3: "Invalid phone number"

**Solution**: Use format `+13128059851` (with country code)

### Issue 4: SMS not received

**Solution**: Check phone number format, Twilio account status

---

## 📞 Need Help?

1. Check **FRONTEND_INTEGRATION_GUIDE.md** for detailed explanations
2. Look at **FRONTEND_QUICK_REFERENCE.md** for API specs
3. Copy working code from **COPY_PASTE_FRONTEND_CODE.md**
4. Test with Postman/curl first to verify backend

---

## ✅ Checklist

Before you start:

- [ ] Backend is deployed and healthy
- [ ] You have `@react-native-async-storage/async-storage` installed
- [ ] You have React Navigation installed (for navigation)
- [ ] You have a test phone number ready

After implementation:

- [ ] User can login with SMS code
- [ ] Token is stored in AsyncStorage
- [ ] Profile screen shows user data
- [ ] User can logout
- [ ] All protected routes require token
- [ ] Token expiration is handled

---

## 🎉 You're Ready!

Pick your guide above and start building! 🚀

**Recommended**: Start with **COPY_PASTE_FRONTEND_CODE.md** for fastest results!
