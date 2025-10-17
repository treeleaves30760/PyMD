# PyMD Backend API Specifications

**Version:** 1.0.0
**Base URL:** `/api/v1`
**Date:** 2025-10-17

## Table of Contents

1. [API Design Principles](#api-design-principles)
2. [Authentication & Authorization](#authentication--authorization)
3. [Common Response Formats](#common-response-formats)
4. [Authentication Endpoints](#authentication-endpoints)
5. [User Management APIs](#user-management-apis)
6. [Document Management APIs](#document-management-apis)
7. [PyMD Rendering APIs](#pymd-rendering-apis)
8. [System APIs](#system-apis)
9. [WebSocket APIs](#websocket-apis)
10. [Error Codes Reference](#error-codes-reference)
11. [Rate Limiting](#rate-limiting)

---

## API Design Principles

### RESTful Design
- Use standard HTTP methods (GET, POST, PUT, PATCH, DELETE)
- Resource-based URLs
- Stateless requests
- Use HTTP status codes appropriately

### JSON Format
- All requests and responses use JSON
- Use camelCase for JSON keys
- Include proper Content-Type headers

### Versioning
- API version in URL path: `/api/v1`
- Major version changes require new path
- Minor changes maintain backward compatibility

### Pagination
- Standard pagination for list endpoints
- Query parameters: `page` (default: 1), `limit` (default: 20, max: 100)
- Response includes metadata: `page`, `limit`, `total`, `pages`

---

## Authentication & Authorization

### Authentication Flow
1. User authenticates via Auth0
2. Auth0 redirects to callback with authorization code
3. Backend exchanges code for tokens
4. Backend issues session cookie or returns JWT
5. Subsequent requests include authentication token

### Authorization Header
```
Authorization: Bearer <access_token>
```

### Session Cookie
```
Cookie: pymd_session=<session_token>
```

### Permission Levels
- **Public**: No authentication required
- **Authenticated**: Valid user token required
- **Owner**: User must own the resource
- **Admin**: Admin role required

---

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### List Response with Pagination
```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... }
  }
}
```

---

## Authentication Endpoints

### 1. Auth0 Callback

**Endpoint:** `POST /auth/callback`
**Auth Required:** No
**Description:** Handles Auth0 callback and creates user session

**Request Body:**
```json
{
  "code": "string",           // Authorization code from Auth0
  "state": "string"            // State parameter for CSRF protection
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "accessToken": "string",   // JWT access token
    "refreshToken": "string",  // Refresh token
    "expiresIn": 3600,         // Seconds until expiration
    "tokenType": "Bearer",
    "user": {
      "id": "string",
      "email": "string",
      "name": "string",
      "avatar": "string|null",
      "createdAt": "timestamp"
    }
  }
}
```

**Errors:**
- `400`: Invalid authorization code
- `401`: Invalid state parameter
- `500`: Auth0 communication error

---

### 2. Refresh Token

**Endpoint:** `POST /auth/refresh`
**Auth Required:** Yes (Refresh Token)
**Description:** Refreshes access token using refresh token

**Request Body:**
```json
{
  "refreshToken": "string"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "accessToken": "string",
    "expiresIn": 3600
  }
}
```

**Errors:**
- `401`: Invalid or expired refresh token

---

### 3. Logout

**Endpoint:** `POST /auth/logout`
**Auth Required:** Yes
**Description:** Invalidates user session and tokens

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

### 4. Get Current User

**Endpoint:** `GET /auth/me`
**Auth Required:** Yes
**Description:** Returns current authenticated user information

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "email": "string",
    "name": "string",
    "avatar": "string|null",
    "role": "user|admin",
    "settings": {
      "theme": "light|dark",
      "language": "en|zh",
      "editorSettings": { ... }
    },
    "createdAt": "timestamp",
    "lastLoginAt": "timestamp"
  }
}
```

**Errors:**
- `401`: Unauthorized

---

## User Management APIs

### 1. Get User Profile

**Endpoint:** `GET /users/:userId`
**Auth Required:** Yes
**Description:** Get user profile (own or public profiles)

**Path Parameters:**
- `userId`: User ID or "me" for current user

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "avatar": "string|null",
    "bio": "string|null",
    "createdAt": "timestamp",
    "documentCount": "integer"
  }
}
```

**Errors:**
- `404`: User not found

---

### 2. Update User Profile

**Endpoint:** `PATCH /users/:userId`
**Auth Required:** Yes (Owner)
**Description:** Update user profile information

**Request Body:**
```json
{
  "name": "string?",
  "bio": "string?",
  "avatar": "string?"        // URL or base64
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "avatar": "string|null",
    "bio": "string|null",
    "updatedAt": "timestamp"
  }
}
```

**Errors:**
- `400`: Invalid input
- `403`: Forbidden (not owner)

---

### 3. Get User Settings

**Endpoint:** `GET /users/:userId/settings`
**Auth Required:** Yes (Owner)
**Description:** Get user settings

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "theme": "light|dark",
    "language": "en|zh",
    "editorSettings": {
      "fontSize": "integer",
      "tabSize": "integer",
      "wordWrap": "boolean",
      "lineNumbers": "boolean",
      "syntaxHighlighting": "boolean"
    },
    "renderSettings": {
      "defaultFormat": "html|markdown",
      "autoSave": "boolean",
      "autoSaveInterval": "integer"
    }
  }
}
```

---

### 4. Update User Settings

**Endpoint:** `PATCH /users/:userId/settings`
**Auth Required:** Yes (Owner)
**Description:** Update user settings

**Request Body:**
```json
{
  "theme": "light|dark?",
  "language": "en|zh?",
  "editorSettings": { ... },
  "renderSettings": { ... }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "theme": "light|dark",
    "language": "en|zh",
    "editorSettings": { ... },
    "renderSettings": { ... },
    "updatedAt": "timestamp"
  }
}
```

---

## Document Management APIs

### 1. List Documents

**Endpoint:** `GET /documents`
**Auth Required:** Yes
**Description:** List user's documents with filtering and pagination

**Query Parameters:**
- `page`: integer (default: 1)
- `limit`: integer (default: 20, max: 100)
- `sort`: "created|updated|title" (default: "updated")
- `order`: "asc|desc" (default: "desc")
- `search`: string (search in title and content)
- `tags`: string[] (comma-separated)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "string",
        "title": "string",
        "content": "string",        // First 200 chars
        "tags": ["string"],
        "createdAt": "timestamp",
        "updatedAt": "timestamp",
        "size": "integer",          // Bytes
        "renderFormat": "html|markdown"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "pages": 8
    }
  }
}
```

---

### 2. Create Document

**Endpoint:** `POST /documents`
**Auth Required:** Yes
**Description:** Create a new PyMD document

**Request Body:**
```json
{
  "title": "string",           // Required, 1-200 chars
  "content": "string",         // PyMD content
  "tags": ["string"],          // Optional
  "renderFormat": "html|markdown"  // Optional, default: "html"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "string",
    "content": "string",
    "tags": ["string"],
    "renderFormat": "html|markdown",
    "ownerId": "string",
    "createdAt": "timestamp",
    "updatedAt": "timestamp"
  }
}
```

**Errors:**
- `400`: Invalid input (missing title, invalid format)
- `413`: Content too large (> 10MB)

---

### 3. Get Document

**Endpoint:** `GET /documents/:documentId`
**Auth Required:** Yes
**Description:** Get a specific document

**Path Parameters:**
- `documentId`: Document ID

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "string",
    "content": "string",
    "tags": ["string"],
    "renderFormat": "html|markdown",
    "ownerId": "string",
    "ownerName": "string",
    "createdAt": "timestamp",
    "updatedAt": "timestamp",
    "size": "integer"
  }
}
```

**Errors:**
- `404`: Document not found
- `403`: Forbidden (not owner, no permission)

---

### 4. Update Document

**Endpoint:** `PATCH /documents/:documentId`
**Auth Required:** Yes (Owner)
**Description:** Update document content or metadata

**Request Body:**
```json
{
  "title": "string?",
  "content": "string?",
  "tags": ["string"]?,
  "renderFormat": "html|markdown?"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "title": "string",
    "content": "string",
    "tags": ["string"],
    "renderFormat": "html|markdown",
    "updatedAt": "timestamp"
  }
}
```

**Errors:**
- `400`: Invalid input
- `403`: Forbidden (not owner)
- `404`: Document not found
- `413`: Content too large

---

### 5. Delete Document

**Endpoint:** `DELETE /documents/:documentId`
**Auth Required:** Yes (Owner)
**Description:** Delete a document

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

**Errors:**
- `403`: Forbidden (not owner)
- `404`: Document not found

---

### 6. Duplicate Document

**Endpoint:** `POST /documents/:documentId/duplicate`
**Auth Required:** Yes
**Description:** Create a copy of a document

**Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "string",            // New document ID
    "title": "string",         // "Copy of {original title}"
    "content": "string",
    "tags": ["string"],
    "createdAt": "timestamp"
  }
}
```

---

### 7. Search Documents

**Endpoint:** `GET /documents/search`
**Auth Required:** Yes
**Description:** Full-text search across user's documents

**Query Parameters:**
- `q`: string (required, search query)
- `page`: integer (default: 1)
- `limit`: integer (default: 20)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "string",
        "title": "string",
        "content": "string",    // Excerpt with highlight
        "relevance": "float",   // 0-1 score
        "createdAt": "timestamp",
        "updatedAt": "timestamp"
      }
    ],
    "pagination": { ... }
  }
}
```

---

## PyMD Rendering APIs

### 1. Render Document

**Endpoint:** `POST /render`
**Auth Required:** Yes
**Description:** Render PyMD content to HTML or Markdown

**Request Body:**
```json
{
  "content": "string",         // PyMD content
  "format": "html|markdown",   // Output format
  "options": {
    "theme": "light|dark?",
    "includeStyles": "boolean?",
    "includeToc": "boolean?"
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "rendered": "string",      // Rendered output
    "format": "html|markdown",
    "warnings": ["string"],    // Any warnings during rendering
    "executionTime": "float"   // Milliseconds
  }
}
```

**Errors:**
- `400`: Invalid PyMD syntax
- `413`: Content too large
- `422`: Rendering failed

---

### 2. Render Document by ID

**Endpoint:** `GET /documents/:documentId/render`
**Auth Required:** Yes
**Description:** Render a stored document

**Query Parameters:**
- `format`: "html|markdown" (default: document's renderFormat)

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "documentId": "string",
    "rendered": "string",
    "format": "html|markdown",
    "cachedAt": "timestamp|null"
  }
}
```

