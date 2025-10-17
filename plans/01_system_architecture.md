# PyMD Web Application - System Architecture Plan

**Version:** 1.0
**Date:** 2025-10-17
**Status:** Planning Phase

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [High-Level Architecture](#high-level-architecture)
3. [Backend Architecture](#backend-architecture)
4. [Frontend Architecture](#frontend-architecture)
5. [Frontend-Backend Integration](#frontend-backend-integration)
6. [Scalability Considerations](#scalability-considerations)
7. [Security Architecture](#security-architecture)
8. [Infrastructure & Deployment](#infrastructure--deployment)
9. [Observability & Monitoring](#observability--monitoring)
10. [Architecture Decision Records](#architecture-decision-records)

---

## Executive Summary

PyMD is evolving from a single-user local development tool to a multi-user collaborative web platform similar to HackMD. This architecture plan outlines the technical foundation for building a scalable, secure, and maintainable web service that preserves PyMD's core strengths while enabling collaborative document creation and execution.

**Key Architectural Principles:**
- **Security-First Design**: Isolated execution environments, comprehensive authentication/authorization
- **Scalability by Design**: Horizontal scaling capability, stateless architecture where possible
- **Clean Architecture**: Clear separation of concerns, dependency inversion, testability
- **Cloud-Native Patterns**: Containerization, infrastructure as code, 12-factor methodology
- **Progressive Enhancement**: Maintain backwards compatibility with single-user mode

---

## High-Level Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Layer (Browser)                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │   Next.js Frontend (React 19, TypeScript, Tailwind CSS)     │  │
│  │   - Real-time editor                                         │  │
│  │   - Document management                                      │  │
│  │   - User authentication UI                                   │  │
│  │   - WebSocket client for live updates                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                         HTTPS / WebSocket
                                   │
┌─────────────────────────────────────────────────────────────────────┐
│                        API Gateway / Load Balancer                  │
│  - TLS termination                                                  │
│  - Rate limiting                                                    │
│  - Request routing                                                  │
│  - DDoS protection                                                  │
└─────────────────────────────────────────────────────────────────────┘
                                   │
            ┌──────────────────────┴──────────────────────┐
            │                                             │
┌───────────▼──────────────┐                ┌────────────▼─────────────┐
│   Backend API Service    │                │  Code Execution Service  │
│   (FastAPI / Python)     │                │  (Sandboxed Python)      │
│                          │                │                          │
│  - RESTful APIs          │◄───────────────┤  - Isolated execution    │
│  - WebSocket gateway     │   Job Queue    │  - Resource limits       │
│  - Auth middleware       │                │  - Security policies     │
│  - Document CRUD         │                │  - Result caching        │
│  - User management       │                │                          │
└──────────┬───────────────┘                └──────────────────────────┘
           │                                              │
           │                                              │
┌──────────▼──────────────────────────────────────────────▼────────────┐
│                        Data Layer                                    │
│                                                                       │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │   PostgreSQL    │  │     Redis        │  │  Object Storage   │  │
│  │   (Primary DB)  │  │  - Sessions      │  │  - Documents      │  │
│  │  - Users        │  │  - Cache         │  │  - Images         │  │
│  │  - Documents    │  │  - Job queue     │  │  - Videos         │  │
│  │  - Metadata     │  │  - WebSocket     │  │  - Exports        │  │
│  └─────────────────┘  └──────────────────┘  └───────────────────┘  │
└───────────────────────────────────────────────────────────────────────┘
           │
           │
┌──────────▼────────────────────────────────────────────────────────────┐
│                    External Services                                  │
│                                                                        │
│  ┌──────────────┐  ┌─────────────────┐  ┌──────────────────────┐    │
│  │   Auth0      │  │  Email Service  │  │  Monitoring (APM)    │    │
│  │  - OAuth2    │  │  - SendGrid     │  │  - DataDog/NewRelic  │    │
│  │  - JWT       │  │  - Mailgun      │  │  - Sentry            │    │
│  └──────────────┘  └─────────────────┘  └──────────────────────┘    │
└────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack Recommendations

**Frontend:**
- **Framework**: Next.js 15 (App Router) with React 19
- **Language**: TypeScript 5+
- **Styling**: Tailwind CSS 4
- **State Management**: React Server Components + Zustand for client state
- **Real-time**: Socket.IO client
- **Code Editor**: Monaco Editor (VS Code's editor)
- **Build Tool**: Turbopack (Next.js built-in)

**Backend:**
- **API Framework**: FastAPI (Python 3.11+)
- **WebSocket**: FastAPI WebSocket + Socket.IO
- **Task Queue**: Celery with Redis broker
- **Authentication**: Auth0 + PyJWT
- **ORM**: SQLAlchemy 2.0 with async support
- **Validation**: Pydantic v2
- **ASGI Server**: Uvicorn with Gunicorn

**Data Layer:**
- **Primary Database**: PostgreSQL 15+ (ACID compliance)
- **Cache & Queue**: Redis 7+ (Cluster mode)
- **Object Storage**: S3-compatible (AWS S3, MinIO, Cloudflare R2)
- **Search**: PostgreSQL full-text search (initial), Elasticsearch (scale-up)

**Infrastructure:**
- **Containerization**: Docker + Docker Compose (dev), Kubernetes (prod)
- **IaC**: Terraform or Pulumi
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana, Sentry for errors
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana) or Loki

### Service Boundaries

**Core Services:**

1. **API Service** - RESTful API and WebSocket gateway
2. **Execution Service** - Code execution in sandboxed environments
3. **Storage Service** - Document and media management
4. **Auth Service** - Authentication and authorization (Auth0)
5. **Notification Service** - Real-time updates and email notifications

**Supporting Services:**

6. **Cache Service** - Redis for caching and session management
7. **Queue Service** - Background job processing
8. **Search Service** - Document search and indexing (future)

---

## Backend Architecture

### Framework Selection: FastAPI

**Rationale for FastAPI:**

1. **Performance**: ASGI-based, comparable to Node.js and Go
2. **Type Safety**: Full Pydantic integration for request/response validation
3. **Async Native**: Built-in async/await support for concurrent operations
4. **Auto Documentation**: OpenAPI/Swagger docs generated automatically
5. **Python Ecosystem**: Direct integration with existing PyMD codebase
6. **WebSocket Support**: Native WebSocket support for real-time features
7. **Dependency Injection**: Clean DI system for testability

**Alternative Considerations:**
- **Django**: Too heavyweight, ORM-centric, less performant for API workloads
- **Flask**: Lacks async native support, requires more middleware setup
- **FastAPI Wins**: Modern async patterns, better performance, cleaner architecture

### Backend Project Structure

```
pymd_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   │
│   ├── api/                       # API layer (HTTP + WebSocket)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── auth.py        # Authentication endpoints
│   │   │   │   ├── documents.py   # Document CRUD
│   │   │   │   ├── execution.py   # Code execution requests
│   │   │   │   ├── users.py       # User management
│   │   │   │   └── health.py      # Health checks
│   │   │   └── websocket/
│   │   │       ├── handlers.py    # WebSocket event handlers
│   │   │       └── rooms.py       # Document room management
│   │   └── deps.py                # Dependency injection
│   │
│   ├── core/                      # Core business logic
│   │   ├── renderer.py            # PyMD rendering (adapted from existing)
│   │   ├── executor.py            # Code execution orchestration
│   │   ├── security.py            # Security utilities
│   │   ├── sandbox.py             # Sandboxing implementation
│   │   └── cache.py               # Caching strategies
│   │
│   ├── services/                  # Service layer (business logic)
│   │   ├── document_service.py    # Document operations
│   │   ├── execution_service.py   # Code execution management
│   │   ├── user_service.py        # User operations
│   │   ├── storage_service.py     # File storage abstraction
│   │   └── notification_service.py # Real-time notifications
│   │
│   ├── models/                    # Domain models (SQLAlchemy)
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── execution.py
│   │   └── session.py
│   │
│   ├── schemas/                   # Pydantic schemas (DTO)
│   │   ├── auth.py
│   │   ├── document.py
│   │   ├── execution.py
│   │   └── user.py
│   │
│   ├── repositories/              # Data access layer
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── document_repository.py
│   │   └── execution_repository.py
│   │
│   ├── middleware/                # Request/response middleware
│   │   ├── auth_middleware.py     # JWT validation
│   │   ├── rate_limit.py          # Rate limiting
│   │   ├── cors.py                # CORS configuration
│   │   └── logging.py             # Request logging
│   │
│   ├── workers/                   # Background workers (Celery)
│   │   ├── celery_app.py
│   │   ├── execution_worker.py    # Code execution tasks
│   │   └── cleanup_worker.py      # Resource cleanup
│   │
│   └── utils/                     # Utilities
│       ├── validators.py
│       ├── formatters.py
│       └── helpers.py
│
├── tests/                         # Test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
│
├── docker/
│   ├── Dockerfile
│   ├── Dockerfile.worker
│   └── docker-compose.yml
│
├── pyproject.toml                 # Python dependencies
├── requirements.txt
├── .env.example
└── README.md
```

### The `pyexecmd backend` Command

**Command Design:**

```bash
pyexecmd backend [OPTIONS]

Options:
  --mode {dev|prod}           Run mode (default: dev)
  --host TEXT                 Bind host (default: 0.0.0.0)
  --port INTEGER              Bind port (default: 8000)
  --workers INTEGER           Number of worker processes (default: auto)
  --reload                    Auto-reload on code changes (dev only)
  --log-level {debug|info|warning|error}
  --config FILE               Configuration file path

Examples:
  pyexecmd backend                    # Start dev server on 0.0.0.0:8000
  pyexecmd backend --mode prod        # Start production server
  pyexecmd backend --port 8080        # Custom port
```

**Implementation:**

```python
# pymd/cli.py (extended)

def backend_command(args):
    """Start multi-user backend server"""
    try:
        # Import backend dependencies
        from pymd_backend.app.main import create_app
        import uvicorn

        # Load configuration
        config = load_backend_config(args.config)

        # Create FastAPI application
        app = create_app(config)

        # Production settings
        if args.mode == 'prod':
            uvicorn.run(
                "pymd_backend.app.main:app",
                host=args.host,
                port=args.port,
                workers=args.workers or cpu_count(),
                log_level=args.log_level,
                access_log=True,
                server_header=False,
                proxy_headers=True
            )
        else:
            # Development settings
            uvicorn.run(
                app,
                host=args.host,
                port=args.port,
                reload=args.reload,
                log_level=args.log_level or "debug"
            )

    except ImportError:
        print("Backend dependencies not installed.")
        print("Install with: pip install pyexecmd[backend]")
        return 1
```

### Process Management for Multi-User Support

**Architecture Pattern: Microservices with Shared-Nothing**

```
┌────────────────────────────────────────────────────────────────────┐
│                     Load Balancer (Nginx / ALB)                    │
└─────────────┬──────────────────────────────────────────────────────┘
              │
              ├─────────────────────────────────────────────────┐
              │                                                 │
┌─────────────▼──────────┐  ┌────────────────────┐  ┌──────────▼──────┐
│  API Instance 1        │  │  API Instance 2    │  │  API Instance N │
│  (FastAPI + Uvicorn)   │  │  (FastAPI)         │  │  (FastAPI)      │
│                        │  │                    │  │                 │
│  - Stateless           │  │  - Stateless       │  │  - Stateless    │
│  - WebSocket gateway   │  │  - WebSocket       │  │  - WebSocket    │
└────────┬───────────────┘  └─────────┬──────────┘  └────────┬────────┘
         │                            │                       │
         │                  ┌─────────▼───────────┐          │
         │                  │  Redis Pub/Sub      │          │
         └──────────────────┤  (WebSocket sync)   ├──────────┘
                            └─────────────────────┘
                                      │
                            ┌─────────▼───────────┐
                            │  Redis Job Queue    │
                            └─────────┬───────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
┌─────────────▼──────┐  ┌────────────▼─────────┐  ┌─────────▼────────┐
│  Execution Worker  │  │  Execution Worker    │  │  Execution Worker│
│  (Celery + Docker) │  │  (Celery + Docker)   │  │  (Celery)        │
│                    │  │                      │  │                  │
│  - Sandboxed exec  │  │  - Sandboxed exec    │  │  - Sandboxed     │
│  - Resource limits │  │  - Resource limits   │  │  - Resource      │
│  - Timeout control │  │  - Timeout control   │  │  - Timeout       │
└────────────────────┘  └──────────────────────┘  └──────────────────┘
```

**Process Isolation Strategies:**

1. **API Servers**:
   - Stateless workers (scale horizontally)
   - No code execution (security boundary)
   - Handle HTTP/WebSocket connections
   - Session data in Redis

2. **Execution Workers**:
   - **Container-based isolation** (Docker containers)
   - **Resource limits**: CPU, memory, disk I/O
   - **Network restrictions**: No external network access
   - **Timeout enforcement**: Kill long-running processes
   - **User namespace isolation**: Non-root execution

**Multi-User Resource Allocation:**

```python
# Core execution configuration
EXECUTION_LIMITS = {
    'free_tier': {
        'cpu_limit': '0.5',              # 50% of one CPU
        'memory_limit': '512m',          # 512 MB RAM
        'timeout': 30,                   # 30 seconds
        'concurrent_executions': 2,       # Max concurrent
        'disk_quota': '100m'             # 100 MB disk
    },
    'pro_tier': {
        'cpu_limit': '2.0',
        'memory_limit': '2g',
        'timeout': 300,                  # 5 minutes
        'concurrent_executions': 10,
        'disk_quota': '1g'
    }
}

# User-level resource tracking
class ResourceManager:
    async def allocate_execution_slot(self, user_id: str, tier: str):
        """Allocate execution resources for user"""
        # Check current usage
        current = await self.get_user_usage(user_id)
        limits = EXECUTION_LIMITS[tier]

        if current >= limits['concurrent_executions']:
            raise ResourceExhaustedError("Concurrent execution limit reached")

        # Reserve slot in Redis
        await self.redis.incr(f"user:{user_id}:active_executions")

    async def release_execution_slot(self, user_id: str):
        """Release execution resources"""
        await self.redis.decr(f"user:{user_id}:active_executions")
```

### WebSocket vs REST Considerations

**Real-time Features Requiring WebSocket:**

1. **Live Collaborative Editing** (future)
   - Operational Transformation (OT) or CRDT for conflict resolution
   - Sub-second latency requirements

2. **Code Execution Progress**
   - Real-time output streaming
   - Progress updates (0-100%)
   - Step-by-step execution feedback

3. **Presence Indicators**
   - Who's viewing/editing a document
   - User cursor positions (advanced collaboration)

4. **Notifications**
   - Document share events
   - System alerts

**REST for Everything Else:**

1. **Document CRUD**: Create, read, update, delete documents
2. **User Profile**: User settings, preferences
3. **Authentication**: Login, logout, token refresh
4. **Export Operations**: HTML, Markdown, PDF generation
5. **Search**: Document search queries

**Hybrid Architecture Decision:**

```
┌──────────────────────────────────────────────────────────────┐
│                      Frontend Client                         │
│                                                              │
│  ┌─────────────────┐                ┌──────────────────┐    │
│  │  REST Client    │                │  Socket.IO       │    │
│  │  (fetch/axios)  │                │  WebSocket       │    │
│  └────────┬────────┘                └─────────┬────────┘    │
│           │                                   │              │
└───────────┼───────────────────────────────────┼──────────────┘
            │                                   │
            │ HTTPS                             │ WSS
            │                                   │
┌───────────▼───────────────────────────────────▼──────────────┐
│                   Backend (FastAPI)                          │
│                                                              │
│  ┌─────────────────┐                ┌──────────────────┐    │
│  │  REST Endpoints │                │  WebSocket       │    │
│  │  @app.get()     │                │  @app.websocket  │    │
│  │  @app.post()    │                │  Socket.IO       │    │
│  └─────────────────┘                └──────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

**WebSocket Event Schema:**

```typescript
// Client → Server
interface ClientEvents {
  'document:subscribe': { documentId: string }
  'document:unsubscribe': { documentId: string }
  'execution:start': { documentId: string, code: string }
  'execution:cancel': { executionId: string }
}

// Server → Client
interface ServerEvents {
  'document:updated': { documentId: string, content: string }
  'execution:progress': { executionId: string, progress: number, message: string }
  'execution:output': { executionId: string, output: string, isError: boolean }
  'execution:complete': { executionId: string, result: ExecutionResult }
  'presence:update': { documentId: string, users: User[] }
  'notification': { type: string, message: string }
}
```

### Background Job Processing

**Celery Architecture:**

```python
# workers/celery_app.py
from celery import Celery

celery_app = Celery(
    'pymd_backend',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,        # 10 minutes hard limit
    task_soft_time_limit=540,   # 9 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100
)

# workers/execution_worker.py
@celery_app.task(bind=True, name='execute_pymd_code')
def execute_pymd_code(self, user_id: str, document_id: str, code: str, tier: str):
    """Execute PyMD code in isolated environment"""

    # Update task state
    self.update_state(state='PROGRESS', meta={'progress': 0, 'message': 'Initializing'})

    # Create isolated Docker container
    container = create_sandboxed_container(user_id, tier)

    try:
        # Copy code to container
        container.put_archive('/workspace', code_archive)

        # Execute code with timeout
        self.update_state(state='PROGRESS', meta={'progress': 25, 'message': 'Executing code'})
        exec_result = container.exec_run(
            cmd='python /workspace/code.py',
            demux=True,
            stream=True
        )

        # Stream output
        output = []
        for chunk in exec_result.output:
            output.append(chunk.decode('utf-8'))
            self.update_state(state='PROGRESS', meta={
                'progress': 50 + len(output),
                'message': 'Processing output'
            })

        # Capture generated files (images, videos)
        self.update_state(state='PROGRESS', meta={'progress': 90, 'message': 'Capturing output files'})
        files = capture_output_files(container)

        return {
            'success': True,
            'output': ''.join(output),
            'files': files
        }

    finally:
        # Always cleanup container
        container.stop()
        container.remove()
```

**Background Job Types:**

1. **Code Execution**: Long-running code execution (primary use case)
2. **Export Generation**: PDF/HTML export for large documents
3. **Cleanup Jobs**: Delete old executions, temporary files
4. **Analytics**: Usage metrics aggregation
5. **Email Notifications**: Document sharing, collaboration invites

### Rate Limiting and Resource Management

**Multi-Level Rate Limiting:**

```python
# middleware/rate_limit.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

# API rate limits by tier
RATE_LIMITS = {
    'anonymous': '10/minute',
    'free': '60/minute',
    'pro': '300/minute',
    'enterprise': '1000/minute'
}

# Endpoint-specific limits
@app.post("/api/v1/execute")
@limiter.limit("5/minute")  # Execution is expensive
async def execute_code(request: Request, ...):
    pass

@app.get("/api/v1/documents")
@limiter.limit("100/minute")  # Reads are cheap
async def list_documents(...):
    pass
```

**Resource Quotas:**

```python
# core/resource_manager.py
class ResourceQuotaManager:
    async def check_quota(self, user_id: str, resource_type: str):
        """Check if user has quota for resource"""

        quota_key = f"quota:{user_id}:{resource_type}:{date.today()}"
        current = await redis.get(quota_key) or 0
        limit = await self.get_user_limit(user_id, resource_type)

        if current >= limit:
            raise QuotaExceededError(f"{resource_type} quota exceeded")

        await redis.incr(quota_key)
        await redis.expire(quota_key, 86400)  # 24 hours

# Resource types
QUOTA_TYPES = {
    'executions_per_day': {'free': 100, 'pro': 1000},
    'storage_mb': {'free': 100, 'pro': 10000},
    'export_count': {'free': 10, 'pro': 100}
}
```

---

## Frontend Architecture

### Next.js Application Structure

```
pymd_frontend/
├── src/
│   ├── app/                           # App Router (Next.js 15)
│   │   ├── (auth)/                    # Route group with auth layout
│   │   │   ├── login/
│   │   │   ├── signup/
│   │   │   └── layout.tsx
│   │   │
│   │   ├── (dashboard)/               # Route group with dashboard layout
│   │   │   ├── documents/
│   │   │   │   ├── page.tsx           # Document list
│   │   │   │   ├── [id]/
│   │   │   │   │   ├── page.tsx       # Document viewer
│   │   │   │   │   └── edit/
│   │   │   │   │       └── page.tsx   # Document editor
│   │   │   │   └── new/
│   │   │   │       └── page.tsx       # Create new document
│   │   │   ├── settings/
│   │   │   │   └── page.tsx
│   │   │   └── layout.tsx
│   │   │
│   │   ├── api/                       # API routes (Next.js API)
│   │   │   └── auth/
│   │   │       └── [...nextauth]/
│   │   │           └── route.ts
│   │   │
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Landing page
│   │   ├── globals.css
│   │   └── providers.tsx              # Context providers
│   │
│   ├── components/                    # React components
│   │   ├── editor/
│   │   │   ├── CodeEditor.tsx         # Monaco editor wrapper
│   │   │   ├── PreviewPane.tsx        # Live preview
│   │   │   ├── EditorToolbar.tsx
│   │   │   └── ExecutionPanel.tsx     # Code execution UI
│   │   ├── documents/
│   │   │   ├── DocumentCard.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   └── DocumentSearch.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   └── ui/                        # Reusable UI components
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Modal.tsx
│   │       └── Spinner.tsx
│   │
│   ├── lib/                           # Core libraries
│   │   ├── api/
│   │   │   ├── client.ts              # API client (axios/fetch wrapper)
│   │   │   ├── documents.ts           # Document API calls
│   │   │   ├── execution.ts           # Execution API calls
│   │   │   └── users.ts               # User API calls
│   │   ├── websocket/
│   │   │   ├── socket.ts              # WebSocket client setup
│   │   │   └── handlers.ts            # Event handlers
│   │   ├── auth/
│   │   │   ├── auth-client.ts         # Auth0 client
│   │   │   └── session.ts             # Session management
│   │   └── utils/
│   │       ├── validators.ts
│   │       └── formatters.ts
│   │
│   ├── hooks/                         # Custom React hooks
│   │   ├── useDocument.ts             # Document state management
│   │   ├── useExecution.ts            # Code execution state
│   │   ├── useWebSocket.ts            # WebSocket connection
│   │   └── useAuth.ts                 # Authentication state
│   │
│   ├── stores/                        # Client state (Zustand)
│   │   ├── documentStore.ts           # Document state
│   │   ├── executionStore.ts          # Execution state
│   │   └── uiStore.ts                 # UI state (modals, toasts)
│   │
│   ├── types/                         # TypeScript types
│   │   ├── api.ts                     # API response types
│   │   ├── document.ts
│   │   ├── execution.ts
│   │   └── user.ts
│   │
│   └── styles/                        # Global styles
│       └── editor.css                 # Editor-specific styles
│
├── public/                            # Static assets
│   ├── images/
│   └── fonts/
│
├── .env.local
├── .env.example
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### State Management Strategy

**Server State (React Query / SWR):**

```typescript
// For data fetched from backend
import { useQuery, useMutation } from '@tanstack/react-query';

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => api.documents.get(documentId),
    staleTime: 30000, // 30 seconds
    refetchOnWindowFocus: true
  });
}

export function useUpdateDocument(documentId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (content: string) => api.documents.update(documentId, content),
    onSuccess: () => {
      queryClient.invalidateQueries(['document', documentId]);
    }
  });
}
```

**Client State (Zustand):**

```typescript
// stores/editorStore.ts
import { create } from 'zustand';

interface EditorState {
  // Editor state
  currentDocument: Document | null;
  editorContent: string;
  isExecuting: boolean;
  executionOutput: string[];

  // Actions
  setDocument: (doc: Document) => void;
  updateContent: (content: string) => void;
  startExecution: () => void;
  addOutput: (output: string) => void;
}

export const useEditorStore = create<EditorState>((set) => ({
  currentDocument: null,
  editorContent: '',
  isExecuting: false,
  executionOutput: [],

  setDocument: (doc) => set({ currentDocument: doc, editorContent: doc.content }),
  updateContent: (content) => set({ editorContent: content }),
  startExecution: () => set({ isExecuting: true, executionOutput: [] }),
  addOutput: (output) => set((state) => ({
    executionOutput: [...state.executionOutput, output]
  }))
}));
```

**Form State (React Hook Form):**

```typescript
// For complex forms
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const documentSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string(),
  isPublic: z.boolean()
});

export function DocumentForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(documentSchema)
  });

  const onSubmit = (data) => {
    // Submit to API
  };

  return <form onSubmit={handleSubmit(onSubmit)}>...</form>;
}
```

### Code Editor Integration

**Monaco Editor Setup:**

```typescript
// components/editor/CodeEditor.tsx
import Editor, { Monaco } from '@monaco-editor/react';
import { useEditorStore } from '@/stores/editorStore';

export function CodeEditor() {
  const { editorContent, updateContent } = useEditorStore();

  const handleEditorMount = (editor: any, monaco: Monaco) => {
    // Register PyMD language
    monaco.languages.register({ id: 'pymd' });

    // Define syntax highlighting
    monaco.languages.setMonarchTokensProvider('pymd', {
      tokenizer: {
        root: [
          [/^#.*$/, 'comment.pymd'],       // Markdown lines
          [/^```$/, 'keyword.pymd'],       // Code block delimiters
          [/^\/\/.*$/, 'comment.ignored'], // Ignored comments
          // ... more rules
        ]
      }
    });

    // Define theme
    monaco.editor.defineTheme('pymd-theme', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment.pymd', foreground: '6A9955' },
        { token: 'keyword.pymd', foreground: 'C586C0' },
      ],
      colors: {}
    });

    // Set keyboard shortcuts
    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
      () => handleSave()
    );

    editor.addCommand(
      monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
      () => handleExecute()
    );
  };

  return (
    <Editor
      language="pymd"
      theme="pymd-theme"
      value={editorContent}
      onChange={(value) => updateContent(value || '')}
      onMount={handleEditorMount}
      options={{
        fontSize: 14,
        lineNumbers: 'on',
        minimap: { enabled: true },
        scrollBeyondLastLine: false,
        wordWrap: 'on',
        tabSize: 4,
        insertSpaces: true
      }}
    />
  );
}
```

---

## Frontend-Backend Integration

### Communication Protocols

**REST API Communication:**

```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (add auth token)
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API methods
export const api = {
  documents: {
    list: () => apiClient.get('/api/v1/documents'),
    get: (id: string) => apiClient.get(`/api/v1/documents/${id}`),
    create: (data: any) => apiClient.post('/api/v1/documents', data),
    update: (id: string, data: any) => apiClient.put(`/api/v1/documents/${id}`, data),
    delete: (id: string) => apiClient.delete(`/api/v1/documents/${id}`)
  },
  execution: {
    execute: (documentId: string, code: string) =>
      apiClient.post('/api/v1/execute', { documentId, code })
  }
};
```

**WebSocket Communication:**

```typescript
// lib/websocket/socket.ts
import { io, Socket } from 'socket.io-client';

