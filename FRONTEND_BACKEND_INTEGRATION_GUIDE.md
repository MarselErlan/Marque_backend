# 🚀 Frontend-Backend Integration Guide

## 📋 Overview

This guide shows how to connect your frontend to the **new wishlist API** that accepts `user_id` and `product_id` directly. The API is stateless, easy to use, and production-ready!

## 🎯 API Base URL

```
https://marquebackend-production.up.railway.app/api/v1
```

## 🔐 Authentication Flow

### 1. User Registration/Login

```javascript
// Send verification code
const sendCode = async (phoneNumber) => {
  const response = await fetch(
    "https://marquebackend-production.up.railway.app/api/v1/auth/send-code",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        phone: phoneNumber,
      }),
    }
  );

  return await response.json();
};

// Verify code and get user info
const verifyCode = async (phoneNumber, code) => {
  const response = await fetch(
    "https://marquebackend-production.up.railway.app/api/v1/auth/verify-code",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        phone: phoneNumber,
        verification_code: code,
      }),
    }
  );

  const data = await response.json();

  if (data.success) {
    // Store user info in localStorage
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("phone_number", phoneNumber);
  }

  return data;
};
```

## 🛒 Wishlist API Integration

### 1. Get User's Wishlist

```javascript
const getWishlist = async (userId) => {
  try {
    const response = await fetch(
      "https://marquebackend-production.up.railway.app/api/v1/wishlist/get",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.items || [];
    } else {
      console.error("Failed to get wishlist:", data.message);
      return [];
    }
  } catch (error) {
    console.error("Error getting wishlist:", error);
    return [];
  }
};
```

### 2. Add Product to Wishlist

```javascript
const addToWishlist = async (userId, productId) => {
  try {
    const response = await fetch(
      "https://marquebackend-production.up.railway.app/api/v1/wishlist/add",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          product_id: productId,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.items || [];
    } else {
      console.error("Failed to add to wishlist:", data.message);
      throw new Error(data.message);
    }
  } catch (error) {
    console.error("Error adding to wishlist:", error);
    throw error;
  }
};
```

### 3. Remove Product from Wishlist

```javascript
const removeFromWishlist = async (userId, productId) => {
  try {
    const response = await fetch(
      "https://marquebackend-production.up.railway.app/api/v1/wishlist/remove",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          product_id: productId,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.items || [];
    } else {
      console.error("Failed to remove from wishlist:", data.message);
      throw new Error(data.message);
    }
  } catch (error) {
    console.error("Error removing from wishlist:", error);
    throw error;
  }
};
```

### 4. Clear Entire Wishlist

```javascript
const clearWishlist = async (userId) => {
  try {
    const response = await fetch(
      "https://marquebackend-production.up.railway.app/api/v1/wishlist/clear",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return [];
    } else {
      console.error("Failed to clear wishlist:", data.message);
      throw new Error(data.message);
    }
  } catch (error) {
    console.error("Error clearing wishlist:", error);
    throw error;
  }
};
```

## 🛍️ Shopping Cart API Integration

### 1. Get User's Cart

```javascript
const getCart = async (userId) => {
  try {
    const response = await fetch(
      "https://marquebackend-production.up.railway.app/api/v1/cart/get",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.items || [];
    } else {
      console.error("Failed to get cart:", data.message);
      return [];
    }
  } catch (error) {
    console.error("Error getting cart:", error);
    return [];
  }
};
```

### 2. Add Product to Cart

```javascript
const addToCart = async (userId, productId, quantity = 1) => {
  try {
    const response = await fetch(
      "https://marquebackend-production.up.railway.app/api/v1/cart/add",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          user_id: userId,
          product_id: productId,
          quantity: quantity,
        }),
      }
    );

    const data = await response.json();

    if (response.ok) {
      return data.items || [];
    } else {
      console.error("Failed to add to cart:", data.message);
      throw new Error(data.message);
    }
  } catch (error) {
    console.error("Error adding to cart:", error);
    throw error;
  }
};
```

## 📱 React Component Examples

### Wishlist Component

