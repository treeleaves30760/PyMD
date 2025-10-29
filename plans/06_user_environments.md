# User Environment Management System

**Plan ID**: 06
**Status**: Phase 1-2 Complete ✅ | Phase 3-5 Pending
**Priority**: High
**Dependencies**: 01 (Architecture), 02 (API), 03 (Schema), 04 (Auth0)

---

## Overview

Implement per-user isolated Python environments with Docker containerization, allowing users to install custom packages via pip while maintaining security and resource isolation.

## Problem Statement

Current PyMD executes code in a shared Python process using `exec()`:
- **Security Risk**: No isolation between users or from server
- **No Custom Packages**: Users cannot install dependencies
- **Resource Issues**: No CPU/memory limits
- **State Leakage**: Variables can persist inappropriately

## Solution Architecture

### High-Level Design

```
User → API → Environment Service → Docker Executor → Isolated Container
                                                        ├─ User Volume
                                                        ├─ Resource Limits
                                                        └─ No Network (by default)
```

### Key Components

1. **User Environments** - Each user can create multiple named environments
2. **Docker Isolation** - On-demand containers with resource limits
3. **Volume Persistence** - Docker volumes store installed packages
4. **Package Management** - pip install/uninstall with quota enforcement
5. **Quota System** - FREE vs PRO tier limits

---

## Phase 1: Core Infrastructure ✅ COMPLETE

### Database Schema

**Tables Created:**

```sql
-- User environments
CREATE TABLE user_environments (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    python_version VARCHAR(20) DEFAULT '3.11',
    volume_name VARCHAR(255) UNIQUE,
    status VARCHAR(20),  -- active, creating, error, deleted
    total_size_bytes BIGINT DEFAULT 0,
    package_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    UNIQUE(user_id, name)
);

-- Installed packages tracking
CREATE TABLE environment_packages (
    id UUID PRIMARY KEY,
    environment_id UUID REFERENCES user_environments(id),
    package_name VARCHAR(255) NOT NULL,
    version VARCHAR(100),
    size_bytes BIGINT,
    installed_at TIMESTAMP,
    UNIQUE(environment_id, package_name)
);

-- Execution history
CREATE TABLE environment_executions (
    id UUID PRIMARY KEY,
    environment_id UUID REFERENCES user_environments(id),
    document_id UUID REFERENCES documents(id),
    status VARCHAR(20),  -- queued, running, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_ms INTEGER,
    error_message TEXT
);
```

**Migration**: `20251029_0001_add_user_environments.py`

### Docker Executor

**Image**: `pymd-executor:latest` (410MB)

**Features:**
- Python 3.11-slim base
- Non-root user (executor, UID 1000)
- Pre-installed: pip, setuptools, wheel, gcc, g++
- execute.py script for JSON-formatted execution
- Security hardening (no network, resource limits)

**Tests:** 16/16 passed ✅

### Services Implemented

**DockerExecutorService** (`app/services/docker_executor_service.py`):
- Container lifecycle management
- Volume creation/deletion
- Code execution with resource limits
- Package installation
- Cleanup utilities

**EnvironmentService** (`app/services/environment_service.py`):
- Environment CRUD operations
- Quota enforcement
- Default environment management
- Statistics tracking

### Configuration

```python
# Environment Limits
MAX_ENVIRONMENTS_FREE = 3
MAX_ENVIRONMENTS_PRO = 10

# Package Limits
MAX_PACKAGES_FREE = 50
MAX_PACKAGES_PRO = 500
MAX_ENVIRONMENT_SIZE_FREE = 1GB
MAX_ENVIRONMENT_SIZE_PRO = 10GB

# Execution Limits
EXECUTION_TIMEOUT_FREE = 30s
EXECUTION_TIMEOUT_PRO = 300s
EXECUTION_CPU_LIMIT_FREE = 0.5 cores
EXECUTION_CPU_LIMIT_PRO = 2.0 cores
EXECUTION_MEMORY_LIMIT_FREE = 512MB
EXECUTION_MEMORY_LIMIT_PRO = 2GB
```

