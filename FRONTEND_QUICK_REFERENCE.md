# 🚀 Frontend Quick Reference - API Cheat Sheet

## 🌐 Base URL

```
https://marquebackend-production.up.railway.app/api/v1
```

---

## 🔐 Authentication APIs

### 1. Send Code

```javascript
POST /auth/send-verification
{
  "phone_number": "+13128059851"
}

// Response
{
  "success": true,
  "phone_number": "+1 (312) 805-9851",
  "market": "us",
  "expires_in_minutes": 15
}
```

### 2. Verify Code (Login)

```javascript
POST /auth/verify-code
{
  "phone_number": "+13128059851",
  "code": "123456"
}

// Response
{
  "access_token": "eyJhbGci...",
  "user": {
    "id": "19",
    "phone": "+13128059851",
    "is_active": true,
    "is_verified": true
  },
  "is_new_user": false
}
```

### 3. Get Profile

```javascript
GET /auth/profile
Headers: { Authorization: "Bearer <token>" }

// Response
{
  "id": "19",
  "phone_number": "+13128059851",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "market": "us"
}
```

### 4. Update Profile

```javascript
PUT /auth/profile
Headers: { Authorization: "Bearer <token>" }
{
  "full_name": "John Doe",
  "language": "en"
}
```

### 5. Logout

```javascript
POST /auth/logout
Headers: { Authorization: "Bearer <token>" }

// Response
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## 📍 Address APIs

```javascript
// Get all addresses
GET /profile/addresses
Headers: { Authorization: "Bearer <token>" }

// Create address
POST /profile/addresses
Headers: { Authorization: "Bearer <token>" }
{
  "address_type": "home",
  "street_address": "123 Main St",
  "city": "New York",
  "postal_code": "10001",
  "is_default": true
}

// Update address
PUT /profile/addresses/{id}
Headers: { Authorization: "Bearer <token>" }
{ /* updated fields */ }

// Delete address
DELETE /profile/addresses/{id}
Headers: { Authorization: "Bearer <token>" }
```

---

## 💳 Payment Methods APIs

```javascript
// Get all payment methods
GET /profile/payment-methods
Headers: { Authorization: "Bearer <token>" }

// Create payment method
POST /profile/payment-methods
Headers: { Authorization: "Bearer <token>" }
{
  "payment_type": "card",
  "card_last_four": "4242",
  "card_brand": "Visa",
  "is_default": true
}

// Update
PUT /profile/payment-methods/{id}

// Delete
DELETE /profile/payment-methods/{id}
```

---

## 📦 Order APIs

```javascript
// Get all orders
GET / profile / orders;
Headers: {
  Authorization: "Bearer <token>";
}

// Get single order
GET / profile / orders / { id };
Headers: {
  Authorization: "Bearer <token>";
}

// Cancel order
POST / profile / orders / { id } / cancel;
Headers: {
  Authorization: "Bearer <token>";
}
```

---

## 🔔 Notification APIs

```javascript
// Get all notifications
GET / profile / notifications;
Headers: {
  Authorization: "Bearer <token>";
}

// Mark as read
PUT / profile / notifications / { id } / read;
Headers: {
  Authorization: "Bearer <token>";
}

// Mark all as read
PUT / profile / notifications / read - all;
Headers: {
  Authorization: "Bearer <token>";
}
```

---

## 💻 Code Examples

### Fetch with Token

```javascript
const token = await AsyncStorage.getItem("auth_token");

const response = await fetch(
  "https://marquebackend-production.up.railway.app/api/v1/auth/profile",
  {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
  }
);

const data = await response.json();
```

### Axios with Token

```javascript
import axios from "axios";

const token = await AsyncStorage.getItem("auth_token");

const response = await axios.get(
  "https://marquebackend-production.up.railway.app/api/v1/auth/profile",
  {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
);

const data = response.data;
```

---

## ⚡ Quick Login Flow

```javascript
// 1. Send code
await fetch("/auth/send-verification", {
  method: "POST",
  body: JSON.stringify({ phone_number: "+13128059851" }),
});

// 2. Verify code
const loginResponse = await fetch("/auth/verify-code", {
  method: "POST",
  body: JSON.stringify({
    phone_number: "+13128059851",
    code: "123456",
  }),
});

const { access_token } = await loginResponse.json();

// 3. Store token
await AsyncStorage.setItem("auth_token", access_token);

// 4. Use token for all requests
const profile = await fetch("/auth/profile", {
  headers: { Authorization: `Bearer ${access_token}` },
});
```

---

## 🔑 Token Storage

```javascript
// Store
await AsyncStorage.setItem("auth_token", token);

// Get
const token = await AsyncStorage.getItem("auth_token");

// Remove (logout)
await AsyncStorage.removeItem("auth_token");
```

---

## ⚠️ Error Handling

```javascript
try {
  const response = await fetch(endpoint, options);
  const data = await response.json();

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired - redirect to login
      await AsyncStorage.removeItem("auth_token");
      navigation.replace("Login");
    } else if (response.status === 400) {
      // Bad request - show error
      Alert.alert("Error", data.detail);
    }
    throw new Error(data.detail || "Request failed");
  }

  return data;
} catch (error) {
  console.error(error);
  Alert.alert("Error", error.message);
}
```

---

## 📱 Phone Number Formats

| Market | Code | Example       | Database   |
| ------ | ---- | ------------- | ---------- |
| 🇰🇬 KG  | +996 | +996700123456 | Railway KG |
| 🇺🇸 US  | +1   | +13128059851  | Railway US |

---

## ✅ Response Codes

| Code | Meaning      | Action                  |
| ---- | ------------ | ----------------------- |
| 200  | Success      | Continue                |
| 400  | Bad Request  | Show error message      |
| 401  | Unauthorized | Redirect to login       |
| 403  | Forbidden    | Token expired, re-login |
| 404  | Not Found    | Resource doesn't exist  |
| 500  | Server Error | Try again later         |

---

## 🎯 Full Integration Checklist

- [ ] Install AsyncStorage
- [ ] Create API config with base URL
- [ ] Create auth service
- [ ] Implement login screen
- [ ] Store token after login
- [ ] Add token to all API requests
- [ ] Create profile screen
- [ ] Implement logout
- [ ] Handle token expiration
- [ ] Test with real phone number

---

## 📖 Need More Details?

See **FRONTEND_INTEGRATION_GUIDE.md** for:

- Complete code examples
- Full screen implementations
- Error handling utilities
- Navigation setup
- TypeScript types

---

## 🚀 Production URLs

- **API**: `https://marquebackend-production.up.railway.app/api/v1`
- **Admin Panel**: `https://marquebackend-production.up.railway.app/admin`
- **Health Check**: `https://marquebackend-production.up.railway.app/health`

---

**Happy Coding! 🎉**