**Errors:**
- `404`: Document not found
- `403`: Forbidden

---

### 3. Preview Render (Real-time)

**Endpoint:** `POST /render/preview`
**Auth Required:** Yes
**Description:** Quick preview rendering with caching
**Rate Limit:** 10 requests per minute

**Request Body:**
```json
{
  "content": "string",
  "format": "html|markdown"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "rendered": "string",
    "cached": "boolean"
  }
}
```

---

### 4. Validate PyMD Syntax

**Endpoint:** `POST /render/validate`
**Auth Required:** Yes
**Description:** Validate PyMD syntax without rendering

**Request Body:**
```json
{
  "content": "string"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "valid": "boolean",
    "errors": [
      {
        "line": "integer",
        "column": "integer",
        "message": "string",
        "severity": "error|warning"
      }
    ]
  }
}
```

---

### 5. Export Document

**Endpoint:** `GET /documents/:documentId/export`
**Auth Required:** Yes
**Description:** Export document in various formats

**Query Parameters:**
- `format`: "html|markdown|pdf|json" (default: "html")

**Response (200 OK):**
- Content-Type based on format
- Content-Disposition header for download

**Errors:**
- `404`: Document not found
- `403`: Forbidden
- `400`: Unsupported format

---

## System APIs

### 1. Health Check

