# PyMD Storage Schema Design

**Version:** 1.0.0
**Date:** 2025-10-17

## Table of Contents

1. [Database Technology Selection](#database-technology-selection)
2. [Schema Overview](#schema-overview)
3. [Entity Definitions](#entity-definitions)
4. [Relationships](#relationships)
5. [Indexing Strategy](#indexing-strategy)
6. [Document Storage Strategy](#document-storage-strategy)
7. [Migration Strategy](#migration-strategy)
8. [Backup and Recovery](#backup-and-recovery)
9. [Performance Optimization](#performance-optimization)
10. [Caching Strategy](#caching-strategy)

---

## Database Technology Selection

### Chosen Database: PostgreSQL 15+

**Rationale:**

**Advantages:**
- **ACID Compliance**: Essential for user data integrity and document consistency
- **JSON Support**: Native JSONB for flexible user settings and metadata
- **Full-Text Search**: Built-in support for document content search
- **Proven Scalability**: Handles millions of rows efficiently
- **Rich Ecosystem**: Excellent tooling, extensions, and community support
- **Data Integrity**: Strong constraint enforcement and referential integrity
- **Mature ORM Support**: SQLAlchemy, Django ORM, etc.

**Comparison to Alternatives:**

| Feature | PostgreSQL | MySQL | MongoDB |
|---------|-----------|-------|---------|
| ACID Compliance | ✅ Full | ✅ Full | ❌ Limited |
| JSON Support | ✅ JSONB | ⚠️ Basic | ✅ Native |
| Full-Text Search | ✅ Built-in | ⚠️ Limited | ✅ Good |
| Relationships | ✅ Strong | ✅ Strong | ❌ Weak |
| Schema Evolution | ✅ Excellent | ✅ Good | ✅ Flexible |
| Complex Queries | ✅ Excellent | ✅ Good | ⚠️ Limited |
| Horizontal Scaling | ⚠️ Moderate | ⚠️ Moderate | ✅ Excellent |

**Decision**: PostgreSQL provides the best balance of relational data integrity, flexible JSON storage, full-text search, and proven scalability for a document management system.

---

## Schema Overview

### Core Entities

1. **users** - User accounts and authentication
2. **documents** - PyMD document content and metadata
3. **user_settings** - User preferences and configuration
4. **sessions** - User session management
5. **tags** - Document categorization
6. **document_tags** - Many-to-many relationship
7. **document_versions** - Version history (optional, future)
8. **api_keys** - API access tokens (future)

### Entity Relationship Diagram

```
┌─────────────┐
│   users     │
└──────┬──────┘
       │
       │ 1:1
       ├──────────────────┐
       │                  │
       │ 1:N              │ 1:1
       ▼                  ▼
┌─────────────┐    ┌──────────────┐
│  documents  │    │user_settings │
└──────┬──────┘    └──────────────┘
       │
       │ M:N
       ├──────────────┐
       │              │
       ▼              ▼
┌─────────────┐ ┌────────┐
│document_tags│─│  tags  │
└─────────────┘ └────────┘
```

---

## Entity Definitions

### 1. users

Stores user account information synced from Auth0.

```sql
CREATE TABLE users (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Auth0 Integration
    auth0_id VARCHAR(255) UNIQUE NOT NULL,  -- Auth0 user ID (sub claim)
    email VARCHAR(320) UNIQUE NOT NULL,      -- RFC 5321 max length
    email_verified BOOLEAN DEFAULT FALSE,

    -- Profile Information
    name VARCHAR(255) NOT NULL,
    avatar_url TEXT,                         -- Profile picture URL
    bio TEXT,                                -- User biography
    role VARCHAR(50) DEFAULT 'user',         -- user|admin|premium

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,

    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT role_values CHECK (role IN ('user', 'admin', 'premium'))
);

-- Indexes
CREATE INDEX idx_users_auth0_id ON users(auth0_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_last_login ON users(last_login_at DESC);
```

**Field Descriptions:**
- `id`: UUID primary key for internal references
- `auth0_id`: Auth0 unique identifier (from `sub` claim in JWT)
- `email`: User email address (unique, indexed)
- `email_verified`: Email verification status from Auth0
- `name`: Display name
- `avatar_url`: Profile picture URL (can be Auth0 avatar or custom)
- `bio`: User biography/description
- `role`: User permission level (user, admin, premium)
- `is_active`: Account active status (for soft ban)
- `is_deleted`: Soft delete flag
- `last_login_at`: Last successful login timestamp

---

### 2. documents

Stores PyMD document content and metadata.

```sql
CREATE TABLE documents (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Ownership
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Document Content
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,                   -- PyMD source content
    content_hash VARCHAR(64),                -- SHA-256 for change detection

    -- Rendering
    render_format VARCHAR(20) DEFAULT 'html', -- html|markdown
    rendered_html TEXT,                       -- Cached HTML output
    rendered_markdown TEXT,                   -- Cached Markdown output
    rendered_at TIMESTAMP WITH TIME ZONE,     -- Last render timestamp

    -- Metadata
    description TEXT,                         -- Document description/summary
    is_public BOOLEAN DEFAULT FALSE,          -- Public access flag
    is_template BOOLEAN DEFAULT FALSE,        -- Template document flag

    -- Status
    is_deleted BOOLEAN DEFAULT FALSE,         -- Soft delete

    -- Size and Stats
    content_length INTEGER GENERATED ALWAYS AS (LENGTH(content)) STORED,
    word_count INTEGER,                       -- Word count cache

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE,

    -- Full-Text Search
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(content, '')), 'C')
    ) STORED,

    -- Constraints
    CONSTRAINT title_not_empty CHECK (LENGTH(TRIM(title)) > 0),
    CONSTRAINT content_not_empty CHECK (LENGTH(TRIM(content)) > 0),
    CONSTRAINT content_size_limit CHECK (LENGTH(content) <= 10485760), -- 10MB
    CONSTRAINT render_format_values CHECK (render_format IN ('html', 'markdown'))
);

-- Indexes
CREATE INDEX idx_documents_owner_id ON documents(owner_id);
CREATE INDEX idx_documents_created_at ON documents(created_at DESC);
CREATE INDEX idx_documents_updated_at ON documents(updated_at DESC);
CREATE INDEX idx_documents_title ON documents(title);
CREATE INDEX idx_documents_is_public ON documents(is_public) WHERE is_public = TRUE;
CREATE INDEX idx_documents_is_deleted ON documents(is_deleted) WHERE is_deleted = FALSE;
CREATE INDEX idx_documents_search_vector ON documents USING GIN(search_vector);
CREATE INDEX idx_documents_content_hash ON documents(content_hash);

-- Composite indexes for common queries
CREATE INDEX idx_documents_owner_updated ON documents(owner_id, updated_at DESC);
CREATE INDEX idx_documents_owner_created ON documents(owner_id, created_at DESC);
```

**Field Descriptions:**
- `id`: UUID primary key
- `owner_id`: Foreign key to users table
- `title`: Document title (required, max 255 chars)
- `content`: PyMD source content (max 10MB)
- `content_hash`: SHA-256 hash for detecting changes
- `render_format`: Default output format (html or markdown)
- `rendered_html`: Cached HTML rendering
- `rendered_markdown`: Cached Markdown rendering
- `rendered_at`: Timestamp of last successful render
- `description`: Optional document description
- `is_public`: Public access flag (future feature)
- `is_template`: Mark as template document
- `content_length`: Auto-calculated content length
- `word_count`: Cached word count
- `search_vector`: Full-text search tsvector (auto-generated)

---

### 3. user_settings

Stores user preferences and configuration.

```sql
CREATE TABLE user_settings (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationship
    user_id UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- UI Preferences
    theme VARCHAR(20) DEFAULT 'light',         -- light|dark|auto
    language VARCHAR(10) DEFAULT 'en',         -- en|zh|ja|etc

    -- Editor Settings (JSONB for flexibility)
    editor_settings JSONB DEFAULT '{
        "fontSize": 14,
        "tabSize": 4,
        "wordWrap": true,
        "lineNumbers": true,
        "syntaxHighlighting": true,
        "autoComplete": true,
        "vimMode": false
    }'::jsonb,

    -- Render Settings
    render_settings JSONB DEFAULT '{
        "defaultFormat": "html",
        "autoSave": true,
        "autoSaveInterval": 30,
        "includeToc": true,
        "includeStyles": true
    }'::jsonb,

    -- Notification Settings
    notification_settings JSONB DEFAULT '{
        "email": true,
        "browser": true,
        "documentShared": true,
        "systemUpdates": true
    }'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT theme_values CHECK (theme IN ('light', 'dark', 'auto'))
);

-- Indexes
CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX idx_user_settings_theme ON user_settings(theme);
```

**JSONB Schema Examples:**

**editor_settings:**
```json
{
  "fontSize": 14,
  "tabSize": 4,
  "wordWrap": true,
  "lineNumbers": true,
  "syntaxHighlighting": true,
  "autoComplete": true,
  "vimMode": false,
  "keyBindings": "default"
}
```

**render_settings:**
```json
{
  "defaultFormat": "html",
  "autoSave": true,
  "autoSaveInterval": 30,
  "includeToc": true,
  "includeStyles": true,
  "theme": "github"
}
```

---

### 4. sessions

Stores user session information for authentication.

```sql
CREATE TABLE sessions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationship
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Session Data
    session_token VARCHAR(255) UNIQUE NOT NULL,  -- Session identifier
    refresh_token TEXT,                          -- Auth0 refresh token (encrypted)
    access_token TEXT,                           -- Auth0 access token (encrypted)

    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- Client Information
    user_agent TEXT,
    ip_address INET,
    device_info JSONB,                           -- Device fingerprint

    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT expires_after_creation CHECK (expires_at > created_at)
);

-- Indexes
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_session_token ON sessions(session_token);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_is_active ON sessions(is_active) WHERE is_active = TRUE;

-- Composite index for session validation
CREATE INDEX idx_sessions_token_active ON sessions(session_token, is_active, expires_at);
```

**Field Descriptions:**
- `session_token`: Unique session identifier (stored in cookie)
- `refresh_token`: Auth0 refresh token (encrypted at rest)
- `access_token`: Auth0 access token (encrypted at rest)
- `expires_at`: Session expiration timestamp
- `user_agent`: Browser user agent string
- `ip_address`: Client IP address
- `device_info`: Device fingerprint (JSONB)
- `is_active`: Session active status
- `revoked_at`: Timestamp when session was revoked

---

### 5. tags

Stores available tags for document categorization.

```sql
CREATE TABLE tags (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Tag Information
    name VARCHAR(50) UNIQUE NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,          -- URL-safe version
    color VARCHAR(7) DEFAULT '#3B82F6',        -- Hex color code

    -- Metadata
    description TEXT,
    usage_count INTEGER DEFAULT 0,             -- Number of documents using tag

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT name_not_empty CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT slug_format CHECK (slug ~* '^[a-z0-9-]+$'),
    CONSTRAINT color_format CHECK (color ~* '^#[0-9A-F]{6}$')
);

-- Indexes
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_tags_slug ON tags(slug);
CREATE INDEX idx_tags_usage_count ON tags(usage_count DESC);
```

---

### 6. document_tags

Many-to-many relationship between documents and tags.

```sql
CREATE TABLE document_tags (
    -- Composite Primary Key
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Primary Key
    PRIMARY KEY (document_id, tag_id)
);

-- Indexes
CREATE INDEX idx_document_tags_document_id ON document_tags(document_id);
CREATE INDEX idx_document_tags_tag_id ON document_tags(tag_id);
```

---

### 7. document_versions (Future Feature)

Stores version history for documents.

```sql
CREATE TABLE document_versions (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Relationship
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,

    -- Version Data
    version_number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    content_hash VARCHAR(64) NOT NULL,

    -- Metadata
    change_description TEXT,
    changes_summary JSONB,                   -- Diff summary

    -- Size
    content_length INTEGER,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    UNIQUE(document_id, version_number)
);

-- Indexes
CREATE INDEX idx_document_versions_document_id ON document_versions(document_id);
CREATE INDEX idx_document_versions_created_at ON document_versions(created_at DESC);
CREATE INDEX idx_document_versions_doc_version ON document_versions(document_id, version_number DESC);
```

---

## Relationships

### Cardinality

| Relationship | Type | Description |
|-------------|------|-------------|
| users ↔ documents | 1:N | One user owns many documents |
| users ↔ user_settings | 1:1 | One user has one settings record |
| users ↔ sessions | 1:N | One user can have multiple active sessions |
| documents ↔ tags | M:N | Many documents can have many tags |
| documents ↔ document_versions | 1:N | One document has many versions |

### Foreign Key Constraints

All foreign keys use:
- `ON DELETE CASCADE`: For owned entities (documents, settings, sessions)
- `ON DELETE SET NULL`: For audit trail entities (document_versions.user_id)
- `ON DELETE RESTRICT`: For shared entities (not applicable yet)

### Referential Integrity

PostgreSQL enforces:
- Foreign key constraints
- Unique constraints
- Check constraints
- NOT NULL constraints

---

## Indexing Strategy

### Index Types

1. **B-Tree Indexes** (Default)
   - Primary keys (automatic)
   - Foreign keys
   - Frequently queried columns
   - Sorting columns

2. **GIN Indexes**
   - Full-text search vectors
   - JSONB columns (when needed)

3. **Partial Indexes**
   - `WHERE is_deleted = FALSE` for active records
   - `WHERE is_active = TRUE` for active sessions
   - `WHERE is_public = TRUE` for public documents

### Index Maintenance

**Monitoring:**
```sql
-- Check unused indexes
SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;

-- Check index bloat
SELECT * FROM pg_stat_user_tables;
```

**Maintenance:**
- **REINDEX**: Monthly for frequently updated tables
- **VACUUM**: Automated by PostgreSQL autovacuum
- **ANALYZE**: After bulk operations

### Query Optimization Guidelines

1. **Use indexes for:**
   - WHERE clauses
   - JOIN conditions
   - ORDER BY columns
   - Frequent search patterns

2. **Avoid indexes for:**
   - Low cardinality columns (< 10 distinct values)
   - Columns rarely used in queries
   - Very small tables (< 1000 rows)

---

## Document Storage Strategy

### Content Storage: Database (JSONB + TEXT)

**Decision**: Store document content in PostgreSQL TEXT columns.

**Rationale:**

**Pros:**
- **Transactional Integrity**: ACID guarantees for document updates
- **Atomic Updates**: Content and metadata updated together
- **Simplified Architecture**: No separate storage layer
- **Full-Text Search**: Native PostgreSQL search capabilities
- **Backup Simplicity**: Single database backup includes all data
- **Performance**: Fast for documents < 10MB with proper indexing

**Cons:**
- **Database Size**: Large documents increase database size
- **Backup Duration**: Larger backups with content included

**Alternative Considered**: File System + Database Metadata

**Why Not File System:**
- Added complexity (sync issues, consistency problems)
- No transactional guarantees across systems
- More difficult backup/restore procedures
- File system permission management
- CDN integration more complex

**Mitigation for Large Databases:**
- **Content Limit**: 10MB per document (enforced by constraint)
- **Compression**: Use PostgreSQL pg_compress for large TEXT fields
- **Partitioning**: Table partitioning by date if needed
- **Archival**: Move old/inactive documents to archive tables

### Rendered Content Caching

Store rendered HTML/Markdown in database for performance:
- **rendered_html**: Cached HTML output
- **rendered_markdown**: Cached Markdown output
- **rendered_at**: Cache timestamp
- **content_hash**: Invalidate cache on content change

**Cache Invalidation:**
```sql
-- Trigger to invalidate cache on content update
CREATE OR REPLACE FUNCTION invalidate_render_cache()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.content <> OLD.content THEN
        NEW.content_hash = encode(sha256(NEW.content::bytea), 'hex');
        NEW.rendered_html = NULL;
        NEW.rendered_markdown = NULL;
        NEW.rendered_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_invalidate_render_cache
BEFORE UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION invalidate_render_cache();
```

---

## Migration Strategy

### Migration Tool: Alembic

**Why Alembic:**
- Industry standard for SQLAlchemy-based projects
- Automatic migration script generation
- Version control for database schema
- Supports complex migrations (data transformations)
- Rollback capabilities

### Migration Workflow

1. **Development**: Create migration scripts with Alembic
2. **Testing**: Test migrations on staging database
3. **Review**: Code review for migration scripts
4. **Deployment**: Apply migrations before app deployment
5. **Verification**: Verify schema and data integrity

### Migration Script Structure

```python
# alembic/versions/001_initial_schema.py
def upgrade():
    # Create tables in dependency order
    op.create_table('users', ...)
    op.create_table('documents', ...)
    # Create indexes
    # Create triggers

def downgrade():
    # Drop in reverse order
    op.drop_table('documents')
    op.drop_table('users')
```

### Zero-Downtime Migrations

For production deployments:

1. **Additive Changes**: Add new columns/tables without removing old ones
2. **Backward Compatibility**: New code works with old schema
3. **Two-Phase Deployment**:
   - Phase 1: Deploy schema changes
   - Phase 2: Deploy code changes
4. **Data Migrations**: Run in background for large datasets

### Schema Versioning

Track schema version in database:
```sql
CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    PRIMARY KEY (version_num)
);
```

---

## Backup and Recovery

### Backup Strategy

#### 1. Full Database Backups
- **Frequency**: Daily at 2:00 AM UTC
- **Retention**: 7 daily, 4 weekly, 12 monthly
- **Tool**: `pg_dump` or `pg_basebackup`
- **Storage**: AWS S3, Azure Blob, or Google Cloud Storage

```bash
# Full backup
pg_dump -Fc -f backup_$(date +%Y%m%d).dump pymd_db

# Restore
pg_restore -d pymd_db backup_20251017.dump
```

#### 2. Incremental Backups (WAL Archiving)
- **Frequency**: Continuous (Write-Ahead Log archiving)
- **RPO**: < 5 minutes
- **Tool**: PostgreSQL WAL archiving + tools like WAL-G or pgBackRest

#### 3. Point-in-Time Recovery (PITR)
- Enable WAL archiving for PITR capability
- Restore to any point within retention window

### Backup Verification
- **Monthly**: Test restore on staging environment
- **Automated**: Integrity checks on backup files
- **Monitoring**: Alert on backup failures

### Disaster Recovery

**RTO (Recovery Time Objective)**: 4 hours
**RPO (Recovery Point Objective)**: 15 minutes

**Recovery Procedures:**
1. Restore from most recent backup
2. Apply WAL logs for PITR
3. Verify data integrity
4. Update DNS/load balancer
5. Resume operations

---

## Performance Optimization

### Query Optimization

#### 1. Efficient Queries
```sql
-- Good: Use covering indexes
SELECT id, title, created_at
FROM documents
WHERE owner_id = $1
ORDER BY created_at DESC
LIMIT 20;

-- Bad: SELECT *
SELECT * FROM documents WHERE owner_id = $1;
```

#### 2. Pagination
```sql
-- Use cursor-based pagination for large datasets
SELECT * FROM documents
WHERE created_at < $cursor
ORDER BY created_at DESC
LIMIT 20;
```

#### 3. N+1 Query Prevention
```sql
-- Good: JOIN to get related data
SELECT d.*, u.name as owner_name
FROM documents d
JOIN users u ON d.owner_id = u.id
WHERE d.id = $1;

-- Bad: Separate queries
SELECT * FROM documents WHERE id = $1;
SELECT name FROM users WHERE id = $owner_id;
```

### Database Configuration

**PostgreSQL Tuning Parameters:**

```ini
# Memory
shared_buffers = 4GB              # 25% of RAM
effective_cache_size = 12GB       # 75% of RAM
work_mem = 64MB                   # Per-operation memory
maintenance_work_mem = 1GB        # For VACUUM, CREATE INDEX

# Connections
max_connections = 200
connection_limit = 100            # Reserve for maintenance

# Write Performance
wal_buffers = 16MB
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9

# Query Planner
random_page_cost = 1.1            # For SSD storage
effective_io_concurrency = 200    # For SSD storage
```

### Connection Pooling

Use **PgBouncer** or **SQLAlchemy pooling**:

```python
# SQLAlchemy connection pool
engine = create_engine(
    DATABASE_URL,
    pool_size=20,              # Max connections
    max_overflow=10,           # Additional connections
    pool_pre_ping=True,        # Verify connection health
    pool_recycle=3600          # Recycle after 1 hour
)
```

### Read Replicas

For read-heavy workloads:
- **Primary**: Write operations
- **Replicas**: Read operations (1-2 replicas)
- **Load Balancer**: Route reads to replicas

```python
# Read/Write splitting
read_engine = create_engine(REPLICA_URL)
write_engine = create_engine(PRIMARY_URL)
```

---

## Caching Strategy

### Multi-Level Caching

#### 1. Application-Level Cache (Redis)

**Use Cases:**
- Session data
- Rendered document cache
- User settings
- API rate limiting counters
- Full-text search results

**Configuration:**
```python
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "decode_responses": True,
    "max_connections": 50
}
```

**Cache Keys:**
```
user:settings:{user_id}
document:rendered:{document_id}:{format}
session:{session_token}
ratelimit:{user_id}:{endpoint}
```

**TTL Strategy:**
- User settings: 1 hour
- Rendered documents: 1 hour (invalidate on update)
- Sessions: Match JWT expiry
- Rate limits: 1 minute/1 hour based on limit window

#### 2. Database Query Cache

**PostgreSQL Query Result Cache:**
- Use prepared statements
- PostgreSQL's internal query cache
- Application-level query result caching

#### 3. CDN Cache

For rendered documents (future):
- Cache rendered HTML at CDN edge
- Serve static content globally
- Reduce database load

### Cache Invalidation

**Strategies:**
1. **TTL-Based**: Automatic expiration
2. **Event-Based**: Invalidate on updates
3. **Tag-Based**: Invalidate related caches

**Example:**
```python
async def update_document(document_id: str, content: str):
    # Update database
    await db.update(document_id, content)

    # Invalidate caches
    await cache.delete(f"document:rendered:{document_id}:html")
    await cache.delete(f"document:rendered:{document_id}:markdown")
    await cache.delete(f"user:documents:{owner_id}")
```

---

## Data Retention and Archival

### Active Data Retention
- **Documents**: Indefinite (until user deletes)
- **Sessions**: 30 days after expiration
- **Audit Logs**: 90 days

### Soft Delete Strategy
- Use `is_deleted` flag instead of hard deletes
- Allows recovery within grace period (30 days)
- Hard delete after grace period via scheduled job

### Archival Process
```sql
-- Archive old deleted documents
INSERT INTO documents_archive
SELECT * FROM documents
WHERE is_deleted = TRUE
  AND updated_at < NOW() - INTERVAL '30 days';

-- Hard delete after archival
DELETE FROM documents
WHERE is_deleted = TRUE
  AND updated_at < NOW() - INTERVAL '30 days';
```

---

## Security Considerations

### Data Encryption

1. **At Rest**: Use PostgreSQL encryption (pgcrypto extension)
   ```sql
   -- Encrypt sensitive fields
   CREATE EXTENSION pgcrypto;

   -- Store encrypted tokens
   INSERT INTO sessions (access_token)
   VALUES (pgp_sym_encrypt($token, $key));
   ```

2. **In Transit**: TLS/SSL for database connections

### Access Control

1. **Database Users**: Separate credentials per service
2. **Least Privilege**: Grant minimum required permissions
3. **No Direct Access**: Applications only, no direct client access

### SQL Injection Prevention

1. **Parameterized Queries**: Always use prepared statements
2. **ORM**: SQLAlchemy provides automatic escaping
3. **Input Validation**: Validate before database operations

### Auditing

Track sensitive operations:
- User creation/deletion
- Document access (if required)
- Admin actions
- Schema changes

---

**End of Storage Schema Design**
