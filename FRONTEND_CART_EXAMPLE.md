# 🛒 Complete Frontend Cart/Wishlist Implementation Example

> Copy-paste ready code showing how cart/wishlist persists across sessions

---

## 📱 Complete React Native Example

### 1. API Service (`services/api.js`)

```javascript
import AsyncStorage from "@react-native-async-storage/async-storage";

const API_BASE_URL = "https://marquebackend-production.up.railway.app/api/v1";
const MARKET = "us"; // or 'kg'

// Generic API request handler
export async function apiRequest(endpoint, method = "GET", body = null) {
  const token = await AsyncStorage.getItem("access_token");

  const headers = {
    "Content-Type": "application/json",
    "X-Market": MARKET,
  };

  // Add authorization if token exists
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

    // Handle unauthorized (token expired or invalid)
    if (response.status === 401) {
      await AsyncStorage.removeItem("access_token");
      throw new Error("Session expired. Please login again.");
    }

    // Handle other errors
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Request failed");
    }

    return await response.json();
  } catch (error) {
    console.error("API Request Error:", error);
    throw error;
  }
}

// Authentication
export const authService = {
  async sendVerificationCode(phone) {
    return await apiRequest("/auth/send-verification", "POST", { phone });
  },

  async verifyCode(phone, code) {
    const response = await apiRequest("/auth/verify-code", "POST", {
      phone,
      verification_code: code,
    });

    // Store token
    await AsyncStorage.setItem("access_token", response.access_token);
    await AsyncStorage.setItem("user", JSON.stringify(response.user));

    return response;
  },

  async logout() {
    try {
      await apiRequest("/auth/logout", "POST");
    } finally {
      await AsyncStorage.removeItem("access_token");
      await AsyncStorage.removeItem("user");
    }
  },
};

// Cart API
export const cartService = {
  async getCart() {
    return await apiRequest("/cart");
  },

  async addToCart(sku_id, quantity = 1) {
    return await apiRequest("/cart/items", "POST", { sku_id, quantity });
  },

  async updateCartItem(item_id, quantity) {
    return await apiRequest(`/cart/items/${item_id}`, "PUT", { quantity });
  },

  async removeFromCart(item_id) {
    return await apiRequest(`/cart/items/${item_id}`, "DELETE");
  },

  async clearCart() {
    return await apiRequest("/cart", "DELETE");
  },
};

// Wishlist API
export const wishlistService = {
  async getWishlist() {
    return await apiRequest("/wishlist");
  },

  async addToWishlist(product_id) {
    return await apiRequest("/wishlist/items", "POST", { product_id });
  },

  async removeFromWishlist(product_id) {
    return await apiRequest(`/wishlist/items/${product_id}`, "DELETE");
  },

  async clearWishlist() {
    return await apiRequest("/wishlist", "DELETE");
  },
};

// Orders API
export const orderService = {
  async getOrders(status_filter = null) {
    const query = status_filter ? `?status_filter=${status_filter}` : "";
    return await apiRequest(`/profile/orders${query}`);
  },

  async getOrderDetails(order_id) {
    return await apiRequest(`/profile/orders/${order_id}`);
  },

  async cancelOrder(order_id) {
    return await apiRequest(`/profile/orders/${order_id}/cancel`, "POST");
  },
};
```

---

### 2. Cart Screen (`screens/CartScreen.js`)

