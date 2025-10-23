# 📋 Copy-Paste Frontend Code - Ready to Use!

> Complete, working code you can copy directly into your React Native project

---

## 📁 File Structure

```
your-app/
├── src/
│   ├── api/
│   │   └── config.js          ← API configuration
│   ├── services/
│   │   ├── authService.js     ← Authentication logic
│   │   └── profileService.js  ← Profile/addresses/orders
│   ├── screens/
│   │   ├── LoginScreen.js     ← Login UI
│   │   ├── ProfileScreen.js   ← Profile UI
│   │   └── AddressScreen.js   ← Addresses UI
│   └── App.js                 ← Main app
```

---

## 1️⃣ API Config (`src/api/config.js`)

```javascript
// src/api/config.js
export const API_BASE_URL =
  "https://marquebackend-production.up.railway.app/api/v1";

export const API_ENDPOINTS = {
  // Auth
  SEND_CODE: `${API_BASE_URL}/auth/send-verification`,
  VERIFY_CODE: `${API_BASE_URL}/auth/verify-code`,
  PROFILE: `${API_BASE_URL}/auth/profile`,
  LOGOUT: `${API_BASE_URL}/auth/logout`,

  // Profile
  ADDRESSES: `${API_BASE_URL}/profile/addresses`,
  PAYMENT_METHODS: `${API_BASE_URL}/profile/payment-methods`,
  ORDERS: `${API_BASE_URL}/profile/orders`,
  NOTIFICATIONS: `${API_BASE_URL}/profile/notifications`,
};
```

---

## 2️⃣ Auth Service (`src/services/authService.js`)

```javascript
// src/services/authService.js
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_ENDPOINTS } from "../api/config";

const TOKEN_KEY = "auth_token";
const USER_KEY = "user_data";

class AuthService {
  // Send verification code
  async sendCode(phoneNumber) {
    const response = await fetch(API_ENDPOINTS.SEND_CODE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: phoneNumber }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Failed to send code");
    return data;
  }

  // Verify code and login
  async verifyCode(phoneNumber, code) {
    const response = await fetch(API_ENDPOINTS.VERIFY_CODE, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone_number: phoneNumber, code: code }),
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Invalid code");

    // Store token and user
    await AsyncStorage.setItem(TOKEN_KEY, data.access_token);
    await AsyncStorage.setItem(USER_KEY, JSON.stringify(data.user));

    return data;
  }

  // Get profile
  async getProfile() {
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    if (!token) throw new Error("Not logged in");

    const response = await fetch(API_ENDPOINTS.PROFILE, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    });

    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Failed to get profile");

    await AsyncStorage.setItem(USER_KEY, JSON.stringify(data));
    return data;
  }

  // Update profile
  async updateProfile(updates) {
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
    if (!response.ok) throw new Error(data.detail || "Failed to update");

    await AsyncStorage.setItem(USER_KEY, JSON.stringify(data));
    return data;
  }

  // Logout
  async logout() {
    const token = await AsyncStorage.getItem(TOKEN_KEY);

    if (token) {
      try {
        await fetch(API_ENDPOINTS.LOGOUT, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
      } catch (error) {
        console.log("Logout API error:", error);
      }
    }

    await AsyncStorage.removeItem(TOKEN_KEY);
    await AsyncStorage.removeItem(USER_KEY);
  }

  // Check if logged in
  async isLoggedIn() {
    const token = await AsyncStorage.getItem(TOKEN_KEY);
    return !!token;
  }

  // Get token
  async getToken() {
    return await AsyncStorage.getItem(TOKEN_KEY);
  }

  // Get user
  async getUser() {
    const userData = await AsyncStorage.getItem(USER_KEY);
    return userData ? JSON.parse(userData) : null;
  }
}

export default new AuthService();
```

---

## 3️⃣ Profile Service (`src/services/profileService.js`)

```javascript
// src/services/profileService.js
import AsyncStorage from "@react-native-async-storage/async-storage";
import { API_ENDPOINTS } from "../api/config";

class ProfileService {
  async getToken() {
    return await AsyncStorage.getItem("auth_token");
  }

  async request(endpoint, method = "GET", body = null) {
    const token = await this.getToken();

    const options = {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(endpoint, options);
    const data = await response.json();

    if (!response.ok) throw new Error(data.detail || "Request failed");
    return data;
  }

  // Addresses
  async getAddresses() {
    return await this.request(API_ENDPOINTS.ADDRESSES);
  }

  async createAddress(addressData) {
    return await this.request(API_ENDPOINTS.ADDRESSES, "POST", addressData);
  }

  async updateAddress(id, addressData) {
    return await this.request(
      `${API_ENDPOINTS.ADDRESSES}/${id}`,
      "PUT",
      addressData
    );
  }

  async deleteAddress(id) {
    return await this.request(`${API_ENDPOINTS.ADDRESSES}/${id}`, "DELETE");
  }

  // Orders
  async getOrders() {
    return await this.request(API_ENDPOINTS.ORDERS);
  }

  async getOrder(id) {
    return await this.request(`${API_ENDPOINTS.ORDERS}/${id}`);
  }

  async cancelOrder(id) {
    return await this.request(`${API_ENDPOINTS.ORDERS}/${id}/cancel`, "POST");
  }

  // Notifications
  async getNotifications() {
    return await this.request(API_ENDPOINTS.NOTIFICATIONS);
  }

  async markAsRead(id) {
    return await this.request(
      `${API_ENDPOINTS.NOTIFICATIONS}/${id}/read`,
      "PUT"
    );
  }

  async markAllAsRead() {
    return await this.request(`${API_ENDPOINTS.NOTIFICATIONS}/read-all`, "PUT");
  }
}

export default new ProfileService();
```

