# 👤 Complete Profile API Guide

**Status:** ✅ READY TO IMPLEMENT  
**Date:** October 23, 2025  
**Market Support:** KG & US

---

## 🎯 Overview

This guide provides complete API documentation for user profile management, including:

- User profile (name, phone, avatar)
- Delivery addresses
- Payment methods
- Orders history
- Notifications

---

## 📍 Base URL

```
Production: https://marquebackend-production.up.railway.app/api/v1
Local: http://localhost:8000/api/v1
```

---

## 🔐 Authentication

All profile endpoints require authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <access_token>
```

---

## 1️⃣ User Profile APIs

### 1.1 Get User Profile

```http
GET /api/v1/auth/profile
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "id": 19,
  "phone_number": "+13128059851",
  "full_name": "Анна Ахматова",
  "profile_image_url": "https://example.com/avatar.jpg",
  "is_active": true,
  "is_verified": true,
  "last_login": "2025-10-23T14:30:00Z",
  "market": "us",
  "language": "en",
  "country": "United States",
  "created_at": "2025-07-15T10:30:00Z"
}
```

---

### 1.2 Update User Profile

```http
PUT /api/v1/auth/profile
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "full_name": "Анна Ахматова",
  "profile_image_url": "https://example.com/new-avatar.jpg"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Profile updated successfully",
  "user": {
    "id": 19,
    "phone_number": "+13128059851",
    "full_name": "Анна Ахматова",
    "profile_image_url": "https://example.com/new-avatar.jpg",
    "market": "us"
  }
}
```

---

## 2️⃣ Delivery Address APIs

### 2.1 Get All Addresses

```http
GET /api/v1/profile/addresses
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "addresses": [
    {
      "id": 1,
      "title": "Адрес ул. Юнусалиева, 34",
      "full_address": "ул. Юнусалиева, 34, кв. 12, Бишкек",
      "street": "ул. Юнусалиева",
      "building": "34",
      "apartment": "12",
      "city": "Бишкек",
      "postal_code": "720000",
      "country": "Kyrgyzstan",
      "is_default": true,
      "created_at": "2025-07-15T10:30:00Z"
    },
    {
      "id": 2,
      "title": "Адрес ул. Уметалиева, 11a",
      "full_address": "ул. Уметалиева, 11a, Бишкек",
      "street": "ул. Уметалиева",
      "building": "11a",
      "apartment": null,
      "city": "Бишкек",
      "postal_code": "720000",
      "country": "Kyrgyzstan",
      "is_default": false,
      "created_at": "2025-08-10T14:20:00Z"
    }
  ],
  "total": 2
}
```

---

### 2.2 Create New Address

```http
POST /api/v1/profile/addresses
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "Домашний адрес",
  "full_address": "ул. Юнусалиева, 34, кв. 12, Бишкек",
  "street": "ул. Юнусалиева",
  "building": "34",
  "apartment": "12",
  "city": "Бишкек",
  "postal_code": "720000",
  "country": "Kyrgyzstan",
  "is_default": false
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "message": "Address created successfully",
  "address": {
    "id": 3,
    "title": "Домашний адрес",
    "full_address": "ул. Юнусалиева, 34, кв. 12, Бишкек",
    "is_default": false,
    "created_at": "2025-10-23T14:30:00Z"
  }
}
```

---

### 2.3 Update Address

```http
PUT /api/v1/profile/addresses/{address_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:** (same as create, all fields optional)

```json
{
  "title": "Рабочий адрес",
  "is_default": true
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Address updated successfully",
  "address": {
    "id": 3,
    "title": "Рабочий адрес",
    "is_default": true
  }
}
```

---

### 2.4 Delete Address

```http
DELETE /api/v1/profile/addresses/{address_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Address deleted successfully"
}
```

---

## 3️⃣ Payment Method APIs

### 3.1 Get All Payment Methods

```http
GET /api/v1/profile/payment-methods
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "payment_methods": [
    {
      "id": 1,
      "payment_type": "card",
      "card_type": "visa",
      "card_number_masked": "2352",
      "card_holder_name": "ANNA AKHMATOVA",
      "is_default": true,
      "created_at": "2025-07-15T10:30:00Z"
    },
    {
      "id": 2,
      "payment_type": "card",
      "card_type": "mastercard",
      "card_number_masked": "5256",
      "card_holder_name": "ANNA AKHMATOVA",
      "is_default": false,
      "created_at": "2025-08-10T14:20:00Z"
    }
  ],
  "total": 2
}
```

---

### 3.2 Create New Payment Method

```http
POST /api/v1/profile/payment-methods
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "card_number": "4111111111111111",
  "card_holder_name": "ANNA AKHMATOVA",
  "expiry_month": "12",
  "expiry_year": "2028",
  "is_default": false
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "message": "Payment method added successfully",
  "payment_method": {
    "id": 3,
    "card_type": "visa",
    "card_number_masked": "1111",
    "is_default": false,
    "created_at": "2025-10-23T14:30:00Z"
  }
}
```

---

### 3.3 Update Payment Method

```http
PUT /api/v1/profile/payment-methods/{payment_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "is_default": true
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Payment method updated successfully"
}
```

---

### 3.4 Delete Payment Method

```http
DELETE /api/v1/profile/payment-methods/{payment_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Payment method deleted successfully"
}
```

---

## 4️⃣ Orders APIs

### 4.1 Get All Orders

```http
GET /api/v1/profile/orders
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `status` (optional): Filter by status (pending, confirmed, shipped, delivered, cancelled)
- `limit` (optional): Number of orders per page (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**

```json
{
  "success": true,
  "orders": [
    {
      "id": 23529,
      "order_number": "#23529",
      "status": "delivered",
      "total_amount": 5233.0,
      "currency": "KGS",
      "order_date": "2025-07-15T10:30:00Z",
      "delivery_date": "2025-07-21T14:20:00Z",
      "delivery_address": "ул. Юнусалиева, 34, Бишкек",
      "items_count": 3,
      "items": [
        {
          "product_name": "Чёрная футболка",
          "quantity": 1,
          "price": 1500.0,
          "image_url": "https://example.com/product.jpg"
        }
      ]
    }
  ],
  "total": 1,
  "has_more": false
}
```

---

### 4.2 Get Order Details

```http
GET /api/v1/profile/orders/{order_id}
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "order": {
    "id": 23529,
    "order_number": "#23529",
    "status": "delivered",
    "customer_name": "Анна Ахматова",
    "customer_phone": "+996505325311",
    "delivery_address": "ул. Юнусалиева, 34, кв. 12, Бишкек",
    "subtotal": 5233.0,
    "shipping_cost": 0.0,
    "total_amount": 5233.0,
    "currency": "KGS",
    "order_date": "2025-07-15T10:30:00Z",
    "confirmed_date": "2025-07-15T11:00:00Z",
    "shipped_date": "2025-07-18T09:00:00Z",
    "delivered_date": "2025-07-21T14:20:00Z",
    "items": [
      {
        "product_name": "Чёрная футболка",
        "quantity": 1,
        "price": 1500.0,
        "subtotal": 1500.0,
        "image_url": "https://example.com/product.jpg"
      },
      {
        "product_name": "Джинсы синие",
        "quantity": 2,
        "price": 1866.5,
        "subtotal": 3733.0,
        "image_url": "https://example.com/jeans.jpg"
      }
    ]
  }
}
```

---

### 4.3 Cancel Order

```http
POST /api/v1/profile/orders/{order_id}/cancel
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Order cancelled successfully",
  "order_id": 23529,
  "status": "cancelled"
}
```

---

## 5️⃣ Notifications APIs

### 5.1 Get All Notifications

```http
GET /api/v1/profile/notifications
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Query Parameters:**

