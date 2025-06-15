# Entegra API Documentation - GET Endpoints Only

## Overview
This documentation covers the GET endpoints available in the Entegra API for data extraction purposes. The base URL for all endpoints is:

```
https://apiv2.entegrabilisim.com
```

## Authentication

### Get Token
**Endpoint:** `POST /api/user/token/obtain/`  
**Purpose:** Obtain JWT token for authentication

**Request Body:**
```json
{
    "email": "{{ApiUsername}}",
    "password": "{{ApiPassword}}"
}
```

**Response:**
```json
{
    "access": "jwt_token_here",
    "refresh": "refresh_token_here"
}
```

**Usage:** Include the token in the Authorization header as:
```
Authorization: JWT {access_token}
```

---

## Data Endpoints

### 1. Products (Ürünler)

#### Get Products
**Endpoint:** `GET /product/page={page_number}/`

**Description:** Retrieve paginated list of products

**Parameters:**
- `page` (path parameter): Page number for pagination
- `id` (query parameter, optional): Specific product ID
- `api_sync` (query parameter, optional): Synchronization flag (0 or 1)

**Example URLs:**
```
GET /product/page=1/
GET /product/page=1/?id=1223
GET /product/page=1/?api_sync=0
```

**Response Structure:**
```json
{
    "productList": [
        {
            "id": "1223",
            "productCode": "3007975",
            "status": "1",
            "description": "Product description",
            "barcode": "8690570518436",
            "date_change": "2023-01-01 10:00:00"
        }
    ],
    "totalProduct": 150
}
```

#### Get Product V2
**Endpoint:** `GET /product/v2/`

**Description:** Alternative product endpoint with enhanced functionality

---

### 2. Categories (Kategoriler)

#### Get Categories
**Endpoint:** `GET /category/page={page_number}/`

**Description:** Retrieve paginated list of product categories

**Example URLs:**
```
GET /category/page=1/
```

**Response Structure:**
```json
{
    "categories": [
        {
            "id": "1",
            "name": "Default",
            "description": "",
            "status": "1",
            "sort_order": "0",
            "parent_id": "0"
        }
    ]
}
```

---

### 3. Orders (Siparişler)

#### Get Orders
**Endpoint:** `GET /order/page={page_number}/`

**Description:** Retrieve paginated list of orders

**Parameters:**
- `page` (path parameter): Page number for pagination
- `id` (query parameter, optional): Specific order ID
- `supplier` (query parameter, optional): Filter by supplier
- `start_date` (query parameter, optional): Start date filter (YYYY-MM-DD)
- `end_date` (query parameter, optional): End date filter (YYYY-MM-DD)

**Example URLs:**
```
GET /order/page=1/
GET /order/page=1/?id=26
GET /order/page=1/?supplier=n11
GET /order/page=1/?start_date=2022-12-04&end_date=2022-12-05
```

**Response Structure:**
```json
{
    "orders": [
        {
            "id": "26",
            "order_number": "12345",
            "supplier": "n11",
            "status": "completed",
            "order_date": "2023-01-01 10:00:00"
        }
    ],
    "totalOrder": 75
}
```

---

### 4. Stores (Mağazalar)

#### Get Stores
**Endpoint:** `GET /store/getStores`

**Description:** Retrieve list of stores/locations

**Example URLs:**
```
GET /store/getStores
```

**Response Structure:**
```json
{
    "stores": [
        {
            "id": "1",
            "name": "Main Store",
            "status": "1",
            "location": "Istanbul"
        }
    ]
}
```

---

### 5. Brands (Markalar)

#### Get Brands
**Endpoint:** `GET /product/brand/page={page_number}/`

**Description:** Retrieve paginated list of brands

**Example URLs:**
```
GET /product/brand/page=1/
```

**Response Structure:**
```json
{
    "brands": [
        {
            "id": "1",
            "name": "Brand Name",
            "status": "1"
        }
    ]
}
```

---

### 6. Prices (Fiyatlar)

#### Get Prices
**Endpoint:** `GET /price/getPrices`

**Description:** Retrieve list of product prices

**Example URLs:**
```
GET /price/getPrices
```

**Response Structure:**
```json
{
    "prices": [
        {
            "id": "1",
            "product_id": "1223",
            "price_value": "100.00",
            "store_id": "1",
            "date_modified": "2023-01-01 10:00:00"
        }
    ]
}
```

---

### 7. Customers (Müşteriler)

#### Get Customers
**Endpoint:** `GET /customer/page={page_number}/`

**Description:** Retrieve paginated list of customers

**Parameters:**
- `page` (path parameter): Page number for pagination
- `orderId` (query parameter, optional): Filter by specific order ID

**Example URLs:**
```
GET /customer/page=1/
GET /customer/page=1/?orderId=500
```

**Response Structure:**
```json
{
    "customers": [
        {
            "id": "1",
            "name": "Customer Name",
            "email": "customer@example.com",
            "date_modified": "2023-01-01 10:00:00"
        }
    ]
}
```

---

### 8. Marketplace Quantity Settings

#### Get Marketplace Quantity Settings
**Endpoint:** `GET /store/getMarketplaceQuantitySettings`

**Description:** Retrieve marketplace quantity configuration settings

**Example URLs:**
```
GET /store/getMarketplaceQuantitySettings
```

---

### 9. Marketplace Price Settings

#### Get Marketplace Price Settings
**Endpoint:** `GET /price/getMarketplacePriceSettings`

**Description:** Retrieve marketplace price configuration settings

**Example URLs:**
```
GET /price/getMarketplacePriceSettings
```

---

## General Notes

### Pagination
- **Paginated endpoints** use path-based pagination: `/endpoint/page=1/`
  - Products: `/product/page=1/`
  - Categories: `/category/page=1/`
  - Orders: `/order/page=1/`
  - Brands: `/product/brand/page=1/`
  - Customers: `/customer/page=1/`
- **Non-paginated endpoints** return all data in single request:
  - Stores: `/store/getStores`
  - Prices: `/price/getPrices`
  - Marketplace Quantity Settings: `/store/getMarketplaceQuantitySettings`
  - Marketplace Price Settings: `/price/getMarketplacePriceSettings`
- Page numbering starts from 1 for paginated endpoints
- Paginated responses include total count for planning pagination

### Authentication
- All endpoints require JWT authentication
- Include `Authorization: JWT {token}` header in all requests
- Tokens have expiration time, use refresh token when needed

### Response Format
- All responses are in JSON format
- Most endpoints return arrays of data with total count
- Consistent error handling across all endpoints

### Rate Limiting
- API may have rate limiting in place
- Implement appropriate delays between requests

### SSL/TLS
- API uses HTTPS
- SSL certificate verification may need to be handled based on environment

---

## Implementation Notes for Meltano Tap

1. **Primary Keys:** All entities use `"id"` as the primary key
2. **Incremental Sync:** Products and Orders support date-based incremental sync
3. **Pagination:** Implement page-based pagination starting from page=1
4. **Error Handling:** Implement robust error handling for authentication and rate limiting
5. **Schema Evolution:** Monitor for schema changes in API responses 