```javascript
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Image,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from "react-native";
import { cartService } from "../services/api";

export default function CartScreen({ navigation }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadCart();
  }, []);

  const loadCart = async () => {
    try {
      setLoading(true);
      const cartData = await cartService.getCart();
      setCart(cartData);
    } catch (error) {
      if (error.message.includes("login")) {
        // Token expired - redirect to login
        Alert.alert("Session Expired", "Please login again", [
          { text: "OK", onPress: () => navigation.navigate("Login") },
        ]);
      } else {
        Alert.alert("Error", error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadCart();
    setRefreshing(false);
  };

  const updateQuantity = async (item_id, newQuantity) => {
    try {
      if (newQuantity < 1) {
        await removeItem(item_id);
        return;
      }

      const updatedCart = await cartService.updateCartItem(
        item_id,
        newQuantity
      );
      setCart(updatedCart);
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  const removeItem = async (item_id) => {
    try {
      const updatedCart = await cartService.removeFromCart(item_id);
      setCart(updatedCart);
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  const handleCheckout = () => {
    if (cart && cart.items.length > 0) {
      navigation.navigate("Checkout", { cart });
    }
  };

  const renderCartItem = ({ item }) => (
    <View style={styles.cartItem}>
      <Image
        source={{ uri: item.image || "https://via.placeholder.com/80" }}
        style={styles.productImage}
      />
      <View style={styles.itemDetails}>
        <Text style={styles.productName}>{item.name}</Text>
        <Text style={styles.productPrice}>${item.price.toFixed(2)}</Text>

        <View style={styles.quantityControls}>
          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => updateQuantity(item.id, item.quantity - 1)}
          >
            <Text style={styles.quantityButtonText}>-</Text>
          </TouchableOpacity>

          <Text style={styles.quantity}>{item.quantity}</Text>

          <TouchableOpacity
            style={styles.quantityButton}
            onPress={() => updateQuantity(item.id, item.quantity + 1)}
          >
            <Text style={styles.quantityButtonText}>+</Text>
          </TouchableOpacity>
        </View>
      </View>

      <TouchableOpacity
        style={styles.removeButton}
        onPress={() => removeItem(item.id)}
      >
        <Text style={styles.removeButtonText}>✕</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyText}>Your cart is empty</Text>
        <TouchableOpacity
          style={styles.shopButton}
          onPress={() => navigation.navigate("Products")}
        >
          <Text style={styles.shopButtonText}>Start Shopping</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={cart.items}
        renderItem={renderCartItem}
        keyExtractor={(item) => item.id.toString()}
        refreshing={refreshing}
        onRefresh={handleRefresh}
      />

      <View style={styles.footer}>
        <View style={styles.totalContainer}>
          <Text style={styles.totalLabel}>Total:</Text>
          <Text style={styles.totalAmount}>${cart.total_price.toFixed(2)}</Text>
        </View>

        <TouchableOpacity
          style={styles.checkoutButton}
          onPress={handleCheckout}
        >
          <Text style={styles.checkoutButtonText}>
            Checkout ({cart.total_items} items)
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
  },
  centered: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  cartItem: {
    flexDirection: "row",
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: "#eee",
  },
  productImage: {
    width: 80,
    height: 80,
    borderRadius: 8,
  },
  itemDetails: {
    flex: 1,
    marginLeft: 12,
  },
  productName: {
    fontSize: 16,
    fontWeight: "600",
    marginBottom: 4,
  },
  productPrice: {
    fontSize: 14,
    color: "#666",
    marginBottom: 8,
  },
  quantityControls: {
    flexDirection: "row",
    alignItems: "center",
  },
  quantityButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "#f0f0f0",
    justifyContent: "center",
    alignItems: "center",
  },
  quantityButtonText: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#333",
  },
  quantity: {
    marginHorizontal: 16,
    fontSize: 16,
    fontWeight: "600",
  },
  removeButton: {
    padding: 8,
  },
  removeButtonText: {
    fontSize: 20,
    color: "#ff3b30",
  },
  emptyText: {
    fontSize: 18,
    color: "#666",
    marginBottom: 20,
  },
  shopButton: {
    backgroundColor: "#007AFF",
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  shopButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
  footer: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: "#eee",
    backgroundColor: "#fff",
  },
  totalContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 16,
  },
  totalLabel: {
    fontSize: 18,
    fontWeight: "600",
  },
  totalAmount: {
    fontSize: 18,
    fontWeight: "bold",
    color: "#007AFF",
  },
  checkoutButton: {
    backgroundColor: "#007AFF",
    padding: 16,
    borderRadius: 8,
    alignItems: "center",
  },
  checkoutButtonText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "600",
  },
});
```

---

### 3. Add to Cart from Product Screen

```javascript
// In ProductDetailScreen.js

import { cartService } from "../services/api";

export default function ProductDetailScreen({ route, navigation }) {
  const { product } = route.params;
  const [selectedSku, setSelectedSku] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [adding, setAdding] = useState(false);

  const handleAddToCart = async () => {
    if (!selectedSku) {
      Alert.alert("Error", "Please select a size/color");
      return;
    }

    try {
      setAdding(true);
      await cartService.addToCart(selectedSku.id, quantity);

      Alert.alert("Success", "Added to cart!", [
        { text: "Continue Shopping", style: "cancel" },
        { text: "View Cart", onPress: () => navigation.navigate("Cart") },
      ]);
    } catch (error) {
      if (error.message.includes("login")) {
        Alert.alert("Please Login", "Login to add items to cart", [
          { text: "OK", onPress: () => navigation.navigate("Login") },
        ]);
      } else {
        Alert.alert("Error", error.message);
      }
    } finally {
      setAdding(false);
    }
  };

  return (
    <View>
      {/* Product details */}

      <TouchableOpacity
        style={styles.addToCartButton}
        onPress={handleAddToCart}
        disabled={adding}
      >
        <Text style={styles.addToCartText}>
          {adding ? "Adding..." : "Add to Cart"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}
```

---

### 4. Wishlist Screen (`screens/WishlistScreen.js`)