- `unread_only` (optional): Get only unread notifications (default: false)
- `limit` (optional): Number of notifications per page (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response (200 OK):**

```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": "order",
      "title": "Заказ №123 подтверждён",
      "message": "Ваш заказ был подтверждён и будет доставлен 21.07.2025",
      "is_read": false,
      "order_id": 123,
      "created_at": "2025-07-15T14:32:00Z"
    },
    {
      "id": 2,
      "type": "promotion",
      "title": "Скидка 30% на летнюю коллекцию",
      "message": "Успейте купить со скидкой до конца недели!",
      "is_read": true,
      "created_at": "2025-07-10T10:00:00Z"
    }
  ],
  "total": 2,
  "unread_count": 1
}
```

---

### 5.2 Mark Notification as Read

```http
PUT /api/v1/profile/notifications/{notification_id}/read
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Notification marked as read"
}
```

---

### 5.3 Mark All Notifications as Read

```http
PUT /api/v1/profile/notifications/read-all
```

**Headers:**

```
Authorization: Bearer <access_token>
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "All notifications marked as read",
  "count": 5
}
```

---

## 🔧 Error Responses

All endpoints follow the same error format:

```json
{
  "success": false,
  "error": "error_code",
  "message": "Human-readable error message"
}
```

**Common HTTP Status Codes:**

- `400` - Bad Request (invalid input)
- `401` - Unauthorized (missing or invalid token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `422` - Validation Error
- `500` - Internal Server Error

---

## 🗂️ Database Models

### User Model

```python
- id: Integer (Primary Key)
- phone_number: String(20) (Unique, Indexed)
- full_name: String(255)
- profile_image_url: String(500)
- is_active: Boolean
- is_verified: Boolean
- market: String(10) (kg/us)
- language: String(10)
- country: String(100)
- created_at: DateTime
- updated_at: DateTime
```

### UserAddress Model

```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- title: String(100)
- full_address: Text
- street, building, apartment, city, postal_code, country
- is_default: Boolean
- is_active: Boolean
- created_at, updated_at: DateTime
```

### UserPaymentMethod Model

```python
- id: Integer (Primary Key)
- user_id: Integer (Foreign Key)
- payment_type: String(20) (card/wallet/cash)
- card_type: String(20) (visa/mastercard/mir)
- card_number_masked: String(20)
- card_holder_name: String(100)
- is_default: Boolean
- is_active: Boolean
- created_at, updated_at: DateTime
```

### Order Model

```python
- id: Integer (Primary Key)
- order_number: String(50) (Unique)
- user_id: Integer (Foreign Key)
- status: Enum (pending/confirmed/shipped/delivered/cancelled)
- customer_name, customer_phone, delivery_address
- subtotal, shipping_cost, total_amount, currency
- order_date, delivered_date, cancelled_date
- created_at, updated_at: DateTime
```

---

## 🎯 Frontend Integration Example

```javascript
const API_BASE = "https://marquebackend-production.up.railway.app/api/v1";

// Get user profile
async function getProfile() {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE}/auth/profile`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return await response.json();
}

// Get user addresses
async function getAddresses() {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE}/profile/addresses`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return await response.json();
}

// Get user orders
async function getOrders() {
  const token = localStorage.getItem("access_token");
  const response = await fetch(`${API_BASE}/profile/orders`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return await response.json();
}
```

---

## ✅ Next Steps

1. ✅ Create profile router with all endpoints
2. ✅ Enable database relationships in models
3. ✅ Test all endpoints with Postman
4. ✅ Update frontend to use new APIs
5. ✅ Deploy to production

---

**Created:** October 23, 2025  
**Author:** Marque Development Team