class WebSocketManager {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(token: string) {
    this.socket = io(process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000', {
      auth: { token },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000
    });

    this.setupEventHandlers();
  }

  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket error:', error);
      this.reconnectAttempts++;

      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.socket?.close();
      }
    });
  }

  // Subscribe to document updates
  subscribeToDocument(documentId: string, callback: (data: any) => void) {
    this.socket?.emit('document:subscribe', { documentId });
    this.socket?.on(`document:${documentId}:updated`, callback);
  }

  // Subscribe to execution updates
  subscribeToExecution(executionId: string, callbacks: {
    onProgress: (data: any) => void;
    onOutput: (data: any) => void;
    onComplete: (data: any) => void;
  }) {
    this.socket?.on(`execution:${executionId}:progress`, callbacks.onProgress);
    this.socket?.on(`execution:${executionId}:output`, callbacks.onOutput);
    this.socket?.on(`execution:${executionId}:complete`, callbacks.onComplete);
  }

  disconnect() {
    this.socket?.disconnect();
  }
}

export const wsManager = new WebSocketManager();
```

**Real-time Execution Flow:**

```typescript
// hooks/useExecution.ts
export function useExecution(documentId: string) {
  const [isExecuting, setIsExecuting] = useState(false);
  const [output, setOutput] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);

  const execute = async (code: string) => {
    setIsExecuting(true);
    setOutput([]);
    setProgress(0);

    try {
      // Start execution via REST API
      const { executionId } = await api.execution.execute(documentId, code);

      // Subscribe to WebSocket updates
      wsManager.subscribeToExecution(executionId, {
        onProgress: (data) => {
          setProgress(data.progress);
        },
        onOutput: (data) => {
          setOutput(prev => [...prev, data.output]);
        },
        onComplete: (data) => {
          setIsExecuting(false);
          setProgress(100);
        }
      });
    } catch (error) {
      setIsExecuting(false);
      console.error('Execution failed:', error);
    }
  };

  return { isExecuting, output, progress, execute };
}
```

### API Contract (OpenAPI)

```yaml
openapi: 3.0.0
info:
  title: PyMD Backend API
  version: 1.0.0

