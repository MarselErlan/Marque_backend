# 🎨 Frontend Integration Guide - Complete Authentication & Profile System

## 📋 Table of Contents

1. [API Overview](#api-overview)
2. [Authentication Flow](#authentication-flow)
3. [API Endpoints](#api-endpoints)
4. [Frontend Implementation](#frontend-implementation)
5. [Token Management](#token-management)
6. [Profile Management](#profile-management)
7. [Error Handling](#error-handling)
8. [Complete Examples](#complete-examples)

---

## 🌐 API Overview

**Base URL (Production)**: `https://marquebackend-production.up.railway.app/api/v1`

**Markets Supported**:

- 🇰🇬 **KG** (Kyrgyzstan): `+996` phone numbers
- 🇺🇸 **US** (United States): `+1` phone numbers

**Authentication**: JWT Bearer Token

---

## 🔐 Authentication Flow

### Complete User Journey

```
1. User enters phone number → 2. SMS verification code sent
   ↓
3. User enters code → 4. Backend verifies & creates/updates user
   ↓
5. Backend returns JWT token → 6. Frontend stores token
   ↓
7. User accesses protected routes → 8. Frontend sends token in headers
   ↓
9. User logs out → 10. Backend sets is_active = false
```

### User States

- **New User**: `is_new_user: true`, `is_verified: true`, `is_active: true`
- **Existing User (Login)**: `is_new_user: false`, `is_verified: true`, `is_active: true`
- **Logged Out User**: `is_active: false`

---

## 📡 API Endpoints

### 1. Authentication APIs

#### 📱 Send Verification Code

```http
POST /api/v1/auth/send-verification
Content-Type: application/json

{
  "phone_number": "+13128059851"
}
```

**Response**:

```json
{
  "success": true,
  "message": "Verification code sent successfully",
  "phone_number": "+1 (312) 805-9851",
  "market": "us",
  "language": "en",
  "expires_in_minutes": 15
}
```

#### ✅ Verify Code & Login

```http
POST /api/v1/auth/verify-code
Content-Type: application/json

{
  "phone_number": "+13128059851",
  "code": "123456"
}
```

**Response**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "19",
    "name": "Not set",
    "phone": "+13128059851",
    "is_active": true,
    "is_verified": true
  },
  "market": "us",
  "is_new_user": false
}
```

#### 👤 Get Profile (Logged In)

```http
GET /api/v1/auth/profile
Authorization: Bearer <your_token>
```

**Response**:

```json
{
  "id": "19",
  "phone_number": "+13128059851",
  "formatted_phone": "+1 (312) 805-9851",
  "name": "Not set",
  "full_name": null,
  "profile_image_url": null,
  "is_active": true,
  "is_verified": true,
  "market": "us",
  "language": "en",
  "country": "United States",
  "currency": "USD",
  "currency_code": "$",
  "last_login": "2025-10-23T23:13:24.738458Z",
  "created_at": "2025-10-23T20:00:00Z"
}
```

#### 🚪 Logout

```http
POST /api/v1/auth/logout
Authorization: Bearer <your_token>
```

**Response**:

```json
{
  "success": true,
  "message": "Logged out successfully. User is now inactive."
}
```

### 2. Profile Management APIs

#### 📝 Update Profile

```http
PUT /api/v1/auth/profile
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "language": "en"
}
```

#### 📍 Address Management

```http
# Get all addresses
GET /api/v1/profile/addresses
Authorization: Bearer <your_token>

# Create address
POST /api/v1/profile/addresses
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "address_type": "home",
  "street_address": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "is_default": true
}

# Update address
PUT /api/v1/profile/addresses/{address_id}
Authorization: Bearer <your_token>

# Delete address
DELETE /api/v1/profile/addresses/{address_id}
Authorization: Bearer <your_token>
```

#### 💳 Payment Methods

```http
# Get all payment methods
GET /api/v1/profile/payment-methods
Authorization: Bearer <your_token>

# Create payment method
POST /api/v1/profile/payment-methods
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "payment_type": "card",
  "card_last_four": "4242",
  "card_brand": "Visa",
  "cardholder_name": "John Doe",
  "expiry_date": "12/25",
  "is_default": true
}
```

#### 📦 Orders

```http
# Get all orders
GET /api/v1/profile/orders
Authorization: Bearer <your_token>

# Get order details
GET /api/v1/profile/orders/{order_id}
Authorization: Bearer <your_token>

# Cancel order
POST /api/v1/profile/orders/{order_id}/cancel
Authorization: Bearer <your_token>
```

#### 🔔 Notifications

```http
# Get all notifications
GET /api/v1/profile/notifications
Authorization: Bearer <your_token>

# Mark notification as read
PUT /api/v1/profile/notifications/{notification_id}/read
Authorization: Bearer <your_token>

# Mark all as read
PUT /api/v1/profile/notifications/read-all
Authorization: Bearer <your_token>
```

---

## 💻 Frontend Implementation

### React / React Native Example

#### 1. Setup API Client

```javascript
// api/config.js
const API_BASE_URL = "https://marquebackend-production.up.railway.app/api/v1";

export const API_ENDPOINTS = {
  SEND_CODE: `${API_BASE_URL}/auth/send-verification`,
  VERIFY_CODE: `${API_BASE_URL}/auth/verify-code`,
  PROFILE: `${API_BASE_URL}/auth/profile`,
  LOGOUT: `${API_BASE_URL}/auth/logout`,
  ADDRESSES: `${API_BASE_URL}/profile/addresses`,
  PAYMENT_METHODS: `${API_BASE_URL}/profile/payment-methods`,
  ORDERS: `${API_BASE_URL}/profile/orders`,
  NOTIFICATIONS: `${API_BASE_URL}/profile/notifications`,
};
```

#### 2. Create Auth Service

```javascript
// services/authService.js
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_ENDPOINTS } from "../api/config";

const TOKEN_KEY = "auth_token";
const USER_KEY = "user_data";

export const authService = {
  // Send verification code
  async sendVerificationCode(phoneNumber) {
    try {
      const response = await fetch(API_ENDPOINTS.SEND_CODE, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ phone_number: phoneNumber }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to send code");
      }

      return data;
    } catch (error) {
      console.error("Send code error:", error);
      throw error;
    }
  },

  // Verify code and login
  async verifyCode(phoneNumber, code) {
    try {
      const response = await fetch(API_ENDPOINTS.VERIFY_CODE, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          phone_number: phoneNumber,
          code: code,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Invalid code");
      }

      // Store token and user data
      await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(data.user));

      return data;
    } catch (error) {
      console.error("Verify code error:", error);
      throw error;
    }
  },

  // Get user profile
  async getProfile() {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);

      if (!token) {
        throw new Error("No token found");
      }

      const response = await fetch(API_ENDPOINTS.PROFILE, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to get profile");
      }

      // Update stored user data
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(data));

      return data;
    } catch (error) {
      console.error("Get profile error:", error);
      throw error;
    }
  },

  // Update profile
  async updateProfile(updates) {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);

      const response = await fetch(API_ENDPOINTS.PROFILE, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updates),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to update profile");
      }

      // Update stored user data
      await AsyncStorage.setItem(USER_KEY, JSON.stringify(data));

      return data;
    } catch (error) {
      console.error("Update profile error:", error);
      throw error;
    }
  },

  // Logout
  async logout() {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);

      if (token) {
        await fetch(API_ENDPOINTS.LOGOUT, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
      }

      // Clear local storage
      await AsyncStorage.removeItem(TOKEN_KEY);
      await AsyncStorage.removeItem(USER_KEY);

      return true;
    } catch (error) {
      console.error("Logout error:", error);
      // Still clear local storage even if API call fails
      await AsyncStorage.removeItem(TOKEN_KEY);
      await AsyncStorage.removeItem(USER_KEY);
      return true;
    }
  },

  // Check if user is logged in
  async isLoggedIn() {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      return !!token;
    } catch (error) {
      return false;
    }
  },

  // Get stored token
  async getToken() {
    return await AsyncStorage.getItem(TOKEN_KEY);
  },

  // Get stored user
  async getUser() {
    const userData = await AsyncStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  },
};
```

#### 3. Create API Client with Auth

```javascript
// api/client.js
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_ENDPOINTS } from "./config";

