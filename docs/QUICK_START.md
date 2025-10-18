# PyMD Quick Start Guide

Get PyMD up and running in 5 minutes!

## 1. Auth0 Setup (2 minutes)

### Create Application in Auth0

1. Go to https://auth0.com → Sign up (free)
2. Create a new application:
   - **Applications** → **+ Create Application**
   - Name: `PyMD Web App`
   - Type: **Regular Web Applications**
   - Click **Create**

3. Configure URLs in **Settings** tab:
   - **Allowed Callback URLs**: `http://localhost:3000/api/auth/callback`
   - **Allowed Logout URLs**: `http://localhost:3000`
   - **Allowed Web Origins**: `http://localhost:3000`
   - **Allowed Origins (CORS)**: `http://localhost:3000`
   - Click **Save Changes**

4. Copy these values:
   - **Domain** (e.g., `dev-abc123.us.auth0.com`)
   - **Client ID** (long string)
   - **Client Secret** (click "Show" to reveal)

## 2. Configure Environment (2 minutes)

### Create `.env` file

```bash
# In project root
cp .env.example .env
```

Edit `.env` and paste your Auth0 values:

```env
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=paste-your-client-id
AUTH0_CLIENT_SECRET=paste-your-client-secret

NEXT_PUBLIC_AUTH0_DOMAIN=your-domain.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=paste-your-client-id

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### Create `frontend/.env.local` file

```bash
cd frontend
cp .env.local.example .env.local
```

Generate secret:
```bash
openssl rand -hex 32
```

Edit `frontend/.env.local`:

```env
AUTH0_SECRET='paste-generated-secret-here'
AUTH0_BASE_URL='http://localhost:3000'
AUTH0_ISSUER_BASE_URL='https://your-domain.auth0.com'
AUTH0_CLIENT_ID='paste-your-client-id'
AUTH0_CLIENT_SECRET='paste-your-client-secret'

NEXT_PUBLIC_AUTH0_DOMAIN='your-domain.auth0.com'
NEXT_PUBLIC_AUTH0_CLIENT_ID='paste-your-client-id'

NEXT_PUBLIC_API_URL='http://localhost:8000'
NEXT_PUBLIC_WS_URL='ws://localhost:8000'
```

## 3. Start Application (1 minute)

```bash
# From project root
docker compose up --build
```

Wait for all services to start (~30-60 seconds).

## 4. Initialize Database

Wait for all services to start, then in a new terminal:

```bash
docker compose exec backend alembic upgrade head
```

## 5. Open Application

Open your browser to: **http://localhost:3000**

Click **"Get Started"** → Sign up with email or Google → Dashboard!

---

## Troubleshooting

**"Callback URL mismatch"**: Check Auth0 Allowed Callback URLs includes `http://localhost:3000/api/auth/callback`

**"Cannot connect to backend"**: Wait 30 seconds for services to fully start, then refresh

**"Database error"**: Run `docker compose exec backend alembic upgrade head`

---

## What's Running?

- **Frontend**: http://localhost:3000 (Next.js)
- **Backend API**: http://localhost:8000 (FastAPI)
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## Next Steps

- Read the full setup guide: [AUTH0_SETUP_GUIDE.md](./AUTH0_SETUP_GUIDE.md)
- Review Phase 1 features: [README_PHASE1.md](./README_PHASE1.md)
- Check the planning docs: [plans/](../plans/)
- Browse all documentation: [INDEX.md](./INDEX.md)

---

**Need help?** Check [AUTH0_SETUP_GUIDE.md](./AUTH0_SETUP_GUIDE.md) for detailed troubleshooting.
