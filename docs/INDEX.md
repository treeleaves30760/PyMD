# PyMD Documentation Index

Welcome to the PyMD documentation! This index will help you find what you need.

## 📚 Getting Started

### New to PyMD Web Platform?
Start here to get up and running quickly:

1. **[Quick Start Guide](./QUICK_START.md)** ⭐
   - 5-minute setup guide
   - Get PyMD running locally
   - Perfect for first-time users

2. **[Auth0 Setup Guide](./AUTH0_SETUP_GUIDE.md)**
   - Complete Auth0 configuration
   - Step-by-step screenshots
   - Troubleshooting tips

## 🏗️ Implementation Documentation

### Phase 1: Core Infrastructure
- **[Phase 1 Documentation](./README_PHASE1.md)**
  - Complete feature list
  - Architecture overview
  - Development commands
  - API endpoints
  - Database schema
  - Testing guide

### Technical Changes
- **[Auth0 Simplified Setup](./CHANGES_AUTH0_SIMPLIFIED.md)**
  - What changed from API Audience to Client ID/Secret
  - Migration guide
  - Technical details

## 📋 Planning Documents

Located in `/plans/` directory:

- **[Implementation Summary](../plans/00_implementation_summary.md)**
  - Executive summary
  - Project overview
  - All phases roadmap
  - Success metrics

- **[System Architecture](../plans/01_system_architecture.md)**
  - High-level architecture
  - Technology stack
  - Backend architecture
  - Frontend architecture
  - Security design

- **[API Specifications](../plans/02_api_specifications.md)**
  - Complete API documentation
  - Request/response schemas
  - Error handling

- **[Storage Schema](../plans/03_storage_schema.md)**
  - Database design
  - Entity relationships
  - Indexing strategy

- **[Auth0 Integration Plan](../plans/04_auth0_integration.md)**
  - Authentication flow
  - Security considerations
  - Implementation details

- **[Frontend Architecture](../plans/05_frontend_architecture.md)**
  - Component design
  - State management
  - Routing structure

## 🔐 Security & Policies

- **[Security Policy](./SECURITY.md)**
  - Security guidelines
  - Vulnerability reporting
  - Best practices

- **[Contributing Guidelines](./CONTRIBUTING.md)**
  - How to contribute
  - Code standards
  - Pull request process

- **[License](./LICENSE)**
  - MIT License details

## 🎯 Quick Links by Task

### I want to...

**Set up PyMD locally**
→ [Quick Start Guide](./QUICK_START.md)

**Configure Auth0**
→ [Auth0 Setup Guide](./AUTH0_SETUP_GUIDE.md)

**Understand the architecture**
→ [System Architecture](../plans/01_system_architecture.md)

**See what's implemented**
→ [Phase 1 Documentation](./README_PHASE1.md)

**Learn about API endpoints**
→ [Phase 1 - API Endpoints](./README_PHASE1.md#api-endpoints)

**Understand database schema**
→ [Phase 1 - Database Schema](./README_PHASE1.md#database-schema)

**Contribute to the project**
→ [Contributing Guidelines](./CONTRIBUTING.md)

**Report a security issue**
→ [Security Policy](./SECURITY.md)

## 🚀 Development Workflow

### 1. Setup
```bash
# Clone repository
git clone <repository-url>
cd PyMD

# Configure environment
cp .env.example .env
# Edit .env with Auth0 credentials

# Start services
docker-compose up --build

# Initialize database
docker-compose exec backend alembic upgrade head
```

### 2. Development
```bash
# Backend development
docker-compose logs -f backend

# Frontend development
cd frontend
pnpm dev

# Run tests
docker-compose exec backend pytest
cd frontend && pnpm test
```

### 3. Documentation
```bash
# View API docs
http://localhost:8000/docs

# Read planning docs
/plans/

# Read implementation docs
/docs/
```

## 📊 Project Status

### ✅ Phase 1: Core Infrastructure (Complete)
- Backend API with FastAPI
- Frontend with Next.js 15
- Auth0 authentication
- PostgreSQL database
- Redis caching
- Docker setup

### 🔄 Phase 2: Document Management (Next)
- Document CRUD operations
- Monaco editor integration
- PyMD rendering service
- Real-time preview

### 📅 Future Phases
- Phase 3: Editor enhancement
- Phase 4: User experience
- Phase 5: Production readiness

## 🆘 Getting Help

### Common Issues
Check the troubleshooting sections in:
- [Quick Start - Troubleshooting](./QUICK_START.md#troubleshooting)
- [Auth0 Setup - Troubleshooting](./AUTH0_SETUP_GUIDE.md#troubleshooting)
- [Phase 1 - Common Issues](./README_PHASE1.md#common-issues-and-solutions)

### Need More Help?
1. Check existing documentation above
2. Review planning documents in `/plans/`
3. Check code comments in source files
4. Create an issue on GitHub

## 📝 Documentation Standards

When adding new documentation:
- Place setup guides in `/docs/`
- Place planning docs in `/plans/`
- Update this INDEX.md
- Use clear headings and examples
- Include troubleshooting section
- Add quick reference sections

---

**Last Updated**: 2025-01-18
**Documentation Version**: 1.0
**Project Phase**: Phase 1 Complete