const TOKEN_KEY = "auth_token";

export const apiClient = {
  // Generic authenticated request
  async authenticatedRequest(url, options = {}) {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);

      if (!token) {
        throw new Error("Not authenticated");
      }

      const response = await fetch(url, {
        ...options,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          ...options.headers,
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Request failed");
      }

      return data;
    } catch (error) {
      console.error("API request error:", error);
      throw error;
    }
  },

  // GET request
  async get(endpoint) {
    return this.authenticatedRequest(endpoint, { method: "GET" });
  },

  // POST request
  async post(endpoint, body) {
    return this.authenticatedRequest(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  // PUT request
  async put(endpoint, body) {
    return this.authenticatedRequest(endpoint, {
      method: "PUT",
      body: JSON.stringify(body),
    });
  },

  // DELETE request
  async delete(endpoint) {
    return this.authenticatedRequest(endpoint, { method: "DELETE" });
  },
};
```

#### 4. Create Profile Service

```javascript
// services/profileService.js
import { apiClient } from "../api/client";
import { API_ENDPOINTS } from "../api/config";

export const profileService = {
  // Addresses
  async getAddresses() {
    return await apiClient.get(API_ENDPOINTS.ADDRESSES);
  },

  async createAddress(addressData) {
    return await apiClient.post(API_ENDPOINTS.ADDRESSES, addressData);
  },

  async updateAddress(addressId, addressData) {
    return await apiClient.put(
      `${API_ENDPOINTS.ADDRESSES}/${addressId}`,
      addressData
    );
  },

  async deleteAddress(addressId) {
    return await apiClient.delete(`${API_ENDPOINTS.ADDRESSES}/${addressId}`);
  },

  // Payment Methods
  async getPaymentMethods() {
    return await apiClient.get(API_ENDPOINTS.PAYMENT_METHODS);
  },

  async createPaymentMethod(paymentData) {
    return await apiClient.post(API_ENDPOINTS.PAYMENT_METHODS, paymentData);
  },

  async updatePaymentMethod(paymentId, paymentData) {
    return await apiClient.put(
      `${API_ENDPOINTS.PAYMENT_METHODS}/${paymentId}`,
      paymentData
    );
  },

  async deletePaymentMethod(paymentId) {
    return await apiClient.delete(
      `${API_ENDPOINTS.PAYMENT_METHODS}/${paymentId}`
    );
  },

  // Orders
  async getOrders() {
    return await apiClient.get(API_ENDPOINTS.ORDERS);
  },

  async getOrder(orderId) {
    return await apiClient.get(`${API_ENDPOINTS.ORDERS}/${orderId}`);
  },

  async cancelOrder(orderId) {
    return await apiClient.post(`${API_ENDPOINTS.ORDERS}/${orderId}/cancel`);
  },

  // Notifications
  async getNotifications() {
    return await apiClient.get(API_ENDPOINTS.NOTIFICATIONS);
  },

  async markNotificationRead(notificationId) {
    return await apiClient.put(
      `${API_ENDPOINTS.NOTIFICATIONS}/${notificationId}/read`
    );
  },

  async markAllNotificationsRead() {
    return await apiClient.put(`${API_ENDPOINTS.NOTIFICATIONS}/read-all`);
  },
};
```

---

## 🔑 Token Management

### Best Practices

```javascript
// utils/tokenManager.js
import AsyncStorage from "@react-native-async-storage/async-storage";
import { authService } from "../services/authService";

const TOKEN_KEY = "auth_token";
const TOKEN_EXPIRY_KEY = "token_expiry";

export const tokenManager = {
  // Store token with expiry
  async setToken(token, expiresInMinutes = 30) {
    const expiryTime = Date.now() + expiresInMinutes * 60 * 1000;
    await AsyncStorage.setItem(TOKEN_KEY, token);
    await AsyncStorage.setItem(TOKEN_EXPIRY_KEY, expiryTime.toString());
  },

  // Get token if not expired
  async getValidToken() {
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    const expiry = await AsyncStorage.getItem(TOKEN_EXPIRY_KEY);

    if (!token || !expiry) {
      return null;
    }

    // Check if token is expired
    if (Date.now() > parseInt(expiry)) {
      await this.clearToken();
      return null;
    }

    return token;
  },

  // Clear token
  async clearToken() {
    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(TOKEN_EXPIRY_KEY);
  },

  // Check if token is valid
  async isTokenValid() {
    const token = await this.getValidToken();
    return !!token;
  },
};
```

---

## 📱 Complete Screen Examples

### 1. Login Screen

```javascript
// screens/LoginScreen.js
import React, { useState } from "react";
import { View, TextInput, Button, Text, Alert } from "react-native";
import { authService } from "../services/authService";

export const LoginScreen = ({ navigation }) => {
  const [phoneNumber, setPhoneNumber] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState("phone"); // 'phone' or 'code'
  const [loading, setLoading] = useState(false);

  const handleSendCode = async () => {
    if (!phoneNumber) {
      Alert.alert("Error", "Please enter phone number");
      return;
    }

    setLoading(true);
    try {
      const result = await authService.sendVerificationCode(phoneNumber);
      Alert.alert("Success", result.message);
      setStep("code");
    } catch (error) {
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!code) {
      Alert.alert("Error", "Please enter verification code");
      return;
    }

    setLoading(true);
    try {
      const result = await authService.verifyCode(phoneNumber, code);

      if (result.is_new_user) {
        Alert.alert("Welcome!", "Account created successfully");
      } else {
        Alert.alert("Welcome back!", "Login successful");
      }

      // Navigate to home screen
      navigation.replace("Home");
    } catch (error) {
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ padding: 20 }}>
      {step === "phone" ? (
        <>
          <Text style={{ fontSize: 24, marginBottom: 20 }}>Login</Text>
          <TextInput
            placeholder="Phone Number (e.g., +13128059851)"
            value={phoneNumber}
            onChangeText={setPhoneNumber}
            keyboardType="phone-pad"
            style={{ borderWidth: 1, padding: 10, marginBottom: 20 }}
          />
          <Button
            title={loading ? "Sending..." : "Send Code"}
            onPress={handleSendCode}
            disabled={loading}
          />
        </>
      ) : (
        <>
          <Text style={{ fontSize: 24, marginBottom: 20 }}>
            Enter Verification Code
          </Text>
          <Text style={{ marginBottom: 20 }}>Code sent to {phoneNumber}</Text>
          <TextInput
            placeholder="6-digit code"
            value={code}
            onChangeText={setCode}
            keyboardType="number-pad"
            maxLength={6}
            style={{ borderWidth: 1, padding: 10, marginBottom: 20 }}
          />
          <Button
            title={loading ? "Verifying..." : "Verify"}
            onPress={handleVerifyCode}
            disabled={loading}
          />
          <Button
            title="Back"
            onPress={() => setStep("phone")}
            disabled={loading}
          />
        </>
      )}
    </View>
  );
};
```

### 2. Profile Screen

```javascript
// screens/ProfileScreen.js
import React, { useState, useEffect } from "react";
import { View, Text, Button, TextInput, Alert } from "react-native";
import { authService } from "../services/authService";