```jsx
import React, { useState, useEffect } from "react";

const WishlistComponent = () => {
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const userId = localStorage.getItem("user_id");

  useEffect(() => {
    if (userId) {
      loadWishlist();
    }
  }, [userId]);

  const loadWishlist = async () => {
    setLoading(true);
    try {
      const items = await getWishlist(userId);
      setWishlistItems(items);
    } catch (error) {
      console.error("Failed to load wishlist:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToWishlist = async (productId) => {
    try {
      const items = await addToWishlist(userId, productId);
      setWishlistItems(items);
    } catch (error) {
      alert("Failed to add to wishlist: " + error.message);
    }
  };

  const handleRemoveFromWishlist = async (productId) => {
    try {
      const items = await removeFromWishlist(userId, productId);
      setWishlistItems(items);
    } catch (error) {
      alert("Failed to remove from wishlist: " + error.message);
    }
  };

  const isInWishlist = (productId) => {
    return wishlistItems.some((item) => item.product.id === productId);
  };

  if (loading) {
    return <div>Loading wishlist...</div>;
  }

  return (
    <div className="wishlist">
      <h2>My Wishlist</h2>
      {wishlistItems.length === 0 ? (
        <p>Your wishlist is empty</p>
      ) : (
        <div className="wishlist-items">
          {wishlistItems.map((item) => (
            <div key={item.id} className="wishlist-item">
              <img src={item.product.image} alt={item.product.name} />
              <h3>{item.product.name}</h3>
              <p>${item.product.price}</p>
              <button onClick={() => handleRemoveFromWishlist(item.product.id)}>
                Remove from Wishlist
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default WishlistComponent;
```

### Product Card Component

```jsx
import React, { useState } from "react";

const ProductCard = ({ product }) => {
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [loading, setLoading] = useState(false);
  const userId = localStorage.getItem("user_id");

  const handleWishlistToggle = async () => {
    if (!userId) {
      alert("Please login first");
      return;
    }

    setLoading(true);
    try {
      if (isInWishlist) {
        await removeFromWishlist(userId, product.id);
        setIsInWishlist(false);
      } else {
        await addToWishlist(userId, product.id);
        setIsInWishlist(true);
      }
    } catch (error) {
      alert("Failed to update wishlist: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!userId) {
      alert("Please login first");
      return;
    }

    setLoading(true);
    try {
      await addToCart(userId, product.id, 1);
      alert("Added to cart!");
    } catch (error) {
      alert("Failed to add to cart: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p>${product.price}</p>
      <div className="product-actions">
        <button
          onClick={handleWishlistToggle}
          disabled={loading}
          className={isInWishlist ? "in-wishlist" : ""}
        >
          {isInWishlist ? "❤️ In Wishlist" : "🤍 Add to Wishlist"}
        </button>
        <button onClick={handleAddToCart} disabled={loading}>
          Add to Cart
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
```

## 🔄 State Management (Redux/Zustand)

### Zustand Store Example

```javascript
import { create } from "zustand";

const useWishlistStore = create((set, get) => ({
  items: [],
  loading: false,

  // Actions
  loadWishlist: async (userId) => {
    set({ loading: true });
    try {
      const items = await getWishlist(userId);
      set({ items, loading: false });
    } catch (error) {
      console.error("Failed to load wishlist:", error);
      set({ loading: false });
    }
  },

  addToWishlist: async (userId, productId) => {
    set({ loading: true });
    try {
      const items = await addToWishlist(userId, productId);
      set({ items, loading: false });
    } catch (error) {
      console.error("Failed to add to wishlist:", error);
      set({ loading: false });
      throw error;
    }
  },

  removeFromWishlist: async (userId, productId) => {
    set({ loading: true });
    try {
      const items = await removeFromWishlist(userId, productId);
      set({ items, loading: false });
    } catch (error) {
      console.error("Failed to remove from wishlist:", error);
      set({ loading: false });
      throw error;
    }
  },

  clearWishlist: async (userId) => {
    set({ loading: true });
    try {
      await clearWishlist(userId);
      set({ items: [], loading: false });
    } catch (error) {
      console.error("Failed to clear wishlist:", error);
      set({ loading: false });
      throw error;
    }
  },

  isInWishlist: (productId) => {
    return get().items.some((item) => item.product.id === productId);
  },
}));

export default useWishlistStore;
```

## 📱 Mobile App Integration (React Native)