paths:
  /api/v1/documents:
    get:
      summary: List user documents
      security:
        - bearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: List of documents
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DocumentList'

    post:
      summary: Create new document
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/DocumentCreate'
      responses:
        '201':
          description: Document created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Document'

  /api/v1/documents/{documentId}:
    get:
      summary: Get document by ID
      security:
        - bearerAuth: []
      parameters:
        - name: documentId
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: Document details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Document'
        '404':
          description: Document not found

  /api/v1/execute:
    post:
      summary: Execute PyMD code
      security:
        - bearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                documentId:
                  type: string
                  format: uuid
                code:
                  type: string
              required:
                - documentId
                - code
      responses:
        '202':
          description: Execution started
          content:
            application/json:
              schema:
                type: object
                properties:
                  executionId:
                    type: string
                    format: uuid
                  status:
                    type: string
                    enum: [queued, running]

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Document:
      type: object
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
        content:
          type: string
        createdAt:
          type: string
          format: date-time
        updatedAt:
          type: string
          format: date-time
        ownerId:
          type: string
          format: uuid
        isPublic:
          type: boolean

    DocumentCreate:
      type: object
      properties:
        title:
          type: string
          minLength: 1
          maxLength: 100
        content:
          type: string
        isPublic:
          type: boolean
          default: false
      required:
        - title

    DocumentList:
      type: object
      properties:
        documents:
          type: array
          items:
            $ref: '#/components/schemas/Document'
        pagination:
          type: object
          properties:
            page:
              type: integer
            limit:
              type: integer
            total:
              type: integer
