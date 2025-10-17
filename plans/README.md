# PyMD Web Platform - Planning Documents

This directory contains comprehensive planning and architectural documentation for the PyMD web platform.

## Overview

The PyMD web platform is a HackMD-like service that enables users to create, edit, and manage PyMD documents through a modern web interface. These documents outline the complete architecture, specifications, and implementation strategy for building a production-ready, multi-user web service.

## Document Index

### 📋 [00_implementation_summary.md](./00_implementation_summary.md)
**Executive summary and project overview**

A high-level overview of the entire project including:
- Project goals and vision
- Architecture summary
- Technology stack decisions
- Implementation phases (20-week roadmap)
- Development commands
- Success metrics and KPIs
- Risk assessment

**Start here** for a quick understanding of the entire project.

---

### 🏗️ [01_system_architecture.md](./01_system_architecture.md)
**Complete system architecture and design**

Detailed system architecture covering:
- High-level architecture diagrams
- Backend architecture (FastAPI, process management, WebSocket vs REST)
- Frontend-backend integration
- Scalability considerations (horizontal scaling, caching, resource management)
- Security architecture (Auth0, RBAC, session management)
- Infrastructure & deployment (Docker, Kubernetes)
- Observability & monitoring (Prometheus, logging)
- Architecture Decision Records (ADRs)

**~88KB** - Most comprehensive document with production-ready architecture patterns.

---

### 🔌 [02_api_specifications.md](./02_api_specifications.md)
**REST API specifications and contracts**

Complete API documentation including:
- API design principles
- Authentication & authorization flows
- Common response formats
- **Authentication endpoints** (login, logout, token refresh)
- **User management APIs** (profile, settings)
- **Document management APIs** (CRUD, search, pagination)
- **PyMD rendering APIs** (render, preview, validate, export)
- **System APIs** (health checks)
- **WebSocket APIs** (real-time features)
- Error codes reference
- Rate limiting strategies

**Use this** for backend API implementation and frontend API client development.

---

### 💾 [03_storage_schema.md](./03_storage_schema.md)
**Database schema and storage design**

Complete database architecture including:
- Database technology selection (PostgreSQL rationale)
- Entity definitions with SQL schemas:
  - `users` - User accounts and authentication
  - `documents` - PyMD document content and metadata
  - `user_settings` - User preferences (JSONB)
  - `sessions` - Session management
  - `tags` - Document categorization
  - `document_tags` - Many-to-many relationships
- Relationships and cardinality
- Indexing strategy (B-Tree, GIN, partial indexes)
- Document storage strategy (database vs file system)
- Migration strategy (Alembic)
- Backup and recovery procedures
- Performance optimization (query optimization, connection pooling)
- Multi-level caching strategy (Redis)

**Use this** for database implementation, migrations, and optimization.

---

### 🔐 [04_auth0_integration.md](./04_auth0_integration.md)
**Authentication and authorization implementation**

Complete Auth0 integration plan covering:
- Auth0 setup requirements (tenant, applications, APIs)
- Application configuration (SPA and M2M)
- Authorization Code Flow with PKCE (detailed flow diagram)
- Frontend integration (@auth0/nextjs-auth0)
  - Environment variables
  - Token storage (secure cookies)
  - Protected routes
  - Token refresh
- Backend integration (JWT verification, middleware)
  - Token validation
  - User synchronization
  - Session management
- Security considerations (CSRF, XSS, HTTPS)
- User profile management
- Error handling
- Testing strategy
- Monitoring and logging

**Use this** for implementing secure authentication on both frontend and backend.

---

### 🎨 [05_frontend_architecture.md](./05_frontend_architecture.md)
**Frontend architecture and component design**

Complete frontend architecture covering:
- Technology stack (Next.js 15, TypeScript, Tailwind CSS)
- Project structure (App Router, route groups)
- Routing architecture (public, protected, API routes)
- **Page specifications** with layouts:
  - Landing page
  - Dashboard
  - Document list
  - Document editor (Monaco integration)
  - Settings pages
- Component architecture (hierarchy, reusable components)
- State management strategy:
  - Server state (TanStack Query)
  - Client state (Zustand)
  - Form state (React Hook Form)
- Styling strategy (Tailwind, CSS variables, component variants)
- API integration (client, hooks, error handling)
- Real-time features (WebSocket vs polling)
- Performance optimization (code splitting, memoization, debouncing)
- User experience patterns (loading, error, empty states)

**Use this** for frontend implementation, component development, and UX design.

---

## Quick Start Guide

### For Project Managers
1. Read **00_implementation_summary.md** for overview
2. Review implementation phases and timeline
3. Check success metrics and risk assessment

### For Backend Developers
1. Read **01_system_architecture.md** for overall architecture
2. Read **02_api_specifications.md** for API contracts
3. Read **03_storage_schema.md** for database design
4. Read **04_auth0_integration.md** (backend sections)

### For Frontend Developers
1. Read **01_system_architecture.md** for overall architecture
2. Read **05_frontend_architecture.md** for frontend design
3. Read **02_api_specifications.md** for API integration
4. Read **04_auth0_integration.md** (frontend sections)

### For DevOps Engineers
1. Read **01_system_architecture.md** (infrastructure sections)
2. Review Docker and Kubernetes specifications
3. Check monitoring and observability requirements