### AsyncStorage Setup

```javascript
import AsyncStorage from "@react-native-async-storage/async-storage";

// Store user data
const storeUserData = async (userData) => {
  try {
    await AsyncStorage.setItem("user_id", userData.user_id.toString());
    await AsyncStorage.setItem("access_token", userData.access_token);
    await AsyncStorage.setItem("phone_number", userData.phone_number);
  } catch (error) {
    console.error("Error storing user data:", error);
  }
};

// Get user data
const getUserData = async () => {
  try {
    const userId = await AsyncStorage.getItem("user_id");
    const accessToken = await AsyncStorage.getItem("access_token");
    const phoneNumber = await AsyncStorage.getItem("phone_number");

    return {
      user_id: userId ? parseInt(userId) : null,
      access_token: accessToken,
      phone_number: phoneNumber,
    };
  } catch (error) {
    console.error("Error getting user data:", error);
    return null;
  }
};
```

## 🎨 CSS Styling Examples

```css
/* Wishlist Styles */
.wishlist {
  padding: 20px;
}

.wishlist-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.wishlist-item {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
}

.wishlist-item img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 4px;
}

/* Product Card Styles */
.product-card {
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 15px;
  margin: 10px;
}

.product-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.product-actions button {
  flex: 1;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.product-actions button.in-wishlist {
  background-color: #ff6b6b;
  color: white;
}

.product-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
```

## 🚨 Error Handling

### Global Error Handler

```javascript
const handleApiError = (error, context) => {
  console.error(`API Error in ${context}:`, error);

  if (error.message.includes("User not found")) {
    // Redirect to login
    localStorage.removeItem("user_id");
    localStorage.removeItem("access_token");
    window.location.href = "/login";
  } else if (error.message.includes("Product not found")) {
    alert("Product not found. Please refresh the page.");
  } else {
    alert("Something went wrong. Please try again.");
  }
};
```

## 🔧 Environment Configuration

### Environment Variables

```javascript
// config.js
const config = {
  development: {
    API_BASE_URL: "http://localhost:8000/api/v1",
  },
  production: {
    API_BASE_URL: "https://marquebackend-production.up.railway.app/api/v1",
  },
};

const environment = process.env.NODE_ENV || "development";
export const API_BASE_URL = config[environment].API_BASE_URL;
```

## 📊 Testing Examples

### Jest Test Examples

```javascript
// wishlist.test.js
import { getWishlist, addToWishlist, removeFromWishlist } from "./wishlistApi";

describe("Wishlist API", () => {
  test("should get wishlist for user", async () => {
    const mockUserId = 123;
    const mockResponse = {
      id: 1,
      user_id: mockUserId,
      items: [],
    };

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockResponse),
    });

    const result = await getWishlist(mockUserId);
    expect(result).toEqual([]);
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/wishlist/get"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ user_id: mockUserId }),
      })
    );
  });

  test("should add product to wishlist", async () => {
    const mockUserId = 123;
    const mockProductId = 456;

    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ items: [] }),
    });

    await addToWishlist(mockUserId, mockProductId);

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/wishlist/add"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          user_id: mockUserId,
          product_id: mockProductId,
        }),
      })
    );
  });
});
```

## 🎯 Key Benefits of This API Design

### ✅ **Stateless Design**

- No JWT token dependency
- Easy to test and debug
- Works with any user ID

### ✅ **Admin-Friendly**

- Admins can manage any user's wishlist
- No authentication required for admin operations

### ✅ **Frontend-Friendly**

- Simple POST requests with JSON body
- Clear error messages
- Consistent response format

### ✅ **Scalable**

- Works with multiple markets (US/KG)
- Handles large user bases
- Easy to extend with new features

## 🚀 Quick Start Checklist

- [ ] Set up authentication flow
- [ ] Implement wishlist API calls
- [ ] Create wishlist UI components
- [ ] Add error handling
- [ ] Test with real user data
- [ ] Deploy to production

## 📞 Support

If you encounter any issues:

1. Check the API response for error messages
2. Verify user_id exists in the database
3. Ensure product_id is valid
4. Check network connectivity
5. Review browser console for errors

---

**Your wishlist API is production-ready and follows best practices!** 🎉