export const ProfileScreen = ({ navigation }) => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [fullName, setFullName] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await authService.getProfile();
      setProfile(data);
      setFullName(data.full_name || "");
    } catch (error) {
      Alert.alert("Error", "Failed to load profile");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateProfile = async () => {
    setLoading(true);
    try {
      const updated = await authService.updateProfile({
        full_name: fullName,
      });
      setProfile(updated);
      setEditing(false);
      Alert.alert("Success", "Profile updated");
    } catch (error) {
      Alert.alert("Error", "Failed to update profile");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert("Logout", "Are you sure you want to logout?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        onPress: async () => {
          await authService.logout();
          navigation.replace("Login");
        },
      },
    ]);
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={{ padding: 20 }}>
      <Text style={{ fontSize: 24, marginBottom: 20 }}>Profile</Text>

      {editing ? (
        <>
          <TextInput
            placeholder="Full Name"
            value={fullName}
            onChangeText={setFullName}
            style={{ borderWidth: 1, padding: 10, marginBottom: 20 }}
          />
          <Button title="Save" onPress={handleUpdateProfile} />
          <Button title="Cancel" onPress={() => setEditing(false)} />
        </>
      ) : (
        <>
          <Text>Phone: {profile?.formatted_phone}</Text>
          <Text>Name: {profile?.full_name || "Not set"}</Text>
          <Text>Market: {profile?.market}</Text>
          <Text>Country: {profile?.country}</Text>
          <Text>Currency: {profile?.currency_code}</Text>
          <Text>Status: {profile?.is_active ? "Active" : "Inactive"}</Text>
          <Text>Verified: {profile?.is_verified ? "Yes" : "No"}</Text>

          <Button
            title="Edit Profile"
            onPress={() => setEditing(true)}
            style={{ marginTop: 20 }}
          />
          <Button title="Logout" onPress={handleLogout} color="red" />
        </>
      )}
    </View>
  );
};
```

### 3. Addresses Screen

```javascript
// screens/AddressesScreen.js
import React, { useState, useEffect } from "react";
import { View, Text, FlatList, Button, Alert } from "react-native";
import { profileService } from "../services/profileService";