**Endpoint:** `GET /health`
**Auth Required:** No
**Description:** System health check

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "1.0.0",
    "timestamp": "timestamp",
    "services": {
      "database": "healthy|degraded|down",
      "cache": "healthy|degraded|down",
      "auth": "healthy|degraded|down"
    }
  }
}
```

---

### 2. Get System Info

**Endpoint:** `GET /system/info`
**Auth Required:** Yes (Admin)
**Description:** System information and statistics

**Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "version": "string",
    "uptime": "integer",       // Seconds
    "users": {
      "total": "integer",
      "active": "integer"      // Last 24h
    },
    "documents": {
      "total": "integer",
      "size": "integer"        // Total bytes
    },
    "system": {
      "cpu": "float",          // Percent
      "memory": "float",       // Percent
      "disk": "float"          // Percent
    }
  }
}
```

---

## WebSocket APIs

### Connection

**Endpoint:** `WS /ws`
**Auth Required:** Yes (via query param or header)
**Description:** WebSocket connection for real-time features

**Connection URL:**
```
ws://localhost:8000/ws?token=<access_token>
```

### Message Format

**Client to Server:**
```json
{
  "type": "subscribe|unsubscribe|ping",
  "data": { ... }
}
```

**Server to Client:**
```json
{
  "type": "document.update|render.complete|system.notification",
  "data": { ... },
  "timestamp": "timestamp"
}
```