---

## Phase 2: Environment Management API ✅ COMPLETE

### API Endpoints

#### Environment CRUD

```
POST   /api/v1/environments       ✅ Implemented
GET    /api/v1/environments       ✅ Implemented
GET    /api/v1/environments/{id}  ✅ Implemented
DELETE /api/v1/environments/{id}  ✅ Implemented
POST   /api/v1/environments/{id}/reset  ✅ Implemented
PATCH  /api/v1/environments/{id}  ✅ Implemented
GET    /api/v1/environments/stats ✅ Implemented
```

#### Request/Response Examples

**Create Environment:**
```json
POST /api/v1/environments
{
  "name": "data-science",
  "python_version": "3.11"
}

Response 201:
{
  "id": "uuid",
  "name": "data-science",
  "python_version": "3.11",
  "volume_name": "pymd-env-{user_id}-data-science",
  "status": "active",
  "package_count": 0,
  "total_size_bytes": 0,
  "created_at": "2025-10-29T10:00:00Z"
}
```

**List Environments:**
```json
GET /api/v1/environments

Response 200:
{
  "environments": [
    {
      "id": "uuid1",
      "name": "default",
      "package_count": 15,
      "total_size_mb": 250,
      "last_used_at": "2025-10-29T09:00:00Z"
    }
  ],
  "total": 1
}
```

### Implementation Tasks

- [x] Create environment router (`app/api/v1/environments.py`)
- [x] Add authentication middleware
- [x] Implement quota checks before creation
- [x] Add environment validation
- [x] Create API tests

**Completed**: 2025-10-30
**Files**:
- `pymd/backend/app/api/v1/environments.py` (305 lines)
- `pymd/backend/tests/test_api_environments.py` (285 lines)
- Updated `pymd/backend/app/main.py` to register router

---

## Phase 3: Package Management (Weeks 3-4)

### API Endpoints

```
POST   /api/v1/environments/{id}/packages
GET    /api/v1/environments/{id}/packages
DELETE /api/v1/environments/{id}/packages/{name}
POST   /api/v1/environments/{id}/packages/import
```

### Package Installation Flow

```python
1. User requests: POST /api/v1/environments/{id}/packages
   Body: {"packages": ["numpy", "pandas"]}

2. Backend checks:
   - User owns environment
   - Quota not exceeded (count & size)
   - Environment is active

3. Create task:
   - Queue Celery task for installation
   - Return task_id for tracking

4. Celery worker:
   - Create Docker container
   - Mount environment volume
   - Run: pip install numpy pandas --user --no-cache-dir
   - Parse output for versions/sizes
   - Update database

5. WebSocket notification:
   - Send progress updates
   - Notify completion or errors

6. Database update:
   - Add to environment_packages
   - Update total_size_bytes
   - Update package_count
```

### PackageService

**Methods:**
- `install_packages(env_id, packages, user_id)`
- `uninstall_package(env_id, package_name, user_id)`
- `list_packages(env_id, user_id)`
- `import_requirements(env_id, requirements_txt, user_id)`
- `get_package_info(env_id, package_name, user_id)`

### Implementation Tasks

- [ ] Create PackageService
- [ ] Add package installation endpoint
- [ ] Implement WebSocket progress
- [ ] Add package list/uninstall endpoints
- [ ] Requirements.txt import
- [ ] Add size tracking
- [ ] Create package tests

---

## Phase 4: Code Execution Integration (Weeks 4-5)

### Updated Execution Flow

**Old (Unsafe):**
```
User Code → exec() in API server → Output
```

**New (Safe):**
```
User Code + environment_id
    ↓
Celery Task Queue
    ↓
Worker: Create Docker Container
    ↓
Mount environment volume
    ↓
Execute with limits (CPU, memory, timeout)
    ↓
Capture output & files
    ↓
Cleanup container
    ↓
Return results via WebSocket
```

### Celery Setup

