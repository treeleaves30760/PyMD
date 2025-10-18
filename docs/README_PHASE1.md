# PyMD Web Platform - Phase 1 Implementation Complete

This document provides setup instructions for the Phase 1 core infrastructure of the PyMD web platform.

## Phase 1 Deliverables ✅

### Backend (Complete)
- ✅ FastAPI application structure with async support
- ✅ PostgreSQL database schema with SQLAlchemy 2.0
- ✅ Alembic migrations for database versioning
- ✅ Auth0 JWT validation middleware
- ✅ Redis connection and cache management
- ✅ Core API endpoints:
  - Health checks (`/health`, `/health/ready`, `/health/live`)
  - Authentication (`/api/v1/auth/me`, `/api/v1/auth/callback`)
  - User management (`/api/v1/users/*`)
- ✅ Security headers and CORS configuration
- ✅ Pytest testing framework

### Frontend (Complete)
- ✅ Next.js 15 with App Router and React 19
- ✅ TypeScript configuration
- ✅ Tailwind CSS with custom theme
- ✅ Shadcn/ui component library integration
- ✅ Auth0 SDK integration with protected routes
- ✅ Layout components (Header with user menu)
- ✅ Dashboard page with authentication
- ✅ Vitest testing framework

### Infrastructure (Complete)
- ✅ Docker Compose for local development
- ✅ PostgreSQL 15 container
- ✅ Redis 7 container
- ✅ Environment configuration files
- ✅ Dockerfile for backend and frontend

## Project Structure

```
PyMD/
├── pymd/                      # PyMD Python Package
│   ├── backend/               # FastAPI Backend
│   │   ├── app/
│   │   │   ├── api/v1/       # API endpoints
│   │   │   ├── core/         # Core modules (DB, Redis, Security)
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   └── main.py       # FastAPI app
│   │   ├── alembic/          # Database migrations
│   │   ├── tests/            # Backend tests
│   │   └── requirements.txt
│   ├── cli/                   # CLI interface (existing)
│   └── ...                    # Other PyMD modules
│
├── frontend/                  # Next.js Frontend
│   ├── app/                   # App Router pages
│   ├── components/            # React components
│   ├── lib/                   # Utilities
│   ├── middleware.ts          # Auth middleware
│   ├── Dockerfile.dev         # Development Dockerfile
│   └── package.json
│
├── Dockerfile.backend         # Backend production Dockerfile
├── docker-compose.yml         # Local development
├── .env.example              # Environment variables template
└── docs/                     # Documentation
    └── README_PHASE1.md      # This file
```

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ and pnpm (for local frontend development)
- Python 3.11+ (for local backend development)
- Auth0 account (for authentication)

## Setup Instructions

### 1. Auth0 Configuration

1. Create an Auth0 account at https://auth0.com
2. Create a new Application (Regular Web Application)
3. Configure Application Settings:
   - Allowed Callback URLs: `http://localhost:3000/api/auth/callback`
   - Allowed Logout URLs: `http://localhost:3000`
   - Allowed Web Origins: `http://localhost:3000`
   - Allowed Origins (CORS): `http://localhost:3000`
4. Note down from your Application:
   - Domain (e.g., `dev-abc123.us.auth0.com`)
   - Client ID
   - Client Secret

For detailed setup instructions, see [AUTH0_SETUP_GUIDE.md](./AUTH0_SETUP_GUIDE.md).

### 2. Environment Configuration

Create `.env` file in the project root:

```bash
# Copy from example
cp .env.example .env
```

Edit `.env` with your Auth0 credentials:

```env
# Auth0 Configuration (Backend)
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret

# Auth0 Configuration (Frontend)
NEXT_PUBLIC_AUTH0_DOMAIN=your-domain.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=your-client-id

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

Create `frontend/.env.local`:

```bash
cp frontend/.env.local.example frontend/.env.local
```

Edit with Auth0 credentials:

```env
AUTH0_SECRET='generate-with-openssl-rand-hex-32'
AUTH0_BASE_URL='http://localhost:3000'
AUTH0_ISSUER_BASE_URL='https://your-domain.auth0.com'
AUTH0_CLIENT_ID='your-client-id'
AUTH0_CLIENT_SECRET='your-client-secret'

NEXT_PUBLIC_AUTH0_DOMAIN='your-domain.auth0.com'
NEXT_PUBLIC_AUTH0_CLIENT_ID='your-client-id'

NEXT_PUBLIC_API_URL='http://localhost:8000'
NEXT_PUBLIC_WS_URL='ws://localhost:8000'
```

Generate `AUTH0_SECRET`:
```bash
openssl rand -hex 32
```

### 3. Start Services with Docker Compose

```bash
# Start all services
docker compose up --build

