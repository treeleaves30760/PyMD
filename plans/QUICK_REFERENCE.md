# PyMD Web Platform - Quick Reference

**One-page reference for the entire project**

## 🎯 Project Goal

Build a HackMD-like web platform for creating, editing, and managing PyMD documents with multi-user support, real-time preview, and export capabilities.

---

## 🏗️ Architecture at a Glance

```
┌─────────────┐
│   Browser   │ Next.js 15 + React + TypeScript
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│  API Server │ FastAPI + Python 3.11+
└──────┬──────┘
       │
   ┌───┴────┬────────┬─────────┐
   ▼        ▼        ▼         ▼
┌────────┐ ┌─────┐ ┌─────┐ ┌──────┐
│Postgres│ │Redis│ │Auth0│ │PyMD  │
│  DB    │ │Cache│ │ IdP │ │Engine│
└────────┘ └─────┘ └─────┘ └──────┘
```

---

## 📚 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, TypeScript, Tailwind CSS, Monaco Editor |
| **Backend** | FastAPI, Python 3.11+, SQLAlchemy 2.0 |
| **Database** | PostgreSQL 15+ |
| **Cache** | Redis 7+ |
| **Auth** | Auth0 (OAuth2 + OIDC) |
| **Deployment** | Docker, Kubernetes, GitHub Actions |

---

## 🗄️ Database Schema (Core Tables)

```sql
users (id, auth0_id, email, name, avatar_url, role)
  ↓ 1:N
documents (id, owner_id, title, content, render_format)
  ↓ M:N
document_tags (document_id, tag_id)
  ↓
tags (id, name, slug)

user_settings (id, user_id, theme, editor_settings JSONB)
sessions (id, user_id, session_token, expires_at)
```

---

## 🔌 API Endpoints (Key Routes)

### Authentication
- `POST /api/v1/auth/callback` - Auth0 callback
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Current user

### Documents
- `GET /api/v1/documents` - List documents (paginated)
- `POST /api/v1/documents` - Create document
- `GET /api/v1/documents/:id` - Get document
- `PATCH /api/v1/documents/:id` - Update document
- `DELETE /api/v1/documents/:id` - Delete document

### Rendering
- `POST /api/v1/render` - Render PyMD content
- `POST /api/v1/render/preview` - Quick preview
- `GET /api/v1/documents/:id/export` - Export document

---

## 🔐 Authentication Flow

```
1. User clicks "Login"
2. Redirect to Auth0 (with PKCE)
3. User authenticates
4. Auth0 redirects back with code
5. Backend exchanges code for JWT
6. JWT stored in httpOnly cookie
7. All API requests include JWT
```

**Token Details:**
- Access Token: 1 hour expiry (RS256 signed)
- Refresh Token: 30 days expiry (encrypted)
- Storage: httpOnly, secure cookies

---

## 📁 Project Structure

```
PyMD/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API routes
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # Business logic
│   ├── alembic/             # Migrations
│   └── tests/
├── frontend/
│   ├── app/                 # Next.js App Router
│   │   ├── (auth)/         # Auth pages
│   │   ├── (dashboard)/    # Protected pages
│   │   └── api/            # API routes
│   ├── components/          # React components
│   ├── lib/                 # Utilities, hooks
│   └── styles/
└── plans/                   # This directory
```

---

## 🚀 Development Commands

### Backend
```bash
# Activate environment
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD

# Start server (NEW COMMAND)
pyexecmd backend

# Migrations
alembic upgrade head

# Tests
pytest tests/
```

### Frontend
```bash
# Install
pnpm install

# Dev server (NEW COMMAND)
pnpm dev

# Build
pnpm build

# Tests
pnpm test
```

### Docker
```bash
# Start all services
docker-compose up --build

# Background
docker-compose up -d

# Logs
docker-compose logs -f
```

---

## 📋 Implementation Phases

| Phase | Duration | Focus |
|-------|----------|-------|
| **1. Core Infrastructure** | Weeks 1-4 | Setup, Auth, Database |
| **2. Document Management** | Weeks 5-8 | CRUD, Editor, Rendering |
| **3. Editor Enhancement** | Weeks 9-12 | Live preview, Auto-save, Export |
| **4. User Experience** | Weeks 13-16 | Settings, Dark mode, Polish |
| **5. Production Ready** | Weeks 17-20 | Testing, CI/CD, Deploy |

**Total: 20 weeks (5 months)**

---

## ✅ MVP Feature Checklist

### Authentication
- [x] User registration (Auth0)
- [x] Login (email + Google)
- [x] Session management
- [x] Protected routes

### Document Management
- [x] Create document
- [x] Edit document
- [x] Delete document
- [x] List documents
- [x] Search documents
- [x] Auto-save

### Editor
- [x] Monaco editor
- [x] PyMD syntax highlighting
- [x] Split view (editor + preview)
- [x] Real-time preview
- [x] Full-screen mode
- [x] Keyboard shortcuts

### Export & Rendering
- [x] Render to HTML
- [x] Render to Markdown
- [x] Export files
- [x] Syntax validation

### UI/UX
- [x] Responsive design
- [x] Dark mode
- [x] User settings
- [x] Loading states
- [x] Error handling

---

## 🎨 Frontend Pages