```

---

## Scalability Considerations

### Horizontal Scaling Design

**Stateless Application Tier:**

All API servers are stateless, allowing easy horizontal scaling:

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pymd-api
spec:
  replicas: 3  # Scale to N instances
  selector:
    matchLabels:
      app: pymd-api
  template:
    metadata:
      labels:
        app: pymd-api
    spec:
      containers:
      - name: api
        image: pymd-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pymd-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: pymd-secrets
              key: redis-url
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: pymd-api-service
spec:
  selector:
    app: pymd-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Auto-Scaling Configuration:**

```yaml
# kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: pymd-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: pymd-api
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # 5 minutes
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
```

### Multi-User Resource Isolation

**Container-Based Isolation:**

```python
# core/sandbox.py
import docker
from typing import Dict

class SandboxManager:
    def __init__(self):
        self.docker_client = docker.from_env()

    def create_execution_container(
        self,
        user_id: str,
        tier: str,
        code: str
    ) -> docker.models.containers.Container:
        """Create isolated container for code execution"""

        limits = EXECUTION_LIMITS[tier]

        container = self.docker_client.containers.run(
            image='pymd-executor:latest',
            command='python /workspace/execute.py',

            # Resource limits
            cpu_quota=int(float(limits['cpu_limit']) * 100000),
            cpu_period=100000,
            mem_limit=limits['memory_limit'],
            memswap_limit=limits['memory_limit'],  # Disable swap

            # Security
            security_opt=['no-new-privileges'],
            cap_drop=['ALL'],
            cap_add=['CHOWN', 'SETUID', 'SETGID'],  # Minimal capabilities
            read_only=True,  # Read-only root filesystem

            # Network isolation
            network_mode='none',  # No network access

            # User namespace
            user='1000:1000',  # Non-root user

            # Volumes (ephemeral)
            volumes={
                f'/tmp/pymd/{user_id}': {
                    'bind': '/workspace',
                    'mode': 'rw'
                }
            },

            # Detached execution
            detach=True,
            remove=False  # Manual cleanup for file extraction
        )

        return container

    async def execute_with_timeout(
        self,
        container: docker.models.containers.Container,
        timeout: int
    ) -> Dict:
        """Execute code with timeout enforcement"""

        try:
            # Wait for container with timeout
            result = container.wait(timeout=timeout)

            # Get logs
            logs = container.logs(stdout=True, stderr=True)

            # Extract output files
            files = self.extract_output_files(container)

            return {
                'success': result['StatusCode'] == 0,
                'output': logs.decode('utf-8'),
                'files': files
            }

        except docker.errors.DockerException as e:
            # Timeout or other error
            container.kill()
            raise ExecutionTimeoutError(f"Execution timed out after {timeout}s")

        finally:
            # Always cleanup
            container.stop()
            container.remove()
