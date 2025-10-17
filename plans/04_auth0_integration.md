# PyMD Auth0 Integration Plan

**Version:** 1.0.0
**Date:** 2025-10-17

## Table of Contents

1. [Auth0 Overview](#auth0-overview)
2. [Auth0 Setup Requirements](#auth0-setup-requirements)
3. [Authentication Flow](#authentication-flow)
4. [Frontend Integration](#frontend-integration)
5. [Backend Integration](#backend-integration)
6. [Security Considerations](#security-considerations)
7. [User Profile Management](#user-profile-management)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)
10. [Monitoring and Logging](#monitoring-and-logging)

---

## Auth0 Overview

### Why Auth0?

**Benefits:**
- **Enterprise-Grade Security**: OAuth2/OIDC standards compliance
- **Reduced Development Time**: Pre-built authentication flows
- **Multi-Factor Authentication**: Built-in MFA support
- **Social Login**: Easy integration with Google, GitHub, etc.
- **User Management**: Dashboard for user administration
- **Security Features**: Breach detection, bot detection, anomaly detection
- **Scalability**: Handles millions of users
- **Compliance**: SOC 2, GDPR, HIPAA compliant

### Architecture Overview

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   Frontend   │────────>│    Auth0     │────────>│   Backend    │
│  (Next.js)   │<────────│  (IdP/AuthN) │<────────│  (FastAPI)   │
└──────────────┘         └──────────────┘         └──────────────┘
      │                                                   │
      │                                                   │
      └───────────────────────────────────────────────────┘
                    Secured API Calls
```

---

## Auth0 Setup Requirements

### 1. Auth0 Account Setup

**Steps:**
1. Create Auth0 account at https://auth0.com
2. Create new tenant (e.g., `pymd-dev`, `pymd-prod`)
3. Select tenant region (closest to users)

### 2. Application Configuration

Create two Auth0 applications:

#### A. Single-Page Application (Frontend)

**Application Type:** Single-Page Application (SPA)

**Configuration:**

| Setting | Development | Production |
|---------|------------|-----------|
| **Name** | PyMD Web App (Dev) | PyMD Web App |
| **Allowed Callback URLs** | http://localhost:3000/auth/callback | https://app.pymd.io/auth/callback |
| **Allowed Logout URLs** | http://localhost:3000 | https://app.pymd.io |
| **Allowed Web Origins** | http://localhost:3000 | https://app.pymd.io |
| **Allowed Origins (CORS)** | http://localhost:3000 | https://app.pymd.io |
| **Token Endpoint Authentication Method** | None | None |
| **Grants** | Authorization Code + PKCE, Refresh Token | Authorization Code + PKCE, Refresh Token |

**Advanced Settings:**
- **Grant Types**:
  - ✅ Authorization Code
  - ✅ Refresh Token
  - ❌ Implicit (Deprecated)
  - ❌ Password (Not recommended for web apps)
- **OIDC Conformant**: ✅ Enabled
- **Refresh Token Rotation**: ✅ Enabled
- **Refresh Token Expiration**: 30 days
- **Absolute Lifetime**: 90 days

#### B. Machine to Machine Application (Backend)

**Application Type:** Machine to Machine (M2M)

**Purpose:** Backend server verification of tokens

**Configuration:**
- **Name**: PyMD Backend API
- **Authorized APIs**: Auth0 Management API
- **Scopes**: `read:users`, `update:users`, `read:user_idp_tokens`

### 3. API Configuration

**Create Auth0 API:**

| Setting | Value |
|---------|-------|
| **Name** | PyMD API |
| **Identifier** | https://api.pymd.io |
| **Signing Algorithm** | RS256 |
| **Allow Skipping User Consent** | ✅ Enabled |
| **Token Expiration** | 3600 seconds (1 hour) |
| **Allow Offline Access** | ✅ Enabled (for refresh tokens) |

**Permissions/Scopes:**
- `read:documents` - Read user documents
- `write:documents` - Create/update documents
- `delete:documents` - Delete documents
- `read:profile` - Read user profile
- `write:profile` - Update user profile

### 4. Connection Settings

**Enable Authentication Methods:**

- ✅ **Username-Password-Authentication** (Database)
  - Require email verification: ✅
  - Password strength: Fair
  - Password history: 5
  - Password dictionary: Enabled

- ✅ **Google OAuth2** (Social)
  - Scopes: `email`, `profile`

- ✅ **GitHub** (Social - optional)
  - Scopes: `user:email`

**Disable:**
- ❌ Passwordless (for MVP)
- ❌ Enterprise connections (for MVP)

### 5. Rules and Actions

**Create Auth0 Action (Login Flow):**

**Purpose:** Sync user data to local database on login

```javascript
/**
 * Handler that will be called during the execution of a PostLogin flow.
 */
exports.onExecutePostLogin = async (event, api) => {
  const axios = require('axios');

  // Sync user to PyMD backend
  try {
    await axios.post('https://api.pymd.io/internal/auth/sync-user', {
      auth0Id: event.user.user_id,
      email: event.user.email,
      name: event.user.name,
      picture: event.user.picture,
      emailVerified: event.user.email_verified
    }, {
      headers: {
        'Authorization': `Bearer ${event.secrets.BACKEND_INTERNAL_TOKEN}`
      }
    });
  } catch (error) {
    console.error('Failed to sync user to backend:', error);
    // Don't block login on sync failure
  }

  // Add custom claims to token
  api.idToken.setCustomClaim('https://pymd.io/roles', event.user.app_metadata?.roles || ['user']);
  api.accessToken.setCustomClaim('https://pymd.io/roles', event.user.app_metadata?.roles || ['user']);
};
```

### 6. Branding

**Universal Login Page:**
- Customize with PyMD branding
- Logo, colors, custom CSS
- Custom domain (optional): `auth.pymd.io`

---

## Authentication Flow

### Authorization Code Flow with PKCE

**PKCE (Proof Key for Code Exchange)** is essential for SPAs to prevent authorization code interception attacks.

### Step-by-Step Flow

```
┌──────────┐                                           ┌──────────┐
│  User    │                                           │ Frontend │
└────┬─────┘                                           └────┬─────┘
     │                                                      │
     │ 1. Click "Login"                                     │
     │─────────────────────────────────────────────────────>│
     │                                                      │
     │                                                      │ 2. Generate code_verifier
     │                                                      │    & code_challenge
     │                                                      │
     │                                                      │ 3. Redirect to Auth0
     │<─────────────────────────────────────────────────────│
     │                                                      │
┌────▼─────┐                                           ┌────▼─────┐
│  Auth0   │                                           │  Auth0   │
└────┬─────┘                                           └────┬─────┘
     │                                                      │
     │ 4. User authenticates (email/password or social)     │
     │                                                      │
     │ 5. Redirect with authorization code                  │
     │─────────────────────────────────────────────────────>│
     │                                                      │
┌────▼─────┐                                           ┌────▼─────┐
│ Frontend │                                           │ Backend  │
└────┬─────┘                                           └────┬─────┘
     │                                                      │
     │ 6. Exchange code + code_verifier for tokens          │
     │─────────────────────────────────────────────────────>│
     │                                                      │
     │                                                      │ 7. Verify with Auth0
     │                                                      │────────────>┌─────────┐
     │                                                      │             │ Auth0   │
     │                                                      │<────────────└─────────┘
     │                                                      │ 8. Return tokens
     │ 9. Return tokens + user info                         │
     │<─────────────────────────────────────────────────────│
     │                                                      │
     │ 10. Store tokens securely                            │
     │                                                      │
     │ 11. Make authenticated API requests                  │
     │─────────────────────────────────────────────────────>│
     │                                                      │
```

### Detailed Steps

#### Step 1-3: Initiate Login
```typescript
// Frontend generates PKCE values
const codeVerifier = generateRandomString(128);
const codeChallenge = await sha256(codeVerifier);

// Redirect to Auth0
const authUrl = `https://${AUTH0_DOMAIN}/authorize?` +
  `client_id=${CLIENT_ID}` +
  `&response_type=code` +
  `&redirect_uri=${encodeURIComponent(CALLBACK_URL)}` +
  `&scope=openid profile email offline_access` +
  `&audience=${API_IDENTIFIER}` +
  `&code_challenge=${codeChallenge}` +
  `&code_challenge_method=S256` +
  `&state=${generateRandomString(32)}`;

window.location.href = authUrl;
```

#### Step 4-5: User Authentication
- User enters credentials or uses social login
- Auth0 validates and redirects back with authorization code
- URL: `https://app.pymd.io/auth/callback?code=AUTH_CODE&state=STATE`

#### Step 6-8: Token Exchange
```typescript
// Frontend sends to backend
POST /api/v1/auth/callback
{
  "code": "AUTH_CODE",
  "state": "STATE",
  "codeVerifier": "CODE_VERIFIER"
}

// Backend exchanges with Auth0
POST https://${AUTH0_DOMAIN}/oauth/token
{
  "grant_type": "authorization_code",
  "client_id": "${CLIENT_ID}",
  "client_secret": "${CLIENT_SECRET}",  // Backend only
  "code": "AUTH_CODE",
  "redirect_uri": "${CALLBACK_URL}",
  "code_verifier": "CODE_VERIFIER"
}

// Auth0 responds with tokens
{
  "access_token": "eyJ...",
  "refresh_token": "v1.M...",
  "id_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

#### Step 9-11: Authenticated State
```typescript
// Backend creates session and returns to frontend
{
  "accessToken": "eyJ...",
  "refreshToken": "v1.M...",
  "expiresIn": 3600,
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe"
  }
}

// Frontend stores tokens and makes authenticated requests
Authorization: Bearer eyJ...
```

---

## Frontend Integration

### 1. Technology Stack

**Recommended Library:** `@auth0/auth0-react` (for React) or `@auth0/nextjs-auth0` (for Next.js)

**Installation:**
```bash
pnpm add @auth0/nextjs-auth0
```

### 2. Environment Variables

```env
# .env.local
AUTH0_SECRET='use [openssl rand -hex 32] to generate a 32 bytes value'
AUTH0_BASE_URL='http://localhost:3000'
AUTH0_ISSUER_BASE_URL='https://your-tenant.auth0.com'
AUTH0_CLIENT_ID='your_client_id'
AUTH0_CLIENT_SECRET='your_client_secret'
AUTH0_AUDIENCE='https://api.pymd.io'
AUTH0_SCOPE='openid profile email offline_access'
```

### 3. Next.js App Router Setup

**File: `app/api/auth/[auth0]/route.ts`**

```typescript
import { handleAuth, handleLogin } from '@auth0/nextjs-auth0';

export const GET = handleAuth({
  login: handleLogin({
    returnTo: '/dashboard',
    authorizationParams: {
      audience: process.env.AUTH0_AUDIENCE,
      scope: 'openid profile email offline_access'
    }
  })
});
```

**File: `app/providers/AuthProvider.tsx`**

```typescript
'use client';

import { UserProvider } from '@auth0/nextjs-auth0/client';

export default function AuthProvider({
  children
}: {
  children: React.ReactNode
}) {
  return <UserProvider>{children}</UserProvider>;
}
```

**File: `app/layout.tsx`**

```typescript
import AuthProvider from './providers/AuthProvider';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

### 4. Protected Routes

**File: `middleware.ts`**

```typescript
import { withMiddlewareAuthRequired } from '@auth0/nextjs-auth0/edge';

export default withMiddlewareAuthRequired();

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/documents/:path*',
    '/settings/:path*',
    '/api/protected/:path*'
  ]
};
```

### 5. Login/Logout Components

**Login Button:**
```typescript
'use client';

import { useUser } from '@auth0/nextjs-auth0/client';

export default function LoginButton() {
  const { user, isLoading } = useUser();

  if (isLoading) return <div>Loading...</div>;

  if (user) {
    return (
      <div>
        <span>Welcome, {user.name}</span>
        <a href="/api/auth/logout">Logout</a>
      </div>
    );
  }

  return <a href="/api/auth/login">Login</a>;
}
```

### 6. API Client with Authentication

**File: `lib/apiClient.ts`**

```typescript
import { getAccessToken } from '@auth0/nextjs-auth0';

export async function apiClient(endpoint: string, options: RequestInit = {}) {
  const { accessToken } = await getAccessToken();

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
      ...options.headers
    }
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}
```

### 7. Token Storage

**Recommended Approach for Next.js:**

1. **Server-Side Session** (Recommended)
   - Tokens stored in encrypted cookies
   - `@auth0/nextjs-auth0` handles this automatically
   - Tokens never exposed to client-side JavaScript
   - CSRF protection included

2. **Client-Side Storage** (Alternative)
   - Store access token in memory only
   - Refresh token in httpOnly, secure cookie
   - Use service worker for token refresh

### 8. Token Refresh

**Automatic Refresh:**
```typescript
// @auth0/nextjs-auth0 handles refresh automatically
// When getAccessToken() is called, it checks expiry and refreshes if needed

// Manual refresh endpoint
export async function POST(request: Request) {
  const session = await getSession();

  if (!session?.refreshToken) {
    return new Response('No refresh token', { status: 401 });
  }

  const response = await fetch(`https://${AUTH0_DOMAIN}/oauth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      grant_type: 'refresh_token',
      client_id: process.env.AUTH0_CLIENT_ID,
      client_secret: process.env.AUTH0_CLIENT_SECRET,
      refresh_token: session.refreshToken
    })
  });

  const tokens = await response.json();

  // Update session with new tokens
  await updateSession({
    ...session,
    accessToken: tokens.access_token,
    accessTokenExpiry: Date.now() + tokens.expires_in * 1000
  });

  return new Response(JSON.stringify(tokens), { status: 200 });
}
```

---

## Backend Integration

### 1. Technology Stack

**Libraries:**
- `python-jose[cryptography]` - JWT verification
- `requests` - HTTP client for Auth0 API
- `cryptography` - Token encryption

**Installation:**
```bash
pip install python-jose[cryptography] requests cryptography
```

### 2. Environment Variables

```env
# .env
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=https://api.pymd.io
AUTH0_ALGORITHMS=RS256
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_MANAGEMENT_API_TOKEN=management_api_token
```

### 3. JWT Verification Middleware

**File: `backend/auth/jwt_validator.py`**

```python
from jose import jwt, JWTError
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
from functools import lru_cache

security = HTTPBearer()

@lru_cache()
def get_jwks():
    """Fetch and cache Auth0 JWKS (public keys)"""
    url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    response = requests.get(url)
    return response.json()

def verify_token(token: str) -> dict:
    """
    Verify Auth0 JWT token

    Validates:
    - Signature using Auth0 public key
    - Expiration
    - Audience
    - Issuer
    """
    try:
        jwks = get_jwks()

        # Decode token header to get key ID
        unverified_header = jwt.get_unverified_header(token)

        # Find matching key in JWKS
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break

        if not rsa_key:
            raise HTTPException(
                status_code=401,
                detail="Unable to find appropriate key"
            )

        # Verify and decode token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[AUTH0_ALGORITHMS],
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid claims")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Unable to parse token: {str(e)}")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Dependency to get current authenticated user from JWT
    Usage: user = Depends(get_current_user)
    """
    token = credentials.credentials
    payload = verify_token(token)

    # Extract user info from token
    auth0_id = payload.get("sub")

    # Fetch user from database
    user = await get_user_by_auth0_id(auth0_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

### 4. Protected Endpoints

**Example Usage:**

```python
from fastapi import APIRouter, Depends
from backend.auth.jwt_validator import get_current_user

router = APIRouter()

@router.get("/documents")
async def list_documents(user: dict = Depends(get_current_user)):
    """List documents for authenticated user"""
    documents = await get_user_documents(user["id"])
    return {"documents": documents}

@router.get("/documents/{document_id}")
async def get_document(
    document_id: str,
    user: dict = Depends(get_current_user)
):
    """Get document if user has permission"""
    document = await get_document_by_id(document_id)

    if document["owner_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"document": document}
```

### 5. User Synchronization

**File: `backend/auth/sync.py`**

```python
@router.post("/internal/auth/sync-user")
async def sync_user_from_auth0(
    data: dict,
    internal_token: str = Header(..., alias="Authorization")
):
    """
    Sync user from Auth0 to local database
    Called by Auth0 Action on login
    """
    # Verify internal token
    if internal_token != f"Bearer {INTERNAL_API_TOKEN}":
        raise HTTPException(status_code=401)

    auth0_id = data["auth0Id"]
    email = data["email"]
    name = data["name"]
    picture = data.get("picture")
    email_verified = data.get("emailVerified", False)

    # Upsert user in database
    user = await upsert_user(
        auth0_id=auth0_id,
        email=email,
        name=name,
        avatar_url=picture,
        email_verified=email_verified
    )

    return {"success": True, "user_id": user["id"]}
```

### 6. Session Management

**Create Session:**
```python
@router.post("/auth/callback")
async def auth_callback(data: dict):
    """Handle Auth0 callback"""
    # Exchange authorization code for tokens
    tokens = await exchange_code_for_tokens(
        code=data["code"],
        code_verifier=data["codeVerifier"]
    )

    # Verify and decode ID token
    id_token = verify_token(tokens["id_token"])

    # Get or create user
    user = await get_or_create_user_from_id_token(id_token)

    # Create session
    session = await create_session(
        user_id=user["id"],
        access_token=encrypt(tokens["access_token"]),
        refresh_token=encrypt(tokens["refresh_token"]),
        expires_at=datetime.now() + timedelta(seconds=tokens["expires_in"])
    )

    return {
        "accessToken": tokens["access_token"],
        "refreshToken": tokens["refresh_token"],
        "expiresIn": tokens["expires_in"],
        "user": user
    }
```

---

## Security Considerations

### 1. Token Security

**Best Practices:**

- ✅ **Never log tokens**: Redact tokens in logs
- ✅ **Encrypt at rest**: Encrypt refresh tokens in database
- ✅ **Use HTTPS only**: All token transmission over TLS
- ✅ **Short-lived access tokens**: 1 hour expiration
- ✅ **Rotate refresh tokens**: Enable rotation in Auth0
- ✅ **Secure storage**: httpOnly, secure cookies in frontend
- ❌ **No localStorage**: Never store tokens in localStorage (XSS risk)

### 2. CSRF Protection

**Implementation:**

1. **State Parameter**: Verify state parameter in OAuth flow
2. **SameSite Cookies**: Use `SameSite=Lax` or `Strict`
3. **CSRF Tokens**: For state-changing operations

```typescript
// Generate state parameter
const state = crypto.randomBytes(16).toString('hex');
sessionStorage.setItem('auth_state', state);

// Verify on callback
const returnedState = urlParams.get('state');
const savedState = sessionStorage.getItem('auth_state');

if (returnedState !== savedState) {
  throw new Error('CSRF attack detected');
}
```

### 3. XSS Prevention

**Measures:**

1. **Content Security Policy (CSP)**
   ```http
   Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.auth0.com
   ```

2. **Input Sanitization**: Sanitize all user input
3. **Output Encoding**: Encode output in HTML contexts
4. **Token Storage**: Never in localStorage, use httpOnly cookies

### 4. HTTPS Enforcement

```python
# Force HTTPS in production
if not request.url.scheme == "https" and not DEBUG:
    return RedirectResponse(
        request.url.replace(scheme="https"),
        status_code=301
    )
```

### 5. Rate Limiting

**Auth Endpoints:**
- `/auth/*`: 10 requests per minute per IP
- Failed login attempts: 5 attempts per hour per email
- Token refresh: 30 requests per hour per user

### 6. Audit Logging

**Log all auth events:**
```python
await log_auth_event({
    "event": "login_success",
    "user_id": user["id"],
    "ip_address": request.client.host,
    "user_agent": request.headers.get("user-agent"),
    "timestamp": datetime.utcnow()
})
```

---

## User Profile Management

### 1. Fetch User Profile

**From Auth0:**
```python
async def get_auth0_user_profile(auth0_id: str) -> dict:
    """Fetch full user profile from Auth0"""
    management_token = await get_management_api_token()

    response = requests.get(
        f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0_id}",
        headers={"Authorization": f"Bearer {management_token}"}
    )

    return response.json()
```

### 2. Update User Profile

**Sync to Auth0:**
```python
async def update_auth0_profile(auth0_id: str, data: dict):
    """Update user profile in Auth0"""
    management_token = await get_management_api_token()

    response = requests.patch(
        f"https://{AUTH0_DOMAIN}/api/v2/users/{auth0_id}",
        headers={
            "Authorization": f"Bearer {management_token}",
            "Content-Type": "application/json"
        },
        json={
            "name": data.get("name"),
            "picture": data.get("picture"),
            "user_metadata": {
                "bio": data.get("bio")
            }
        }
    )

    return response.json()
```

### 3. Custom User Metadata

**Auth0 provides two metadata types:**

1. **user_metadata**: User-editable data (preferences, bio)
2. **app_metadata**: Application data (roles, permissions)

**Store in ID Token:**
```javascript
// Auth0 Action
api.idToken.setCustomClaim('https://pymd.io/user_metadata', event.user.user_metadata);
api.idToken.setCustomClaim('https://pymd.io/app_metadata', event.user.app_metadata);
```

---

## Error Handling

### 1. Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_grant` | Invalid authorization code | Request new code |
| `unauthorized_client` | Wrong client ID/secret | Check Auth0 config |
| `invalid_token` | Expired or invalid token | Refresh token |
| `insufficient_scope` | Missing required scope | Request additional scopes |
| `invalid_request` | Malformed request | Check request parameters |

### 2. Error Response Format

```json
{
  "error": "invalid_grant",
  "error_description": "Invalid authorization code",
  "error_uri": "https://auth0.com/docs/errors/invalid_grant"
}
```

### 3. Frontend Error Handling

```typescript
try {
  await login();
} catch (error) {
  if (error.error === 'login_required') {
    // Redirect to login
    router.push('/login');
  } else if (error.error === 'consent_required') {
    // Request user consent
    await requestConsent();
  } else {
    // Show generic error
    toast.error('Authentication failed. Please try again.');
  }
}
```

### 4. Backend Error Handling

```python
try:
    payload = verify_token(token)
except jwt.ExpiredSignatureError:
    # Token expired - suggest refresh
    raise HTTPException(
        status_code=401,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer error=\"invalid_token\""}
    )
except JWTError:
    # Invalid token
    raise HTTPException(
        status_code=401,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
```

---

## Testing Strategy

### 1. Unit Tests

**Test JWT Verification:**
```python
def test_verify_valid_token():
    token = create_test_token()
    payload = verify_token(token)
    assert payload["sub"] == "auth0|123"

def test_verify_expired_token():
    token = create_expired_test_token()
    with pytest.raises(HTTPException) as exc:
        verify_token(token)
    assert exc.value.status_code == 401
```

### 2. Integration Tests

**Mock Auth0:**
```python
@pytest.fixture
def mock_auth0():
    with responses.RequestsMock() as rsps:
        # Mock JWKS endpoint
        rsps.add(
            responses.GET,
            f"https://{AUTH0_DOMAIN}/.well-known/jwks.json",
            json={"keys": [test_jwk]},
            status=200
        )

        # Mock token endpoint
        rsps.add(
            responses.POST,
            f"https://{AUTH0_DOMAIN}/oauth/token",
            json={"access_token": "test_token"},
            status=200
        )

        yield rsps
```

### 3. End-to-End Tests

**Use Auth0 Test Users:**
```typescript
// Playwright E2E test
test('user can login and access dashboard', async ({ page }) => {
  await page.goto('/login');

  // Fill Auth0 login form
  await page.fill('input[name="email"]', process.env.TEST_USER_EMAIL);
  await page.fill('input[name="password"]', process.env.TEST_USER_PASSWORD);
  await page.click('button[type="submit"]');

  // Verify redirect to dashboard
  await expect(page).toHaveURL('/dashboard');

  // Verify user info displayed
  await expect(page.locator('[data-testid="user-name"]'))
    .toHaveText('Test User');
});
```

### 4. Load Testing

**Test authentication flow under load:**
```bash
# k6 load test
k6 run --vus 100 --duration 30s auth-load-test.js
```

---

## Monitoring and Logging

### 1. Auth0 Logs

**Monitor in Auth0 Dashboard:**
- Login attempts (success/failure)
- Token exchanges
- API calls to Management API
- Rate limit violations

**Stream to External System:**
- Configure Auth0 log streaming to Datadog, Splunk, or CloudWatch
- Real-time alerting on suspicious activity

### 2. Application Logs

**Log Authentication Events:**
```python
logger.info(
    "User authenticated",
    extra={
        "event": "auth_success",
        "user_id": user["id"],
        "auth0_id": user["auth0_id"],
        "ip": request.client.host,
        "user_agent": request.headers.get("user-agent")
    }
)
```

### 3. Metrics to Track

- **Login Success Rate**: Percentage of successful logins
- **Token Refresh Rate**: Frequency of token refreshes
- **Average Login Duration**: Time from login click to authenticated state
- **Failed Login Attempts**: Track and alert on spikes
- **Active Sessions**: Number of concurrent sessions

### 4. Alerts

**Configure alerts for:**
- 🚨 High rate of failed logins (> 10% in 5 minutes)
- 🚨 Spike in 401 errors (authentication failures)
- 🚨 Auth0 service degradation
- 🚨 JWT verification failures
- 🚨 Suspicious login patterns (multiple IPs for same user)

### 5. Security Monitoring

**Auth0 Anomaly Detection:**
- Brute force protection (auto-enabled)
- Breached password detection
- Suspicious IP throttling

**Custom Monitoring:**
```python
# Track failed login attempts
async def track_failed_login(email: str, ip: str):
    key = f"failed_login:{email}"
    count = await redis.incr(key)
    await redis.expire(key, 3600)  # 1 hour

    if count > 5:
        # Trigger alert
        await send_alert(
            "Possible brute force attack",
            f"5+ failed logins for {email} from {ip}"
        )

        # Temporary block
        await redis.setex(f"blocked_ip:{ip}", 1800, "1")  # 30 min
```

---

## Production Checklist

### Pre-Launch

- [ ] Auth0 application configured in production tenant
- [ ] Custom domain configured (auth.pymd.io)
- [ ] Branding customized (logo, colors)
- [ ] MFA enabled for admin accounts
- [ ] Refresh token rotation enabled
- [ ] Anomaly detection enabled
- [ ] Log streaming configured
- [ ] Monitoring and alerts set up
- [ ] Test accounts created
- [ ] E2E tests passing
- [ ] Security audit completed
- [ ] Rate limiting configured
- [ ] HTTPS enforced
- [ ] CSP headers configured
- [ ] Session timeout configured
- [ ] Backup authentication method ready

### Post-Launch

- [ ] Monitor login success rate
- [ ] Monitor error rates
- [ ] Track performance metrics
- [ ] Review Auth0 logs daily
- [ ] Test token refresh flow
- [ ] Verify session management
- [ ] Check for security alerts
- [ ] Review access patterns

---

**End of Auth0 Integration Plan**