---

## 4️⃣ Login Screen (`src/screens/LoginScreen.js`)

```javascript
// src/screens/LoginScreen.js
import React, { useState } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import authService from "../services/authService";

export default function LoginScreen({ navigation }) {
  const [phone, setPhone] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState("phone"); // 'phone' or 'code'
  const [loading, setLoading] = useState(false);

  const handleSendCode = async () => {
    if (!phone) {
      Alert.alert("Error", "Please enter your phone number");
      return;
    }

    setLoading(true);
    try {
      await authService.sendCode(phone);
      Alert.alert("Success", "Code sent to your phone!");
      setStep("code");
    } catch (error) {
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!code) {
      Alert.alert("Error", "Please enter the verification code");
      return;
    }

    setLoading(true);
    try {
      const result = await authService.verifyCode(phone, code);

      if (result.is_new_user) {
        Alert.alert("Welcome!", "Your account has been created");
      } else {
        Alert.alert("Welcome back!", "Login successful");
      }

      navigation.replace("Home");
    } catch (error) {
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>
        {step === "phone" ? "Enter Phone Number" : "Enter Verification Code"}
      </Text>

      {step === "phone" ? (
        <>
          <TextInput
            style={styles.input}
            placeholder="Phone (e.g., +13128059851)"
            value={phone}
            onChangeText={setPhone}
            keyboardType="phone-pad"
            autoCapitalize="none"
          />

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleSendCode}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Send Code</Text>
            )}
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Text style={styles.subtitle}>Code sent to {phone}</Text>

          <TextInput
            style={styles.input}
            placeholder="6-digit code"
            value={code}
            onChangeText={setCode}
            keyboardType="number-pad"
            maxLength={6}
          />

          <TouchableOpacity
            style={[styles.button, loading && styles.buttonDisabled]}
            onPress={handleVerifyCode}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Verify</Text>
            )}
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.backButton}
            onPress={() => setStep("phone")}
          >
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: "center",
    backgroundColor: "#fff",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 10,
    textAlign: "center",
  },
  subtitle: {
    fontSize: 14,
    color: "#666",
    marginBottom: 20,
    textAlign: "center",
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 15,
    fontSize: 16,
    marginBottom: 20,
  },
  button: {
    backgroundColor: "#007AFF",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  backButton: {
    marginTop: 20,
    alignItems: "center",
  },
  backButtonText: {
    color: "#007AFF",
    fontSize: 16,
  },
});
```

---

## 5️⃣ Profile Screen (`src/screens/ProfileScreen.js`)

```javascript
// src/screens/ProfileScreen.js
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from "react-native";
import authService from "../services/authService";

export default function ProfileScreen({ navigation }) {
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
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async () => {
    setLoading(true);
    try {
      const updated = await authService.updateProfile({ full_name: fullName });
      setProfile(updated);
      setEditing(false);
      Alert.alert("Success", "Profile updated!");
    } catch (error) {
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert("Logout", "Are you sure?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Logout",
        style: "destructive",
        onPress: async () => {
          await authService.logout();
          navigation.replace("Login");
        },
      },
    ]);
  };

  if (loading && !profile) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>My Profile</Text>

      {editing ? (
        <View style={styles.editSection}>
          <Text style={styles.label}>Full Name</Text>
          <TextInput
            style={styles.input}
            value={fullName}
            onChangeText={setFullName}
            placeholder="Enter your name"
          />

          <TouchableOpacity style={styles.button} onPress={handleUpdate}>
            <Text style={styles.buttonText}>Save</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.cancelButton]}
            onPress={() => setEditing(false)}
          >
            <Text style={styles.buttonText}>Cancel</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <View style={styles.infoSection}>
          <InfoRow label="Phone" value={profile?.formatted_phone} />
          <InfoRow label="Name" value={profile?.full_name || "Not set"} />
          <InfoRow label="Market" value={profile?.market?.toUpperCase()} />
          <InfoRow label="Country" value={profile?.country} />
          <InfoRow label="Currency" value={profile?.currency_code} />
          <InfoRow
            label="Status"
            value={profile?.is_active ? "🟢 Active" : "🔴 Inactive"}
          />
          <InfoRow
            label="Verified"
            value={profile?.is_verified ? "✅ Yes" : "❌ No"}
          />

          <TouchableOpacity
            style={styles.button}
            onPress={() => setEditing(true)}
          >
            <Text style={styles.buttonText}>Edit Profile</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.navigate("Addresses")}
          >
            <Text style={styles.buttonText}>My Addresses</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.logoutButton]}
            onPress={handleLogout}
          >
            <Text style={styles.buttonText}>Logout</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

function InfoRow({ label, value }) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}:</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 20,
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    marginBottom: 30,
  },
  infoSection: {
    marginBottom: 20,
  },
  infoRow: {
    flexDirection: "row",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f0f0f0",
  },
  infoLabel: {
    fontSize: 16,
    fontWeight: "600",
    width: 100,
    color: "#666",
  },
  infoValue: {
    fontSize: 16,
    flex: 1,
    color: "#000",
  },
  editSection: {
    marginTop: 20,
  },
  label: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 20,
  },
  button: {
    backgroundColor: "#007AFF",
    padding: 15,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 10,
  },
  buttonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  cancelButton: {
    backgroundColor: "#666",
  },
  logoutButton: {
    backgroundColor: "#FF3B30",
    marginTop: 20,
  },
});
```