### Event Types

#### 1. Document Update
```json
{
  "type": "document.update",
  "data": {
    "documentId": "string",
    "changes": {
      "title": "string?",
      "content": "string?",
      "updatedAt": "timestamp"
    }
  }
}
```

#### 2. Render Complete
```json
{
  "type": "render.complete",
  "data": {
    "jobId": "string",
    "status": "success|error",
    "rendered": "string",
    "error": "string?"
  }
}
```

---

## Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTH_REQUIRED` | 401 | Authentication required |
| `AUTH_INVALID` | 401 | Invalid or expired token |
| `AUTH_FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `DUPLICATE_ERROR` | 409 | Resource already exists |
| `RATE_LIMIT` | 429 | Rate limit exceeded |
| `SERVER_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |
| `CONTENT_TOO_LARGE` | 413 | Content exceeds size limit |
| `RENDER_ERROR` | 422 | PyMD rendering failed |
| `DATABASE_ERROR` | 500 | Database operation failed |
| `CACHE_ERROR` | 500 | Cache operation failed |

---

## Rate Limiting

### Default Limits

| Endpoint Pattern | Limit | Window |
|------------------|-------|--------|
| `/auth/*` | 10 requests | 1 minute |
| `/render/preview` | 10 requests | 1 minute |
| `/render` | 30 requests | 1 minute |
| `/documents` (POST) | 30 requests | 1 hour |
| `/documents` (GET) | 100 requests | 1 minute |
| General API | 1000 requests | 1 hour |

### Rate Limit Headers

Response includes:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634567890
```

### Rate Limit Response (429)
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "retryAfter": 45
  }
}
```

---

## API Versioning Strategy

### Version Management
- **Major version** (v1, v2): Breaking changes, new URL path
- **Minor updates**: Backward compatible, same path
- **Deprecation**: 6-month notice before removal

### Version Headers
```
X-API-Version: 1.0.0
X-Deprecated: false
```

### Sunset Header (for deprecated versions)
```
Sunset: Sat, 31 Dec 2025 23:59:59 GMT
```

---

## Implementation Notes

### Security Considerations
1. All endpoints use HTTPS in production
2. CORS configured for frontend domain only
3. Request size limits enforced
4. SQL injection protection via parameterized queries
5. XSS protection via content sanitization
6. CSRF tokens for state-changing operations

### Performance Optimization
1. Response caching for GET requests
2. Database query optimization
3. Connection pooling
4. Gzip compression for responses
5. CDN for static assets

### Monitoring
1. Request/response logging
2. Error tracking
3. Performance metrics
4. Rate limit monitoring
5. Health check endpoints

---

**End of API Specifications**