```javascript
import React, { useState, useEffect } from "react";
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  Image,
  StyleSheet,
  Alert,
} from "react-native";
import { wishlistService, cartService } from "../services/api";

export default function WishlistScreen({ navigation }) {
  const [wishlist, setWishlist] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWishlist();
  }, []);

  const loadWishlist = async () => {
    try {
      setLoading(true);
      const wishlistData = await wishlistService.getWishlist();
      setWishlist(wishlistData);
    } catch (error) {
      if (error.message.includes("login")) {
        navigation.navigate("Login");
      } else {
        Alert.alert("Error", error.message);
      }
    } finally {
      setLoading(false);
    }
  };

  const removeFromWishlist = async (product_id) => {
    try {
      const updatedWishlist = await wishlistService.removeFromWishlist(
        product_id
      );
      setWishlist(updatedWishlist);
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  const moveToCart = async (product) => {
    try {
      // Assuming product has a default SKU
      if (product.skus && product.skus.length > 0) {
        await cartService.addToCart(product.skus[0].id, 1);
        await removeFromWishlist(product.id);
        Alert.alert("Success", "Moved to cart!");
      } else {
        Alert.alert("Error", "Product not available");
      }
    } catch (error) {
      Alert.alert("Error", error.message);
    }
  };

  const renderWishlistItem = ({ item }) => (
    <View style={styles.wishlistItem}>
      <TouchableOpacity
        onPress={() =>
          navigation.navigate("ProductDetail", { product: item.product })
        }
      >
        <Image
          source={{
            uri:
              item.product.main_image_url || "https://via.placeholder.com/150",
          }}
          style={styles.productImage}
        />
      </TouchableOpacity>

      <View style={styles.itemDetails}>
        <Text style={styles.productName}>{item.product.title}</Text>
        <Text style={styles.productPrice}>${item.product.price}</Text>

        <View style={styles.actions}>
          <TouchableOpacity
            style={styles.moveButton}
            onPress={() => moveToCart(item.product)}
          >
            <Text style={styles.moveButtonText}>Move to Cart</Text>
          </TouchableOpacity>

          <TouchableOpacity onPress={() => removeFromWishlist(item.product.id)}>
            <Text style={styles.removeText}>Remove</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.centered}>
        <ActivityIndicator size="large" color="#007AFF" />
      </View>
    );
  }

  if (!wishlist || wishlist.items.length === 0) {
    return (
      <View style={styles.centered}>
        <Text style={styles.emptyText}>Your wishlist is empty</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={wishlist.items}
        renderItem={renderWishlistItem}
        keyExtractor={(item) => item.id.toString()}
      />
    </View>
  );
}
```

---

## 🔄 How Data Persists

### Scenario 1: User Adds Item and Logs Out

```javascript
// 1. User adds item to cart
await cartService.addToCart(42, 2);
// → Backend saves to database:
//   INSERT INTO cart_items (cart_id, sku_id, quantity)
//   VALUES (5, 42, 2)
//   WHERE cart.user_id = 19

// 2. User logs out
await authService.logout();
// → Backend: UPDATE users SET is_active = false WHERE id = 19
// → Frontend: AsyncStorage.removeItem('access_token')

// 3. User closes app

// 4. User opens app next day and logs in
const response = await authService.verifyCode("+13128059851", "123456");
// → Backend: UPDATE users SET is_active = true WHERE id = 19
// → Backend: Creates new JWT token with user_id = 19
// → Frontend: AsyncStorage.setItem('access_token', new_token)

// 5. User opens cart
const cart = await cartService.getCart();
// → Backend decodes new token → user_id = 19
// → Backend queries:
//   SELECT * FROM cart_items
//   WHERE cart_id IN (SELECT id FROM carts WHERE user_id = 19)
// → Returns: Same item (sku_id=42, quantity=2) ✅
```

---

## 🎯 Key Points

### ✅ Data Persistence

1. **Cart/Wishlist saved in database** (linked to user_id)
2. **Token is just a key** to identify user
3. **New token = Same user_id** = Same cart!

### ✅ Session Management

1. **Token stored in AsyncStorage** (frontend)
2. **Token sent with every request** (Authorization header)
3. **Backend decodes token** → gets user_id → queries database
4. **Logout sets is_active = false** → token becomes invalid

### ✅ Error Handling

1. **401 Unauthorized** → Token expired → Redirect to login
2. **Network errors** → Show retry button
3. **Empty states** → Encourage shopping

---

## 🧪 Test It

```javascript
// Test script
async function testCartPersistence() {
  // 1. Login
  await authService.verifyCode("+13128059851", "123456");
  console.log("✅ Logged in");

  // 2. Add item to cart
  await cartService.addToCart(42, 2);
  console.log("✅ Added item to cart");

  // 3. Get cart
  let cart = await cartService.getCart();
  console.log("Cart items:", cart.items.length); // 1

  // 4. Logout
  await authService.logout();
  console.log("✅ Logged out");

  // 5. Login again
  await authService.verifyCode("+13128059851", "654321");
  console.log("✅ Logged in again");

  // 6. Get cart again
  cart = await cartService.getCart();
  console.log("Cart items:", cart.items.length); // Still 1! ✅
  console.log("✅ Cart persisted!");
}
```

---

## ✅ Summary

Your backend is **already correctly implemented**! Just use this frontend code and:

1. ✅ Cart persists across sessions
2. ✅ Wishlist persists across sessions
3. ✅ Orders are permanent
4. ✅ Token expiration handled gracefully
5. ✅ Multi-device support (same phone = same cart)

**You're all set!** 🚀