---

## 6️⃣ Addresses Screen (`src/screens/AddressScreen.js`)

```javascript
// src/screens/AddressScreen.js
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import profileService from "../services/profileService";

export default function AddressScreen() {
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
      Alert.alert("Error", error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = (id) => {
    Alert.alert("Delete Address", "Are you sure?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          try {
            await profileService.deleteAddress(id);
            loadAddresses();
            Alert.alert("Success", "Address deleted");
          } catch (error) {
            Alert.alert("Error", error.message);
          }
        },
      },
    ]);
  };

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>My Addresses</Text>

      {addresses.length === 0 ? (
        <Text style={styles.emptyText}>No addresses yet</Text>
      ) : (
        <FlatList
          data={addresses}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <View style={styles.addressCard}>
              <View style={styles.addressHeader}>
                <Text style={styles.addressType}>{item.address_type}</Text>
                {item.is_default && (
                  <Text style={styles.defaultBadge}>Default</Text>
                )}
              </View>

              <Text style={styles.addressText}>{item.street_address}</Text>
              <Text style={styles.addressText}>
                {item.city}, {item.state} {item.postal_code}
              </Text>
              <Text style={styles.addressText}>{item.country}</Text>

              <TouchableOpacity
                style={styles.deleteButton}
                onPress={() => handleDelete(item.id)}
              >
                <Text style={styles.deleteButtonText}>Delete</Text>
              </TouchableOpacity>
            </View>
          )}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    padding: 20,
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
  },
  emptyText: {
    textAlign: "center",
    color: "#666",
    marginTop: 40,
  },
  addressCard: {
    borderWidth: 1,
    borderColor: "#ddd",
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
  },
  addressHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 10,
  },
  addressType: {
    fontSize: 18,
    fontWeight: "bold",
    textTransform: "capitalize",
  },
  defaultBadge: {
    backgroundColor: "#34C759",
    color: "#fff",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    fontSize: 12,
    fontWeight: "600",
  },
  addressText: {
    fontSize: 14,
    color: "#666",
    marginBottom: 5,
  },
  deleteButton: {
    marginTop: 10,
    backgroundColor: "#FF3B30",
    padding: 10,
    borderRadius: 6,
    alignItems: "center",
  },
  deleteButtonText: {
    color: "#fff",
    fontWeight: "600",
  },
});
```

---

## 7️⃣ App Navigation (`src/App.js`)

```javascript
// src/App.js (if using React Navigation)
import React, { useState, useEffect } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createStackNavigator } from "@react-navigation/stack";
import authService from "./services/authService";

import LoginScreen from "./screens/LoginScreen";
import ProfileScreen from "./screens/ProfileScreen";
import AddressScreen from "./screens/AddressScreen";

const Stack = createStackNavigator();

export default function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const loggedIn = await authService.isLoggedIn();
    setIsLoggedIn(loggedIn);
    setLoading(false);
  };

  if (loading) {
    return null; // Or splash screen
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
            <Stack.Screen name="Home" component={ProfileScreen} />
            <Stack.Screen name="Addresses" component={AddressScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

---

## 🚀 Installation

```bash
# Install required packages
npm install @react-native-async-storage/async-storage
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context

# iOS only
cd ios && pod install && cd ..
```

---

## ✅ Done!

**You now have**:

- ✅ Complete login flow with SMS verification
- ✅ Profile management
- ✅ Address management
- ✅ Proper token storage
- ✅ Logout functionality
- ✅ Error handling

**Just copy the files above into your project and start using!** 🎉