export const AddressesScreen = ({ navigation }) => {
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAddresses();
  }, []);

  const loadAddresses = async () => {
    try {
      const data = await profileService.getAddresses();
      setAddresses(data);
    } catch (error) {
      Alert.alert("Error", "Failed to load addresses");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (addressId) => {
    Alert.alert("Delete Address", "Are you sure?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        onPress: async () => {
          try {
            await profileService.deleteAddress(addressId);
            loadAddresses();
            Alert.alert("Success", "Address deleted");
          } catch (error) {
            Alert.alert("Error", "Failed to delete address");
          }
        },
      },
    ]);
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text>Loading addresses...</Text>
      </View>
    );
  }

  return (
    <View style={{ flex: 1, padding: 20 }}>
      <Text style={{ fontSize: 24, marginBottom: 20 }}>My Addresses</Text>

      <Button
        title="+ Add New Address"
        onPress={() => navigation.navigate("AddAddress")}
      />

      {addresses.length === 0 ? (
        <Text style={{ marginTop: 20, textAlign: "center" }}>
          No addresses yet
        </Text>
      ) : (
        <FlatList
          data={addresses}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <View style={{ padding: 15, borderWidth: 1, marginTop: 10 }}>
              <Text style={{ fontWeight: "bold" }}>{item.address_type}</Text>
              <Text>{item.street_address}</Text>
              <Text>
                {item.city}, {item.state} {item.postal_code}
              </Text>
              <Text>{item.country}</Text>
              {item.is_default && (
                <Text style={{ color: "green" }}>✓ Default</Text>
              )}
              <View style={{ flexDirection: "row", marginTop: 10 }}>
                <Button
                  title="Edit"
                  onPress={() =>
                    navigation.navigate("EditAddress", { address: item })
                  }
                />
                <Button
                  title="Delete"
                  onPress={() => handleDelete(item.id)}
                  color="red"
                />
              </View>
            </View>
          )}
        />
      )}
    </View>
  );
};
```

---

## ⚠️ Error Handling

### Common Error Codes

```javascript
// utils/errorHandler.js
export const ERROR_CODES = {
  // Auth errors
  INVALID_CODE: "Invalid verification code",
  CODE_EXPIRED: "Verification code expired",
  INVALID_PHONE: "Invalid phone number format",
  UNAUTHORIZED: "Please login to continue",
  TOKEN_EXPIRED: "Session expired, please login again",

  // Network errors
  NETWORK_ERROR: "Network error, please check your connection",
  SERVER_ERROR: "Server error, please try again later",
};