```

**Resource Quota Tracking:**

```python
# services/resource_service.py
from datetime import datetime, timedelta

class ResourceTrackingService:
    async def track_execution(
        self,
        user_id: str,
        execution_id: str,
        resources_used: Dict
    ):
        """Track resource usage for billing and quotas"""

        await self.db.execute(
            """
            INSERT INTO resource_usage (
                user_id, execution_id, cpu_seconds, memory_mb_seconds,
                storage_mb, timestamp
            ) VALUES ($1, $2, $3, $4, $5, $6)
            """,
            user_id, execution_id,
            resources_used['cpu_seconds'],
            resources_used['memory_mb_seconds'],
            resources_used['storage_mb'],
            datetime.utcnow()
        )

    async def get_user_usage_today(self, user_id: str) -> Dict:
        """Get user's resource usage for today"""

        today = datetime.utcnow().date()

        result = await self.db.fetchrow(
            """
            SELECT
                COUNT(*) as execution_count,
                SUM(cpu_seconds) as total_cpu_seconds,
                SUM(memory_mb_seconds) as total_memory_mb_seconds,
                SUM(storage_mb) as total_storage_mb
            FROM resource_usage
            WHERE user_id = $1
              AND timestamp >= $2
              AND timestamp < $3
            """,
            user_id,
            datetime.combine(today, datetime.min.time()),
            datetime.combine(today + timedelta(days=1), datetime.min.time())
        )

        return dict(result)

    async def check_quota_available(self, user_id: str, tier: str) -> bool:
        """Check if user has quota available"""

        usage = await self.get_user_usage_today(user_id)
        limits = TIER_LIMITS[tier]

        return (
            usage['execution_count'] < limits['executions_per_day'] and
            usage['total_storage_mb'] < limits['storage_mb']
        )
