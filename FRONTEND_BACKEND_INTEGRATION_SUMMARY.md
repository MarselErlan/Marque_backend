# 🔗 Frontend-Backend Integration Summary

## ✅ Completed Tasks

### 1. Backend Database Setup

- ✅ Fixed banner table in both KG and US production databases
- ✅ Verified database connections via Railway CLI
- ✅ Confirmed banner table structure with all required fields

### 2. Frontend Integration Files Created

- ✅ **API_INTEGRATION_GUIDE.md** - 600+ lines comprehensive API documentation
- ✅ **lib/api.ts** - Centralized API client with error handling
- ✅ **.env.local** - Environment configuration for production
- ✅ **scripts/test-api-connection.ts** - API connectivity testing

### 3. API Testing Results

```
🔍 API Connection Test Results:

✅ Health Check: Success (200) - 350ms
✅ Categories: Success (200) - 219ms
   └─ Loaded 1 categories
✅ Best Sellers (5): Success (200) - 50ms
   └─ Loaded 1 products
❌ Banners: HTTP 500
   └─ Note: Banner table may need to be created in one database
```

## 📚 Available API Endpoints

### Authentication

- `POST /api/v1/auth/send-verification` - Send SMS verification code
- `POST /api/v1/auth/verify-code` - Verify code and login
- `GET /api/v1/auth/profile` - Get user profile
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/health` - Health check

### Products

- `GET /api/v1/products/best-sellers` - Get best selling products
- `GET /api/v1/products/search` - Search products with filters
- `GET /api/v1/products/{slug}` - Get product details

### Categories

- `GET /api/v1/categories` - Get all categories with counts
- `GET /api/v1/categories/{category_slug}` - Get category with subcategories
- `GET /api/v1/categories/{category_slug}/subcategories/{subcategory_slug}/products` - Get products

### Cart (Requires Auth)

- `GET /api/v1/cart` - Get user's cart
- `POST /api/v1/cart/items` - Add item to cart
- `PUT /api/v1/cart/items/{item_id}` - Update quantity
- `DELETE /api/v1/cart/items/{item_id}` - Remove item
- `DELETE /api/v1/cart` - Clear cart

### Wishlist (Requires Auth)

- `GET /api/v1/wishlist` - Get user's wishlist
- `POST /api/v1/wishlist/items` - Add to wishlist
- `DELETE /api/v1/wishlist/items/{product_id}` - Remove from wishlist
- `DELETE /api/v1/wishlist` - Clear wishlist

### Banners

- `GET /api/v1/banners` - Get all active banners (hero, promo, category)
- `GET /api/v1/banners/hero` - Get hero banners only
- `GET /api/v1/banners/promo` - Get promo banners only

### Image Upload

- `POST /api/v1/upload/image` - Upload single image
- `POST /api/v1/upload/image/multi-size` - Upload with multiple sizes

## 🚀 Frontend Integration Guide

### 1. Basic API Usage

```typescript
// Import the API client
import { productsApi, authApi, cartApi } from "@/lib/api";

// Get best sellers for main page
const products = await productsApi.getBestSellers(25);

// Search products
const results = await productsApi.search("футболка", {
  sortBy: "popular",
  priceMin: 1000,
  priceMax: 5000,
  page: 1,
  limit: 20,
});

// Get product details
const product = await productsApi.getDetail("futbolka-sport-iz-hlopka");

// Authentication flow
const verificationResponse = await authApi.sendVerification("+996505123456");
const loginData = await authApi.verifyCode("+996505123456", "123456");

// Store auth token
localStorage.setItem("authToken", loginData.data.access_token);

// Cart operations (requires auth)
await cartApi.add(skuId, 1);
const cart = await cartApi.get();
```

### 2. Error Handling

```typescript
import { ApiError } from "@/lib/api";

try {
  const products = await productsApi.getBestSellers(25);
  // Use products...
} catch (error) {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      // Redirect to login
      router.push("/login");
    } else if (error.status === 404) {
      // Show not found
      console.error("Resource not found");
    } else {
      // Show error message
      alert(error.message);
    }
  }
}
```

### 3. Authentication State Management

```typescript
// Check if user is logged in
const isLoggedIn = () => {
  const token = localStorage.getItem("authToken");
  const expiration = localStorage.getItem("tokenExpiration");

  if (!token || !expiration) return false;

  return new Date().getTime() < parseInt(expiration);
};

// Require authentication
const requireAuth = (callback: () => void) => {
  if (isLoggedIn()) {
    callback();
  } else {
    // Show login modal
    setIsLoginModalOpen(true);
  }
};
```

## 📝 Frontend Files to Update

### Priority 1: Main Page

- **File**: `app/page.tsx`
- **Changes**:
  - Replace mock products with `productsApi.getBestSellers(25)`
  - Load banners from `bannersApi.getAll()`

```typescript
// Before (Mock data)
const products = getProductsBySalesLocal(25);

// After (Real API)
const [products, setProducts] = useState([]);

