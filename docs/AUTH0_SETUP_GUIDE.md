# Auth0 Setup Guide for PyMD

This guide will walk you through setting up Auth0 for the PyMD web platform using **Client ID and Client Secret** (no API required).

## Prerequisites

- An Auth0 account (sign up for free at https://auth0.com)

## Step-by-Step Setup

### 1. Create Auth0 Account

1. Go to https://auth0.com and click "Sign Up"
2. Complete the registration process
3. Choose a tenant domain (e.g., `your-company.auth0.com` or `your-company.us.auth0.com`)
   - **Important**: Remember your domain - you'll need it later!

### 2. Create a New Application

1. Log in to your Auth0 Dashboard
2. Navigate to **Applications** → **Applications** in the left sidebar
3. Click **"+ Create Application"**

4. Configure the application:
   - **Name**: `PyMD Web App` (or any name you prefer)
   - **Application Type**: Select **"Regular Web Applications"**
   - Click **"Create"**

### 3. Configure Application Settings

After creating the application, you'll be on the application's **Settings** tab:

#### Basic Information
- Copy and save these values (you'll need them later):
  - **Domain**: `your-domain.auth0.com` (or `.us.auth0.com`, `.eu.auth0.com`, etc.)
  - **Client ID**: A long string like `abc123xyz...`
  - **Client Secret**: Click "Show" and copy the secret

#### Application URIs

Scroll down to **Application URIs** and configure:

1. **Allowed Callback URLs**:
   ```
   http://localhost:3000/api/auth/callback
   ```

2. **Allowed Logout URLs**:
   ```
   http://localhost:3000
   ```

3. **Allowed Web Origins**:
   ```
   http://localhost:3000
   ```

4. **Allowed Origins (CORS)**:
   ```
   http://localhost:3000
   ```

#### Advanced Settings

Scroll down to **Advanced Settings** → **Grant Types**:
- Ensure these are checked:
  - ✅ Authorization Code
  - ✅ Refresh Token

**Save Changes** at the bottom of the page.

### 4. Configure Social Connections (Optional)

If you want to enable Google login:

1. Navigate to **Authentication** → **Social** in the left sidebar
2. Find **Google** and click on it
3. Click **"Try it"** for a quick setup, or configure with your own Google OAuth credentials
4. Enable the connection for your application

### 5. Get Your Credentials

You now have everything you need:

| Setting | Value | Where to Find |
|---------|-------|---------------|
| **Domain** | `your-domain.auth0.com` | Applications → Your App → Settings → Domain |
| **Client ID** | `abc123xyz...` | Applications → Your App → Settings → Client ID |
| **Client Secret** | `secret123...` | Applications → Your App → Settings → Client Secret (click "Show") |

## Configure PyMD

### 1. Create Environment Files

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your Auth0 credentials:

```env
# Auth0 Configuration (Backend)
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id-here
AUTH0_CLIENT_SECRET=your-client-secret-here

# Auth0 Configuration (Frontend)
NEXT_PUBLIC_AUTH0_DOMAIN=your-domain.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id-here

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 2. Configure Frontend

Create `frontend/.env.local`:

```bash
cd frontend
cp .env.local.example .env.local
```

Generate a secret for `AUTH0_SECRET`:
```bash
openssl rand -hex 32
```

Edit `frontend/.env.local`:

```env
# Auth0 Configuration
AUTH0_SECRET='paste-the-generated-secret-here'
AUTH0_BASE_URL='http://localhost:3000'
AUTH0_ISSUER_BASE_URL='https://your-domain.auth0.com'
AUTH0_CLIENT_ID='your-client-id-here'
AUTH0_CLIENT_SECRET='your-client-secret-here'

# Public Auth0 Configuration
NEXT_PUBLIC_AUTH0_DOMAIN='your-domain.auth0.com'
NEXT_PUBLIC_AUTH0_CLIENT_ID='your-client-id-here'

# API Configuration
NEXT_PUBLIC_API_URL='http://localhost:8000'
NEXT_PUBLIC_WS_URL='ws://localhost:8000'
```

### 3. Example Configuration

Here's a complete example with fake values (replace with your actual values):

**Root `.env`:**
```env
AUTH0_DOMAIN=dev-abc123.us.auth0.com
AUTH0_CLIENT_ID=xYz123AbC456DeF789
AUTH0_CLIENT_SECRET=xYz_AbC-123_DeF-456_GhI-789_JkL

NEXT_PUBLIC_AUTH0_DOMAIN=dev-abc123.us.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=xYz123AbC456DeF789

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

**Frontend `.env.local`:**
```env
AUTH0_SECRET='a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6'
AUTH0_BASE_URL='http://localhost:3000'
AUTH0_ISSUER_BASE_URL='https://dev-abc123.us.auth0.com'
AUTH0_CLIENT_ID='xYz123AbC456DeF789'
AUTH0_CLIENT_SECRET='xYz_AbC-123_DeF-456_GhI-789_JkL'

NEXT_PUBLIC_AUTH0_DOMAIN='dev-abc123.us.auth0.com'
NEXT_PUBLIC_AUTH0_CLIENT_ID='xYz123AbC456DeF789'

NEXT_PUBLIC_API_URL='http://localhost:8000'
NEXT_PUBLIC_WS_URL='ws://localhost:8000'
```

## Start the Application

```bash
# Start all services
docker-compose up --build

# Or start in background
docker-compose up -d --build
```

## Test Authentication

1. Open your browser to http://localhost:3000
2. Click "Get Started" or "Sign in"
3. You'll be redirected to Auth0 login page
4. Sign up with email or social login
5. After successful login, you'll be redirected to the dashboard

## Troubleshooting

### Issue: "Callback URL mismatch"

**Solution**: Verify in Auth0 Dashboard → Applications → Your App → Settings:
- **Allowed Callback URLs** includes: `http://localhost:3000/api/auth/callback`

### Issue: "Invalid audience"

**Solution**: This shouldn't happen with Client ID/Secret setup. If you see this error:
1. Check that `AUTH0_CLIENT_ID` in backend `.env` matches your Auth0 Client ID exactly
2. Verify the token is being generated correctly in the frontend

### Issue: "Login page doesn't load"

**Solution**:
1. Check that `AUTH0_DOMAIN` is correct (including region like `.us.auth0.com`)
2. Verify frontend `.env.local` has `AUTH0_ISSUER_BASE_URL` with `https://` prefix
3. Check browser console for errors

### Issue: "Token validation failed"

**Solution**:
1. Ensure `AUTH0_CLIENT_ID` in backend matches the Client ID in Auth0
2. Check that the token is being passed in the Authorization header
3. Verify JWKS URL is accessible: `https://your-domain.auth0.com/.well-known/jwks.json`

### Issue: "CORS error"

**Solution**:
1. Verify in Auth0: **Allowed Web Origins** includes `http://localhost:3000`
2. Check backend CORS configuration in `docker-compose.yml`

## Production Deployment

When deploying to production:

### 1. Update Auth0 Application URLs

In Auth0 Dashboard → Applications → Your App → Settings:

1. **Allowed Callback URLs**:
   ```
   http://localhost:3000/api/auth/callback,
   https://your-domain.com/api/auth/callback
   ```

2. **Allowed Logout URLs**:
   ```
   http://localhost:3000,
   https://your-domain.com
   ```

3. **Allowed Web Origins**:
   ```
   http://localhost:3000,
   https://your-domain.com
   ```

### 2. Update Environment Variables

Update your production environment variables to use HTTPS:

```env
AUTH0_BASE_URL='https://your-domain.com'
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WS_URL=wss://api.your-domain.com
```

## Security Best Practices

1. **Never commit `.env` files** - They contain secrets!
2. **Use environment variables** in production (don't hardcode credentials)
3. **Rotate Client Secret** periodically in Auth0 Dashboard
4. **Enable MFA** (Multi-Factor Authentication) for your Auth0 account
5. **Use HTTPS** in production
6. **Monitor Auth0 logs** for suspicious activity

## Additional Resources

- [Auth0 Documentation](https://auth0.com/docs)
- [Auth0 Next.js SDK](https://auth0.com/docs/quickstart/webapp/nextjs)
- [Auth0 Dashboard](https://manage.auth0.com)

## Quick Checklist

Before starting the application, verify:

- [ ] Auth0 application created (Regular Web Application)
- [ ] Client ID and Client Secret copied
- [ ] Callback URLs configured in Auth0
- [ ] Root `.env` file created with Auth0 credentials
- [ ] Frontend `.env.local` file created with Auth0 credentials
- [ ] `AUTH0_SECRET` generated (32 hex characters)
- [ ] All URLs match (localhost:3000 for development)

---

If you encounter any issues not covered here, check the Auth0 logs:
1. Go to Auth0 Dashboard → Monitoring → Logs
2. Look for recent failed login attempts or errors
3. The error messages will help identify the issue