# Or start in background
docker compose up -d --build

# View logs
docker compose logs -f

# Stop services
docker compose down
```

This will start:
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`
- Backend API on `http://localhost:8000`
- Frontend on `http://localhost:3000`

### 4. Run Database Migrations

```bash
# Run migrations (backend container must be running)
docker compose exec backend alembic upgrade head
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (when DEBUG=true)

## Development Without Docker

### Backend Development

```bash
# Install PyMD package in development mode
pip install -e .

# Install backend dependencies
pip install -r pymd/backend/requirements.txt

# Start PostgreSQL and Redis (via Docker or locally)
docker compose up postgres redis -d

# Create .env file
cp .env.example .env
# Edit .env with your configuration

# Run migrations
cd pymd/backend
alembic upgrade head

# Start development server
uvicorn pymd.backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
pnpm install

# Create .env.local
cp .env.local.example .env.local
# Edit .env.local with your Auth0 credentials

# Start development server
pnpm dev

# The app will be available at http://localhost:3000
```

## Testing

### Backend Tests

```bash
cd pymd/backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_models.py
```

### Frontend Tests

```bash
cd frontend

# Run tests
pnpm test

# Run tests in watch mode
pnpm test -- --watch
```

## API Endpoints

### Health Checks
- `GET /health` - Basic health check
- `GET /health/ready` - Readiness check (DB + Redis)
- `GET /health/live` - Liveness check

### Authentication
- `GET /api/v1/auth/me` - Get current user (requires auth)
- `POST /api/v1/auth/callback` - Auth0 callback handler
- `POST /api/v1/auth/logout` - Logout

### Users
- `GET /api/v1/users/{user_id}` - Get user profile
- `PATCH /api/v1/users/{user_id}` - Update user profile
- `GET /api/v1/users/{user_id}/settings` - Get user settings
- `PATCH /api/v1/users/{user_id}/settings` - Update user settings

## Database Schema

### Users Table
- User authentication and profile information
- Linked to Auth0 via `auth0_id`
- Roles: admin, user, viewer

### Documents Table
- PyMD document storage
- Owner relationship to users
- Soft delete support
- Full-text search capability

### User Settings Table
- Per-user preferences
- Editor settings (JSON)
- Render settings (JSON)
- Theme and language preferences

### Sessions Table
- User session tracking
- Token management
- Activity monitoring

## Common Issues and Solutions

### Port Already in Use

If ports 3000, 5432, 6379, or 8000 are already in use:

```bash
# Stop services using those ports or modify docker-compose.yml
# Change port mappings:
ports:
  - "3001:3000"  # Frontend on 3001
  - "5433:5432"  # PostgreSQL on 5433
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker compose ps postgres

# View PostgreSQL logs
docker compose logs postgres

# Reset database
docker compose down -v
docker compose up postgres -d
docker compose exec backend alembic upgrade head
```

### Frontend Build Errors

```bash
# Clear Next.js cache
cd frontend
rm -rf .next
pnpm install
pnpm build
```

### Auth0 Configuration Issues

- Verify callback URLs match exactly (including protocol)
- Ensure Client ID and Client Secret are correct
- Check that CORS origins are configured in Auth0
- Verify JWT algorithm is RS256
- See [AUTH0_SETUP_GUIDE.md](./AUTH0_SETUP_GUIDE.md) for troubleshooting

## Next Steps (Phase 2)

Phase 2 will implement:
- Document CRUD API endpoints
- Document list and search functionality
- Monaco editor integration
- PyMD rendering service
- Document preview functionality

## Development Commands

### Backend

```bash
# Navigate to backend directory
cd pymd/backend

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Format code
black app/
ruff check app/

# Run linting
ruff check app/ --fix
```

### Frontend

```bash
# Install dependencies
pnpm install

# Development
pnpm dev

# Build
pnpm build

# Type check
pnpm type-check

# Lint
pnpm lint
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Auth0 Documentation](https://auth0.com/docs)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)

## Support

For issues or questions:
1. Check the [Quick Start Guide](./QUICK_START.md) for setup issues
2. Review the [Auth0 Setup Guide](./AUTH0_SETUP_GUIDE.md) for authentication problems
3. Check the planning documents in `/plans/`
4. Review API documentation at `http://localhost:8000/docs` when backend is running
5. Check Docker logs: `docker compose logs -f`

---

**Phase 1 Status**: ✅ Complete
**Next Phase**: Phase 2 - Document Management
**Last Updated**: 2025-01-18