export const handleApiError = (error) => {
  if (error.message.includes("401")) {
    return ERROR_CODES.UNAUTHORIZED;
  }
  if (error.message.includes("403")) {
    return ERROR_CODES.TOKEN_EXPIRED;
  }
  if (error.message.includes("400")) {
    return ERROR_CODES.INVALID_CODE;
  }
  if (error.message.includes("Network request failed")) {
    return ERROR_CODES.NETWORK_ERROR;
  }
  if (error.message.includes("500")) {
    return ERROR_CODES.SERVER_ERROR;
  }

  return error.message || "An error occurred";
};
```

---

## 🔄 Navigation Setup (React Navigation)

```javascript
// navigation/AppNavigator.js
import React, { useState, useEffect } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import { authService } from "../services/authService";

import { LoginScreen } from "../screens/LoginScreen";
import { ProfileScreen } from "../screens/ProfileScreen";
import { AddressesScreen } from "../screens/AddressesScreen";

const Stack = createStackNavigator();

export const AppNavigator = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkLoginStatus();
  }, []);

  const checkLoginStatus = async () => {
    const loggedIn = await authService.isLoggedIn();
    setIsLoggedIn(loggedIn);
    setLoading(false);
  };

  if (loading) {
    return null; // Or show splash screen
  }

  return (
    <NavigationContainer>
      <Stack.Navigator>
        {!isLoggedIn ? (
          <Stack.Screen
            name="Login"
            component={LoginScreen}
            options={{ headerShown: false }}
          />
        ) : (
          <>
            <Stack.Screen name="Profile" component={ProfileScreen} />
            <Stack.Screen name="Addresses" component={AddressesScreen} />
            {/* Add more screens */}
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};
```

---

## ✅ Testing Checklist

- [ ] User can send verification code
- [ ] User can verify code and login
- [ ] Token is stored correctly
- [ ] Profile screen shows user data
- [ ] User can update profile
- [ ] User can create/edit/delete addresses
- [ ] User can view orders
- [ ] User can logout
- [ ] App handles expired tokens
- [ ] App handles network errors
- [ ] Re-login doesn't create duplicate users

---

## 🚀 Quick Start

1. **Install dependencies**:

   ```bash
   npm install @react-native-async-storage/async-storage
   npm install @react-navigation/native @react-navigation/stack
   ```

2. **Copy the service files** from this guide

3. **Update API_BASE_URL** in `api/config.js`

4. **Implement screens** using the examples above

5. **Test with real phone numbers**

---

## 📞 Support

If you encounter any issues:

1. Check network connectivity
2. Verify API base URL is correct
3. Check token is being sent in headers
4. Review error messages in console
5. Test endpoints with Postman first

---

## 🎉 Done!

Your frontend is now fully integrated with the Marque backend!

**All features work**:

- ✅ Phone authentication with SMS
- ✅ User profile management
- ✅ Addresses, payments, orders, notifications
- ✅ Proper logout/login with user state management
- ✅ No duplicate users
- ✅ Two-market support (KG + US)