### For Security Auditors
1. Read **04_auth0_integration.md** for authentication
2. Read **01_system_architecture.md** (security sections)
3. Read **02_api_specifications.md** (auth and rate limiting)
4. Read **03_storage_schema.md** (data encryption)

---

## Technology Stack Summary

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript 5.x
- **Styling**: Tailwind CSS 3.x
- **UI Components**: Shadcn/ui
- **State**: TanStack Query + Zustand
- **Editor**: Monaco Editor
- **Auth**: @auth0/nextjs-auth0

### Backend
- **Framework**: FastAPI 0.110+
- **Language**: Python 3.11+
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Cache**: Redis 7+
- **Auth**: Auth0 + python-jose
- **Jobs**: Celery + Redis

### Infrastructure
- **Containers**: Docker + Docker Compose
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Logging**: Structured JSON logs

---

## Implementation Timeline

### Phase 1: Core Infrastructure (Weeks 1-4)
- Backend and frontend setup
- Authentication implementation
- Database schema
- Basic API endpoints

### Phase 2: Document Management (Weeks 5-8)
- Document CRUD operations
- PyMD rendering service
- Document list and editor UI

### Phase 3: Editor Enhancement (Weeks 9-12)
- Live preview
- Auto-save
- Export functionality
- Editor customization

### Phase 4: User Experience (Weeks 13-16)
- Settings pages
- Dark mode
- Responsive design
- Polish and refinement

### Phase 5: Production Readiness (Weeks 17-20)
- Testing (unit, integration, E2E)
- Documentation
- CI/CD pipeline
- Deployment automation

**Total: ~20 weeks (5 months)**

---

## Key Features

### MVP Features
- ✅ User authentication (Auth0)
- ✅ Document management (CRUD)
- ✅ Monaco editor integration
- ✅ Real-time preview
- ✅ Auto-save
- ✅ Export (HTML, Markdown)
- ✅ Search and filter
- ✅ User settings
- ✅ Dark mode
- ✅ Responsive design

### Post-MVP Features
- ⏳ Real-time collaboration
- ⏳ Document sharing
- ⏳ Version history
- ⏳ PDF export
- ⏳ Templates
- ⏳ Public URLs
- ⏳ API keys

---

## Development Commands

### Backend
```bash
# Activate environment
source /opt/miniconda3/etc/profile.d/conda.sh && conda activate PyMD

# Start backend server
pyexecmd backend

# Run migrations
alembic upgrade head

# Run tests
pytest tests/
```

### Frontend
```bash
# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Build production
pnpm build

# Run tests
pnpm test
```

### Docker
```bash
# Start all services
docker-compose up --build

# View logs
docker-compose logs -f
```

---

## Architecture Highlights

### Multi-User Support
- **Auth0** for enterprise-grade authentication
- **PostgreSQL** for reliable data storage with ACID guarantees
- **Redis** for high-performance session and cache management
- **Docker** containers for process isolation

### Scalability
- **Horizontal scaling**: Multiple API server instances
- **Read replicas**: Database read scaling
- **Multi-level caching**: Browser, CDN, Redis, database
- **Background jobs**: Celery for async processing

### Security
- **OAuth2 + OIDC**: Industry-standard authentication
- **JWT tokens**: Signed with RS256
- **Encrypted storage**: Sensitive data encrypted at rest
- **Rate limiting**: Per-user and per-IP limits
- **HTTPS only**: TLS 1.3 for all traffic

### Performance
- **< 1s page load**: Target FCP under 1 second
- **< 500ms API**: Target API response under 500ms
- **Real-time preview**: Debounced rendering with < 1s latency
- **Aggressive caching**: Multiple cache layers

---

## Document Status

| Document | Status | Last Updated | Size |
|----------|--------|--------------|------|
| 00_implementation_summary.md | ✅ Complete | 2025-10-17 | 30 KB |
| 01_system_architecture.md | ✅ Complete | 2025-10-17 | 86 KB |
| 02_api_specifications.md | ✅ Complete | 2025-10-17 | 18 KB |
| 03_storage_schema.md | ✅ Complete | 2025-10-17 | 27 KB |
| 04_auth0_integration.md | ✅ Complete | 2025-10-17 | 31 KB |
| 05_frontend_architecture.md | ✅ Complete | 2025-10-17 | 45 KB |

**Total: ~237 KB of comprehensive technical documentation**

---

## Contributing

These planning documents are living documents and should be updated as the project evolves:

1. **Major architectural changes**: Update relevant sections
2. **Technology changes**: Document rationale in ADR format
3. **New features**: Update feature lists and specifications
4. **Lessons learned**: Add to risk assessment and mitigation

---

## Questions?

For questions about:
- **Architecture**: See 01_system_architecture.md
- **APIs**: See 02_api_specifications.md
- **Database**: See 03_storage_schema.md
- **Authentication**: See 04_auth0_integration.md
- **Frontend**: See 05_frontend_architecture.md
- **General**: See 00_implementation_summary.md

---

**Planning Phase Status**: ✅ **COMPLETE**

**Next Step**: Begin Phase 1 implementation (Environment Setup)

**Ready to build!** 🚀