```

### Caching Strategy

**Multi-Level Caching:**

```
┌────────────────────────────────────────────────────────────┐
│                   Client (Browser)                         │
│  - React Query cache (30s-5m)                             │
│  - localStorage for preferences                            │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│                   CDN / Edge Cache                         │
│  - Static assets (HTML, JS, CSS, images)                  │
│  - Public documents (Cache-Control: public, max-age=3600) │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│              Application Cache (Redis)                     │
│  - Session data (TTL: 24h)                                │
│  - Rendered HTML (TTL: 5m)                                │
│  - Code execution results (TTL: 1h)                       │
│  - User preferences (TTL: 1h)                             │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────▼───────────────────────────────────┐
│           Database Query Cache (PostgreSQL)                │
│  - Prepared statements                                     │
│  - Connection pooling                                      │
└────────────────────────────────────────────────────────────┘
```

**Redis Caching Implementation:**

```python
# core/cache.py
from typing import Optional, Any
import json
import hashlib

class CacheManager:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_cached_render(self, content_hash: str) -> Optional[str]:
        """Get cached rendered HTML"""
        key = f"render:{content_hash}"
        cached = await self.redis.get(key)
        return cached.decode('utf-8') if cached else None

    async def set_cached_render(self, content_hash: str, html: str, ttl: int = 300):
        """Cache rendered HTML (5 minutes)"""
        key = f"render:{content_hash}"
        await self.redis.setex(key, ttl, html)

    async def get_cached_execution(self, code_hash: str) -> Optional[Dict]:
        """Get cached execution result"""
        key = f"execution:{code_hash}"
        cached = await self.redis.get(key)
        return json.loads(cached) if cached else None

    async def set_cached_execution(self, code_hash: str, result: Dict, ttl: int = 3600):
        """Cache execution result (1 hour)"""
        key = f"execution:{code_hash}"
        await self.redis.setex(key, ttl, json.dumps(result))

    def generate_content_hash(self, content: str) -> str:
        """Generate hash for content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
```

### Database Scaling

**Read Replicas:**

```python
# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    def __init__(self):
        # Primary database (writes)
        self.primary_engine = create_async_engine(
            os.getenv('DATABASE_PRIMARY_URL'),
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True
        )

        # Read replica (reads)
        self.replica_engine = create_async_engine(
            os.getenv('DATABASE_REPLICA_URL'),
            pool_size=30,
            max_overflow=20,
            pool_pre_ping=True
        )

        self.primary_session = sessionmaker(
            self.primary_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        self.replica_session = sessionmaker(
            self.replica_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    def get_write_session(self) -> AsyncSession:
        """Get session for write operations"""
        return self.primary_session()

    def get_read_session(self) -> AsyncSession:
        """Get session for read operations"""
        return self.replica_session()

# Usage in repository
class DocumentRepository:
    async def get_document(self, document_id: str) -> Document:
        """Read from replica"""
        async with db.get_read_session() as session:
            result = await session.execute(
                select(Document).where(Document.id == document_id)
            )
            return result.scalar_one_or_none()

    async def create_document(self, document: Document) -> Document:
        """Write to primary"""
        async with db.get_write_session() as session:
            session.add(document)
            await session.commit()
            await session.refresh(document)
            return document
```

**Connection Pooling:**

```python
# Configuration
DATABASE_CONFIG = {
    'pool_size': 20,           # Connections kept open
    'max_overflow': 10,        # Additional connections under load
    'pool_timeout': 30,        # Wait 30s for connection
    'pool_recycle': 3600,      # Recycle connections every hour
    'pool_pre_ping': True,     # Check connection before use
    'echo': False,             # Disable SQL logging in prod
    'future': True             # SQLAlchemy 2.0 style
}
```

---

## Security Architecture

### Auth0 Integration

**Authentication Flow (Authorization Code Flow with PKCE):**

```
┌──────────┐                                                    ┌──────────┐
│  Client  │                                                    │  Auth0   │
│(Browser) │                                                    │          │
└────┬─────┘                                                    └────┬─────┘
     │                                                               │
     │  1. Initiate Login                                           │
     ├──────────────────────────────────────────────────────────────►
     │     GET /authorize?                                          │
     │         client_id=...&                                       │
     │         redirect_uri=...&                                    │
     │         response_type=code&                                  │
     │         code_challenge=...&                                  │
     │         code_challenge_method=S256                           │
     │                                                               │
     │  2. Login UI                                                 │
     ◄──────────────────────────────────────────────────────────────┤
     │     (User enters credentials)                                │
     │                                                               │
     │  3. Authorization Code                                       │
     ◄──────────────────────────────────────────────────────────────┤
     │     Redirect: callback?code=AUTH_CODE                        │
     │                                                               │
     │  4. Exchange Code for Tokens                                 │
     ├──────────────────────────────────────────────────────────────►
     │     POST /oauth/token                                        │
     │         code=AUTH_CODE&                                      │
     │         code_verifier=...&                                   │
     │         client_id=...&                                       │
     │         grant_type=authorization_code                        │
     │                                                               │
     │  5. Tokens                                                   │
     ◄──────────────────────────────────────────────────────────────┤
     │     {                                                        │
     │       "access_token": "...",                                 │
     │       "id_token": "...",                                     │
     │       "refresh_token": "...",                                │
     │       "expires_in": 86400                                    │
     │     }                                                        │
     │                                                               │
```

**Next.js Auth Setup:**

```typescript
// lib/auth/auth-client.ts
import { Auth0Client } from '@auth0/auth0-spa-js';

const auth0Client = new Auth0Client({
  domain: process.env.NEXT_PUBLIC_AUTH0_DOMAIN!,
  clientId: process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID!,
  authorizationParams: {
    redirect_uri: typeof window !== 'undefined'
      ? window.location.origin + '/callback'
      : '',
    audience: process.env.NEXT_PUBLIC_AUTH0_AUDIENCE,
    scope: 'openid profile email offline_access'
  },
  cacheLocation: 'localstorage',
  useRefreshTokens: true
});

export async function login() {
  await auth0Client.loginWithRedirect();
}

export async function handleCallback() {
  const result = await auth0Client.handleRedirectCallback();
  return result;
}

export async function getAccessToken() {
  return await auth0Client.getTokenSilently();
}

export async function logout() {
  await auth0Client.logout({
    logoutParams: {
      returnTo: window.location.origin
    }
  });
}

// Context Provider
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const isAuth = await auth0Client.isAuthenticated();
      setIsAuthenticated(isAuth);

      if (isAuth) {
        const user = await auth0Client.getUser();
        setUser(user);
      }

      setIsLoading(false);
    })();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
```

**Backend JWT Validation:**

```python
# middleware/auth_middleware.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

security = HTTPBearer()

class AuthMiddleware:
    def __init__(self):
        self.auth0_domain = os.getenv('AUTH0_DOMAIN')
        self.api_audience = os.getenv('AUTH0_AUDIENCE')
        self.jwks_url = f'https://{self.auth0_domain}/.well-known/jwks.json'
        self._jwks_client = None

    async def get_jwks_client(self):
        """Get JWKS (JSON Web Key Set) for token verification"""
        if not self._jwks_client:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.jwks_url)
                self._jwks_client = response.json()
        return self._jwks_client

    async def verify_token(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> Dict:
        """Verify JWT token and return claims"""

        token = credentials.credentials

        try:
            # Decode token header to get key ID
            unverified_header = jwt.get_unverified_header(token)

            # Get signing key from JWKS
            jwks = await self.get_jwks_client()
            rsa_key = self._get_rsa_key(jwks, unverified_header['kid'])

            if not rsa_key:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to find appropriate key"
                )

            # Verify token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=['RS256'],
                audience=self.api_audience,
                issuer=f'https://{self.auth0_domain}/'
            )

            return payload

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )

    def _get_rsa_key(self, jwks: Dict, kid: str) -> Dict:
        """Extract RSA key from JWKS"""
        for key in jwks['keys']:
            if key['kid'] == kid:
                return {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        return {}

# Dependency for protected routes
auth_middleware = AuthMiddleware()

async def get_current_user(
    token_payload: Dict = Depends(auth_middleware.verify_token)
) -> str:
    """Get current user ID from token"""
    return token_payload.get('sub')

# Usage in endpoint
@app.get("/api/v1/documents")
async def list_documents(
    user_id: str = Depends(get_current_user)
):
    # user_id is verified and available
    documents = await document_service.get_user_documents(user_id)
    return documents
```

### Session Management

**Redis-Based Sessions:**

```python
# core/session.py
from datetime import timedelta
import uuid

class SessionManager:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.session_ttl = timedelta(days=7)  # 7 days

    async def create_session(self, user_id: str, metadata: Dict) -> str:
        """Create new session"""
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"

        session_data = {
            'user_id': user_id,
            'created_at': datetime.utcnow().isoformat(),
            **metadata
        }

        await self.redis.setex(
            session_key,
            self.session_ttl,
            json.dumps(session_data)
        )

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        session_key = f"session:{session_id}"
        data = await self.redis.get(session_key)

        if not data:
            return None

        # Extend session TTL on access
        await self.redis.expire(session_key, self.session_ttl)

        return json.loads(data)

    async def delete_session(self, session_id: str):
        """Delete session (logout)"""
        session_key = f"session:{session_id}"
        await self.redis.delete(session_key)
```

### CORS and Security Headers

**FastAPI CORS Configuration:**

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # Development
        "https://pymd.example.com",           # Production
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
    max_age=3600,  # Cache preflight for 1 hour
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' wss: https:;"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    return response

# Trusted host middleware (prevent host header attacks)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["pymd.example.com", "*.pymd.example.com", "localhost"]
)
```

### API Authentication/Authorization Flow

**Role-Based Access Control (RBAC):**

```python
# models/user.py
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

class Permission(str, Enum):
    DOCUMENT_CREATE = "document:create"
    DOCUMENT_READ = "document:read"
    DOCUMENT_UPDATE = "document:update"
    DOCUMENT_DELETE = "document:delete"
    DOCUMENT_SHARE = "document:share"
    CODE_EXECUTE = "code:execute"

# Role permissions mapping
ROLE_PERMISSIONS = {
    UserRole.ADMIN: [p for p in Permission],  # All permissions
    UserRole.USER: [
        Permission.DOCUMENT_CREATE,
        Permission.DOCUMENT_READ,
        Permission.DOCUMENT_UPDATE,
        Permission.DOCUMENT_DELETE,
        Permission.DOCUMENT_SHARE,
        Permission.CODE_EXECUTE,
    ],
    UserRole.VIEWER: [
        Permission.DOCUMENT_READ,
    ]
}

# Authorization decorator
def require_permission(permission: Permission):
    async def permission_checker(
        user_id: str = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ):
        # Get user role
        user = await db.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check permission
        user_permissions = ROLE_PERMISSIONS.get(user.role, [])

        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Missing required permission: {permission}"
            )

        return user

    return permission_checker

# Usage
@app.post("/api/v1/documents")
async def create_document(
    document: DocumentCreate,
    user: User = Depends(require_permission(Permission.DOCUMENT_CREATE))
):
    # User has permission, proceed
    return await document_service.create(user.id, document)
```

**Document-Level Permissions:**

```python
# models/document.py
class DocumentPermission(Base):
    __tablename__ = "document_permissions"

    id = Column(UUID, primary_key=True)
    document_id = Column(UUID, ForeignKey("documents.id"))
    user_id = Column(UUID, ForeignKey("users.id"))
    permission = Column(Enum(Permission))
    granted_at = Column(DateTime, default=datetime.utcnow)
    granted_by = Column(UUID, ForeignKey("users.id"))

# Authorization check
async def check_document_access(
    document_id: str,
    user_id: str,
    required_permission: Permission,
    db: AsyncSession
) -> bool:
    # Check if user is document owner
    document = await db.get(Document, document_id)
    if document.owner_id == user_id:
        return True

    # Check explicit permissions
    permission = await db.execute(
        select(DocumentPermission).where(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id,
            DocumentPermission.permission == required_permission
        )
    )

    return permission.scalar_one_or_none() is not None
```

---

## Infrastructure & Deployment

### Containerization

**Backend Dockerfile:**

```dockerfile
# docker/Dockerfile
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pymd_backend /app/pymd_backend
COPY pymd /app/pymd

# Create non-root user
RUN useradd -m -u 1000 pymd && \
    chown -R pymd:pymd /app

USER pymd

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "pymd_backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Execution Worker Dockerfile:**

```dockerfile
# docker/Dockerfile.executor
FROM python:3.11-slim

# Minimal Python environment for code execution
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install common data science packages
RUN pip install --no-cache-dir \
    numpy==1.24.3 \
    pandas==2.0.3 \
    matplotlib==3.7.2 \
    scipy==1.11.1

# Create workspace
WORKDIR /workspace

# Create non-root user
RUN useradd -m -u 1000 executor && \
    chown -R executor:executor /workspace

USER executor

# Default command
CMD ["python", "/workspace/execute.py"]
```

**Docker Compose (Development):**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: pymd
      POSTGRES_USER: pymd
      POSTGRES_PASSWORD: pymd_dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U pymd"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://pymd:pymd_dev_password@postgres:5432/pymd
      REDIS_URL: redis://redis:6379/0
      AUTH0_DOMAIN: ${AUTH0_DOMAIN}
      AUTH0_AUDIENCE: ${AUTH0_AUDIENCE}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./pymd_backend:/app/pymd_backend
      - ./pymd:/app/pymd
    command: uvicorn pymd_backend.app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build:
      context: .
      dockerfile: docker/Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://pymd:pymd_dev_password@postgres:5432/pymd
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./pymd_backend:/app/pymd_backend
      - ./pymd:/app/pymd
      - /var/run/docker.sock:/var/run/docker.sock  # Docker-in-Docker for execution
    command: celery -A pymd_backend.workers.celery_app worker --loglevel=info

  frontend:
    build:
      context: ./pymd_frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NEXT_PUBLIC_WS_URL: ws://localhost:8000
      NEXT_PUBLIC_AUTH0_DOMAIN: ${NEXT_PUBLIC_AUTH0_DOMAIN}
      NEXT_PUBLIC_AUTH0_CLIENT_ID: ${NEXT_PUBLIC_AUTH0_CLIENT_ID}
    volumes:
      - ./pymd_frontend/src:/app/src
    command: pnpm dev

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment

**Full Kubernetes Architecture:**

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: pymd-production
---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: pymd-config
  namespace: pymd-production
data:
  LOG_LEVEL: "info"
  WORKERS_PER_CORE: "2"
---
# kubernetes/secrets.yaml (encrypted with sealed-secrets or external secrets operator)
apiVersion: v1
kind: Secret
metadata:
  name: pymd-secrets
  namespace: pymd-production
type: Opaque
data:
  database-url: <base64-encoded>
  redis-url: <base64-encoded>
  auth0-domain: <base64-encoded>
  auth0-audience: <base64-encoded>
---
# kubernetes/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pymd-backend
  namespace: pymd-production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pymd-backend
  template:
    metadata:
      labels:
        app: pymd-backend
    spec:
      containers:
      - name: backend
        image: pymd-backend:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pymd-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: pymd-secrets
              key: redis-url
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: pymd-config
              key: LOG_LEVEL
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2000m"
            memory: "2Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
---
# kubernetes/worker-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pymd-worker
  namespace: pymd-production
spec:
  replicas: 5
  selector:
    matchLabels:
      app: pymd-worker
  template:
    metadata:
      labels:
        app: pymd-worker
    spec:
      containers:
      - name: worker
        image: pymd-backend:v1.0.0
        command: ["celery", "-A", "pymd_backend.workers.celery_app", "worker", "--loglevel=info"]
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: pymd-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: pymd-secrets
              key: redis-url
        volumeMounts:
        - name: docker-sock
          mountPath: /var/run/docker.sock
        resources:
          requests:
            cpu: "1000m"
            memory: "1Gi"
          limits:
            cpu: "4000m"
            memory: "4Gi"
      volumes:
      - name: docker-sock
        hostPath:
          path: /var/run/docker.sock
---
# kubernetes/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: pymd-backend-service
  namespace: pymd-production
spec:
  selector:
    app: pymd-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pymd-ingress
  namespace: pymd-production
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.pymd.example.com
    secretName: pymd-tls-secret
  rules:
  - host: api.pymd.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: pymd-backend-service
            port:
              number: 80
```

---

## Observability & Monitoring

### Monitoring Stack

**Prometheus Metrics:**

```python
# middleware/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

active_executions = Gauge(
    'active_code_executions',
    'Number of active code executions'
)

execution_duration_seconds = Histogram(
    'code_execution_duration_seconds',
    'Code execution duration',
    ['tier']
)

# Middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response

# Expose metrics endpoint
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

@app.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### Logging Strategy

**Structured Logging:**

```python
# core/logger.py
import structlog
import logging

def configure_logging():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

logger = structlog.get_logger()

# Usage
logger.info(
    "code_execution_started",
    user_id=user_id,
    document_id=document_id,
    tier=tier
)
```

---

## Architecture Decision Records

### ADR-001: Backend Framework Selection

**Status:** Accepted

**Context:** Need to choose Python web framework for multi-user backend.

**Decision:** Use FastAPI

**Rationale:**
- Native async/await support for high concurrency
- Automatic OpenAPI documentation
- Type safety with Pydantic
- Best performance among Python frameworks
- Native WebSocket support

**Consequences:**
- Team needs to learn async Python patterns
- Better performance and scalability
- Type-safe API contracts

### ADR-002: Execution Isolation Strategy

**Status:** Accepted

**Context:** Need to securely execute untrusted Python code from multiple users.

**Decision:** Use Docker containers for execution isolation

**Rationale:**
- Strong security boundaries (namespaces, cgroups)
- Resource limits (CPU, memory, disk)
- Network isolation
- Mature ecosystem and tooling

**Alternatives Considered:**
- **Process-based isolation**: Weaker security
- **VMs**: Too heavy, slow startup
- **WASM/Pyodide**: Limited Python package support

**Consequences:**
- Requires Docker on execution workers
- Slightly higher latency (container creation)
- Strong security guarantees

### ADR-003: Real-time Communication Protocol

**Status:** Accepted

**Context:** Need real-time updates for code execution progress and collaboration features.

**Decision:** Use WebSocket (Socket.IO) for real-time, REST for everything else

**Rationale:**
- WebSocket ideal for bi-directional real-time communication
- REST better for CRUD operations (caching, CDN compatibility)
- Clear separation of concerns

**Consequences:**
- Two communication channels to maintain
- Need connection management and reconnection logic
- Better user experience for real-time features

### ADR-004: Database Choice

**Status:** Accepted

**Context:** Need primary database for user data, documents, and metadata.

**Decision:** Use PostgreSQL

**Rationale:**
- ACID compliance for data integrity
- JSON support for flexible schemas
- Full-text search capabilities
- Mature replication and scaling options
- Strong Python ecosystem support

**Alternatives Considered:**
- **MongoDB**: Weaker consistency guarantees
- **MySQL**: Less feature-rich than PostgreSQL

**Consequences:**
- SQL expertise required
- Excellent data integrity
- Good scaling options

---

## Summary

This architecture plan provides a comprehensive foundation for building PyMD as a multi-user web platform. Key architectural highlights:

1. **Clean Separation**: API tier, execution tier, and data tier are clearly separated
2. **Security-First**: Container isolation, Auth0 integration, comprehensive authorization
3. **Scalability**: Horizontal scaling for API servers, isolated execution workers
4. **Modern Stack**: FastAPI (backend), Next.js (frontend), PostgreSQL (data)
5. **Real-time Capable**: WebSocket support for live updates and collaboration
6. **Production-Ready**: Kubernetes deployment, monitoring, observability

**Next Steps:**
1. Review and approve this architecture plan
2. Set up development environment (Docker Compose)
3. Implement core backend services (auth, documents, execution)
4. Develop frontend components (editor, preview, document management)
5. Integration testing and security audits
6. Gradual rollout with feature flags

**Estimated Timeline:**
- Phase 1 (Backend Core): 4-6 weeks
- Phase 2 (Frontend Core): 4-6 weeks
- Phase 3 (Integration & Testing): 2-4 weeks
- Phase 4 (Production Deployment): 2 weeks

**Total:** 12-18 weeks for MVP