**Configuration:**
```python
# backend/app/workers/celery_app.py
celery_app = Celery(
    'pymd_backend',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# backend/app/workers/execution_worker.py
@celery_app.task(bind=True)
def execute_code_in_environment(
    self, user_id, environment_id, code, document_id
):
    # Get environment
    # Create container with volume
    # Execute code
    # Return results
```

### API Updates

**Render Endpoint Update:**
```python
POST /api/v1/render
{
  "content": "# Python code",
  "format": "html",
  "environment_id": "uuid"  # NEW - optional, uses default if not provided
}
```

### Implementation Tasks

- [ ] Set up Celery with Redis broker
- [ ] Create execution worker
- [ ] Update render endpoints
- [ ] Add environment_id to execution
- [ ] Implement output streaming
- [ ] Add execution history tracking
- [ ] Create execution tests

---

## Phase 5: Resource Management & Monitoring (Weeks 5-6)

### Monitoring

**Prometheus Metrics:**
```python
environment_creation_total = Counter('environment_creations_total')
package_installation_total = Counter('package_installations_total')
execution_duration_seconds = Histogram('execution_duration_seconds')
container_start_duration = Histogram('container_start_seconds')
quota_exceeded_total = Counter('quota_exceeded_total', ['type'])
```

### Cleanup Jobs

**Scheduled Tasks:**
- Remove stopped containers (hourly)
- Check orphaned volumes (daily)
- Update package sizes (weekly)
- Archive old execution logs (weekly)

### Admin Dashboard

**Features:**
- Total environments across users
- Total storage used
- Most popular packages
- Execution statistics
- Quota usage alerts
- System health metrics

### Implementation Tasks

- [ ] Add Prometheus integration
- [ ] Create cleanup jobs
- [ ] Build admin dashboard
- [ ] Add usage analytics
- [ ] Implement alerts
- [ ] Create monitoring docs

---

## Frontend Integration

### Components to Create

**EnvironmentSelector** (`components/EnvironmentSelector.tsx`):
```tsx
// Dropdown in editor toolbar
<select onChange={handleEnvironmentChange}>
  <option value="default">Default</option>
  <option value="data-science">Data Science</option>
  <option value="create-new">+ Create New...</option>
</select>
```

**EnvironmentManager** (`components/EnvironmentManager.tsx`):
```tsx
// Full management modal/page
- List all environments
- Create new environment
- Delete environment
- Reset environment
- View package list
- Show quota usage
```

**PackageInstaller** (`components/PackageInstaller.tsx`):
```tsx
// Package management interface
- Search PyPI packages
- Install button with progress
- List installed packages
- Uninstall button
- Import requirements.txt
- Disk usage visualization
```

### Zustand Store

```typescript
// stores/environmentStore.ts
interface EnvironmentStore {
  environments: Environment[];
  activeEnvironmentId: string | null;
  packages: Package[];
  isInstalling: boolean;
  installProgress: number;

  loadEnvironments: () => Promise<void>;
  createEnvironment: (name: string) => Promise<void>;
  deleteEnvironment: (id: string) => Promise<void>;
  setActiveEnvironment: (id: string) => void;
  installPackage: (packageName: string) => Promise<void>;
  uninstallPackage: (packageName: string) => Promise<void>;
}
```

### Implementation Tasks

- [ ] Create EnvironmentSelector component
- [ ] Create EnvironmentManager component
- [ ] Create PackageInstaller component
- [ ] Add environment Zustand store
- [ ] Integrate with editor
- [ ] Add WebSocket for progress
- [ ] Create frontend tests

---

## Security Considerations

### Container Security

```python
container_config = {
    'network_mode': 'none',  # No internet
    'read_only': True,  # Read-only root FS
    'security_opt': ['no-new-privileges'],
    'cap_drop': ['ALL'],
    'mem_limit': '512m',
    'memswap_limit': '512m',
    'cpu_quota': 50000,
    'pids_limit': 100,
}
```

### Package Safety

- Log all installations
- Size limits prevent DoS
- Optional package scanning
- No sudo/root in containers