| Route | Page | Auth Required |
|-------|------|---------------|
| `/` | Landing page | ❌ No |
| `/login` | Auth0 redirect | ❌ No |
| `/dashboard` | User dashboard | ✅ Yes |
| `/documents` | Document list | ✅ Yes |
| `/documents/:id` | Editor | ✅ Yes |
| `/settings/profile` | Profile settings | ✅ Yes |
| `/settings/preferences` | Editor preferences | ✅ Yes |

---

## 🔒 Security Checklist

- [x] Auth0 OAuth2 + OIDC
- [x] JWT RS256 signed tokens
- [x] HTTPS only (TLS 1.3)
- [x] httpOnly, secure cookies
- [x] CSRF protection (SameSite, state param)
- [x] XSS prevention (CSP headers)
- [x] SQL injection protection (parameterized queries)
- [x] Rate limiting (per-user, per-IP)
- [x] Input validation (Pydantic)
- [x] Encrypted token storage

---

## ⚡ Performance Targets

| Metric | Target | Acceptable |
|--------|--------|------------|
| Page Load (FCP) | < 1.0s | < 2.0s |
| API Response | < 200ms | < 500ms |
| Document Render | < 1.0s | < 2.0s |
| Search Query | < 500ms | < 1.0s |

**Scalability:**
- 10,000+ concurrent users
- 1,000+ API requests/sec
- Horizontal scaling ready

---

## 🎯 Success Metrics

### User Metrics
- 1,000+ sign-ups (first 3 months)
- 100+ daily active users
- > 40% 30-day retention
- > 10 min avg session duration

### Technical Metrics
- 99.9% uptime
- < 1% error rate
- < 500ms API latency (p95)
- > 80% cache hit rate
- > 80% test coverage

---

## 🛠️ State Management

### Frontend State Layers

```typescript
// Server State (TanStack Query)
useQuery(['documents']) // Documents from API

// Client State (Zustand)
useUIStore() // Theme, sidebar, layout

// Form State (React Hook Form)
useForm() // Form validation

// Local State (useState)
const [open, setOpen] = useState(false)

// URL State (Next.js)
searchParams.get('page')
```

---

## 📦 Key Dependencies

### Backend
```
fastapi==0.110+
sqlalchemy==2.0+
alembic==1.13+
redis==5.0+
python-jose[cryptography]==3.3+
uvicorn[standard]==0.27+
```

### Frontend
```json
{
  "next": "15.x",
  "@auth0/nextjs-auth0": "^3.x",
  "@tanstack/react-query": "^5.x",
  "zustand": "^4.x",
  "react-hook-form": "^7.x",
  "@monaco-editor/react": "^4.x",
  "tailwindcss": "^3.x"
}
```

---

## 🚨 Common Issues & Solutions

### Backend
**Issue:** `pyexecmd backend` not found
**Solution:** Activate conda environment first
```bash
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD
```

**Issue:** Database connection error
**Solution:** Check PostgreSQL is running and connection string

### Frontend
**Issue:** Auth callback fails
**Solution:** Check Auth0 configuration and callback URLs

**Issue:** Monaco editor not loading
**Solution:** Dynamic import with `ssr: false`

---

## 📖 Documentation Map

| Document | Size | Best For |
|----------|------|----------|
| **00_implementation_summary** | 30 KB | Overview, timeline, metrics |
| **01_system_architecture** | 86 KB | Architecture, infrastructure |
| **02_api_specifications** | 18 KB | API contracts, endpoints |
| **03_storage_schema** | 27 KB | Database design, migrations |
| **04_auth0_integration** | 31 KB | Authentication implementation |
| **05_frontend_architecture** | 45 KB | Frontend design, components |

**Total: 237 KB of technical specs**

---

## 🔗 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@localhost/pymd
REDIS_URL=redis://localhost:6379/0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_API_AUDIENCE=https://api.pymd.io
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
```

### Frontend (.env.local)
```env
AUTH0_SECRET='generate-with-openssl-rand-hex-32'
AUTH0_BASE_URL=http://localhost:3000
AUTH0_ISSUER_BASE_URL=https://your-tenant.auth0.com
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_AUDIENCE=https://api.pymd.io
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🎓 Learning Resources

### For Backend Devs
1. FastAPI: https://fastapi.tiangolo.com
2. SQLAlchemy: https://docs.sqlalchemy.org
3. Auth0 Python: https://auth0.com/docs/quickstart/backend/python

### For Frontend Devs
1. Next.js 15: https://nextjs.org/docs
2. TanStack Query: https://tanstack.com/query
3. Auth0 Next.js: https://auth0.com/docs/quickstart/webapp/nextjs

### For DevOps
1. Docker: https://docs.docker.com
2. Kubernetes: https://kubernetes.io/docs
3. GitHub Actions: https://docs.github.com/actions

---

## 🚀 Next Steps

1. **Week 1**: Set up GitHub repo, Auth0 tenant, databases
2. **Week 2**: Implement backend foundation and database schema
3. **Week 3**: Build frontend foundation with Next.js
4. **Week 4**: Connect frontend and backend, test auth flow
5. **Week 5+**: Follow implementation phases

---

## 📞 Getting Help

- **Architecture questions**: See `01_system_architecture.md`
- **API questions**: See `02_api_specifications.md`
- **Database questions**: See `03_storage_schema.md`
- **Auth questions**: See `04_auth0_integration.md`
- **Frontend questions**: See `05_frontend_architecture.md`

---

**Status**: ✅ Planning Complete - Ready for Implementation

**Created**: 2025-10-17

**Ready to code!** 🎉