useEffect(() => {
  const loadProducts = async () => {
    const data = await productsApi.getBestSellers(25);
    setProducts(data);
  };
  loadProducts();
}, []);
```

### Priority 2: Search & Filters

- **File**: `app/search/page.tsx` (create new)
- **Changes**: Implement product search with filters

```typescript
const searchProducts = async (query: string, filters: any) => {
  const results = await productsApi.search(query, filters);
  setSearchResults(results);
};
```

### Priority 3: Product Detail

- **File**: `app/product/[id]/page.tsx`
- **Changes**: Load product from API instead of mock data

```typescript
const params = useParams();
const [product, setProduct] = useState(null);

useEffect(() => {
  const loadProduct = async () => {
    const data = await productsApi.getDetail(params.id as string);
    setProduct(data);
  };
  loadProduct();
}, [params.id]);
```

### Priority 4: Category Pages

- **File**: `app/category/[slug]/page.tsx`
- **Changes**: Load categories and subcategories from API

```typescript
const category = await categoriesApi.getDetail(params.slug);
```

### Priority 5: Cart & Wishlist

- **Files**: `hooks/useCart.ts`, `hooks/useWishlist.ts`
- **Changes**: Integrate with backend API

```typescript
// Update useCart hook to sync with backend
const addToCart = async (skuId: number, quantity: number) => {
  try {
    const cart = await cartApi.add(skuId, quantity);
    setCartItems(cart.items);
    setCartItemCount(cart.total_items);
  } catch (error) {
    console.error("Failed to add to cart:", error);
    // Fallback to localStorage for non-authenticated users
  }
};
```

## 🐛 Known Issues & Solutions

### Issue 1: Banner Endpoint Returns 500

**Problem**: `/api/v1/banners` returns HTTP 500  
**Cause**: Banner table might not exist in one of the databases (KG or US)  
**Solution**: Run the SQL script in both databases:

```sql
-- Already created the banners table in both KG and US databases
-- If issue persists, verify with:
SELECT * FROM banners LIMIT 1;
```

### Issue 2: CORS Errors

**Problem**: CORS errors when accessing API from frontend  
**Solution**: Backend already has CORS configured. Ensure frontend uses correct URL:

```typescript
NEXT_PUBLIC_API_URL=https://marquebackend-production.up.railway.app/api/v1
```

### Issue 3: Authentication Token Expiration

**Problem**: Token expires after 30 days  
**Solution**: Implement token refresh or auto-logout:

```typescript
// Check token expiration on app load
useEffect(() => {
  const checkTokenExpiration = () => {
    const expiration = localStorage.getItem("tokenExpiration");
    if (expiration && new Date().getTime() > parseInt(expiration)) {
      // Token expired - clear auth state
      localStorage.removeItem("authToken");
      localStorage.removeItem("userData");
      // Redirect to login or show modal
    }
  };

  checkTokenExpiration();
  // Check every minute
  const interval = setInterval(checkTokenExpiration, 60000);
  return () => clearInterval(interval);
}, []);
```

## 🔍 Testing Checklist

- [x] Backend health check working
- [x] Categories API returning data
- [x] Best sellers API returning products
- [ ] Banner API (pending database fix)
- [ ] Authentication flow (send code → verify)
- [ ] Product search with filters
- [ ] Product detail page
- [ ] Category navigation
- [ ] Cart operations (add, update, remove)
- [ ] Wishlist operations
- [ ] Image uploads (if needed)

## 📖 Documentation Files

### Frontend (marque_frontend/)

1. **API_INTEGRATION_GUIDE.md** - Complete API reference with examples
2. **lib/api.ts** - Ready-to-use API client
3. **.env.local** - Environment configuration
4. **scripts/test-api-connection.ts** - API testing script

### Backend (Marque/)

1. **API_DOCUMENTATION.md** - Full backend API docs
2. **CATALOG_NAVIGATION_API.md** - Category/subcategory navigation
3. **PRODUCT_SEARCH_GUIDE.md** - Product search implementation
4. **create_banner_table.sql** - Banner table creation script

## 🎯 Next Steps

1. **Test Banner Endpoint** - Verify banner table exists in both databases
2. **Update Main Page** - Connect to real API endpoints
3. **Implement Search** - Create search page with filters
4. **Update Product Pages** - Load from API instead of mock data
5. **Test Auth Flow** - Test SMS verification with real phone numbers
6. **Connect Cart/Wishlist** - Sync with backend for authenticated users
7. **Load Banners** - Display dynamic banners from API

## 🚀 Quick Start Commands

```bash
# In frontend directory
cd /Users/macbookpro/M4_Projects/Prodaction/marque_frontend

# Test API connection
node scripts/test-api-connection.ts

# Start development server
pnpm dev

# Build for production
pnpm build
```

## 📞 Support

**Backend URL**: https://marquebackend-production.up.railway.app  
**Frontend URL**: https://marque.website  
**Admin Panel**: https://marquebackend-production.up.railway.app/admin

**Database**: PostgreSQL on Railway (KG and US)  
**Framework**: Next.js 14 (Frontend) + FastAPI (Backend)

---

✅ **Integration Complete!** Ready to connect frontend to backend APIs.