### Volume Security

- Namespaced per user
- No cross-user mounting
- Cleanup on deletion
- Backup support

---

## Testing Strategy

### Unit Tests
- Environment CRUD operations
- Package installation/uninstallation
- Quota enforcement
- Docker volume management
- Container lifecycle

### Integration Tests
- Full execution flow
- Multiple environments per user
- Concurrent executions
- Environment reset
- Import requirements.txt

### Load Tests
- 100 users creating environments
- 50 concurrent package installations
- 200 concurrent code executions
- Container pool stress test

### Security Tests
- Container escape attempts
- Network isolation verification
- Resource limit enforcement
- Cross-user access prevention

---

## Rollout Strategy

### Week 1-2: Internal Testing
- Developer testing on staging
- Fix critical bugs
- Performance baseline

### Week 3: Alpha (5-10 users)
- Invite trusted users
- Gather feedback
- Monitor errors closely

### Week 4: Beta (50 users)
- Gradual rollout
- A/B testing if needed
- Monitor resource usage

### Week 5: General Availability
- Enable for all users
- Monitor system health
- Quick rollback plan ready

### Week 6: Optimization
- Address performance issues
- Optimize Docker images
- Implement caching

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Environment creation success rate | > 95% | Phase 1 ✅ |
| Package installation success rate | > 95% | TBD |
| Code execution success rate | > 90% | TBD |
| Average execution time (simple code) | < 5s | ~0.5s ✅ |
| Container start time | < 2s | ~1s ✅ |
| Zero security incidents | ✅ | ✅ |
| Docker image size | < 500MB | 410MB ✅ |

---

## Known Limitations & Future Work

### Current Limitations

1. **Volume Size Tracking** - Approximated from database, not real-time from Docker
2. **Package Size** - Installation reports estimates, not exact
3. **No Package Mirror** - Installs from PyPI directly (network required)
4. **Manual Cleanup** - Orphaned containers need periodic cleanup
5. **Single Python Version** - Only 3.11 currently supported

### Future Enhancements

1. **Multiple Python Versions** - Support 3.9, 3.10, 3.11, 3.12
2. **Conda Support** - Allow conda environments
3. **GPU Access** - Enable GPU for ML workloads (with limits)
4. **Shared Environments** - Team environments for collaboration
5. **Environment Templates** - Pre-configured environments (data-science, ml, web-dev)
6. **Package Caching** - Local PyPI mirror for faster installs
7. **Scheduled Cleanup** - Automatic removal of old environments
8. **Environment Export** - Export environment as requirements.txt or Dockerfile
9. **Real-time Collaboration** - Multiple users in same environment
10. **Environment Snapshots** - Save/restore environment states

---

## Dependencies & Prerequisites

### System Requirements
- Docker 20.10+
- PostgreSQL 13+
- Redis 6+
- Python 3.11+

### Service Dependencies
- Auth0 (authentication)
- Celery (async tasks)
- WebSocket (real-time updates)

### Database Migration
```bash
alembic upgrade head
```

### Docker Image
```bash
docker build -t pymd-executor:latest -f docker/executor/Dockerfile docker/executor/
```

---

## Documentation

### User Documentation
- How to create environments
- How to install packages
- How to switch environments
- Troubleshooting guide
- Quota limits explanation

### Developer Documentation
- Architecture overview
- API reference
- Database schema
- Docker setup guide
- Deployment guide

### Operations Documentation
- Monitoring setup
- Backup procedures
- Scaling guide
- Incident response
- Performance tuning

---

## Related Plans

- **[01 System Architecture](01_system_architecture.md)** - Overall system design
- **[02 API Specifications](02_api_specifications.md)** - API endpoint details
- **[03 Storage Schema](03_storage_schema.md)** - Database schema
- **[04 Auth0 Integration](04_auth0_integration.md)** - Authentication

---

**Document Version**: 1.1
**Last Updated**: 2025-10-30
**Status**: Phase 1-2 Complete ✅ | Phase 3-5 In Planning
