# PyMD Frontend Architecture Plan

**Version:** 1.0.0
**Date:** 2025-10-17

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [Routing Architecture](#routing-architecture)
4. [Page Specifications](#page-specifications)
5. [Component Architecture](#component-architecture)
6. [State Management](#state-management)
7. [Styling Strategy](#styling-strategy)
8. [API Integration](#api-integration)
9. [Real-time Features](#real-time-features)
10. [Performance Optimization](#performance-optimization)
11. [User Experience](#user-experience)

---

## Technology Stack

### Core Framework: Next.js 15 (App Router)

**Why Next.js 15:**

| Feature | Benefit |
|---------|---------|
| **App Router** | Modern routing with React Server Components |
| **Server Components** | Better performance, reduced client bundle |
| **Streaming SSR** | Faster initial page loads |
| **Built-in API Routes** | Simplified backend integration |
| **Image Optimization** | Automatic image optimization |
| **TypeScript Support** | First-class TypeScript experience |
| **SEO Friendly** | Server-side rendering for SEO |

### Technology Decisions

```yaml
Framework: Next.js 15
Language: TypeScript 5.x
Styling: Tailwind CSS 3.x
State Management:
  - Server State: TanStack Query (React Query) v5
  - Client State: Zustand
  - Form State: React Hook Form
UI Components: Shadcn/ui (Radix UI + Tailwind)
Icons: Lucide React
Editor: Monaco Editor (VS Code editor)
Markdown: Unified (remark/rehype ecosystem)
HTTP Client: Fetch API with wrapper
Authentication: @auth0/nextjs-auth0
Testing:
  - Unit: Vitest + React Testing Library
  - E2E: Playwright
Build Tool: Turbopack (Next.js 15 default)
Package Manager: pnpm
```

### Alternatives Considered

| Alternative | Why Not Selected |
|-------------|------------------|
| **Vite + React** | Less integrated, no SSR out of box |
| **Remix** | Smaller ecosystem, less mature |
| **Create React App** | Deprecated, no SSR |
| **Redux** (state) | Overkill for this app, more boilerplate |
| **Monaco vs CodeMirror** | Monaco has better TypeScript/IntelliSense support |

---

## Project Structure

### Directory Layout

```
frontend/
├── app/                        # Next.js 15 App Router
│   ├── (auth)/                 # Auth route group (special layout)
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── signup/
│   │   │   └── page.tsx
│   │   └── layout.tsx          # Auth-specific layout
│   │
│   ├── (dashboard)/            # Dashboard route group (requires auth)
│   │   ├── dashboard/
│   │   │   └── page.tsx        # /dashboard
│   │   ├── documents/
│   │   │   ├── page.tsx        # /documents (list)
│   │   │   ├── [id]/
│   │   │   │   ├── page.tsx    # /documents/:id (view/edit)
│   │   │   │   └── edit/
│   │   │   │       └── page.tsx # /documents/:id/edit
│   │   │   └── new/
│   │   │       └── page.tsx    # /documents/new
│   │   ├── settings/
│   │   │   ├── page.tsx        # /settings (redirect to profile)
│   │   │   ├── profile/
│   │   │   │   └── page.tsx    # /settings/profile
│   │   │   ├── preferences/
│   │   │   │   └── page.tsx    # /settings/preferences
│   │   │   └── security/
│   │   │       └── page.tsx    # /settings/security
│   │   └── layout.tsx          # Dashboard layout (sidebar + nav)
│   │
│   ├── api/                    # API routes
│   │   └── auth/
│   │       └── [auth0]/
│   │           └── route.ts    # Auth0 callback handler
│   │
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Landing page (/)
│   ├── error.tsx               # Error boundary
│   ├── loading.tsx             # Loading UI
│   └── not-found.tsx           # 404 page
│
├── components/                 # Reusable components
│   ├── ui/                     # Shadcn/ui components
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── dialog.tsx
│   │   ├── dropdown.tsx
│   │   ├── toast.tsx
│   │   └── ...
│   │
│   ├── layout/                 # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   ├── Footer.tsx
│   │   └── DashboardLayout.tsx
│   │
│   ├── document/               # Document-related components
│   │   ├── DocumentList.tsx
│   │   ├── DocumentCard.tsx
│   │   ├── DocumentEditor.tsx
│   │   ├── DocumentPreview.tsx
│   │   ├── DocumentToolbar.tsx
│   │   └── DocumentSearch.tsx
│   │
│   ├── editor/                 # Editor components
│   │   ├── MonacoEditor.tsx
│   │   ├── EditorToolbar.tsx
│   │   ├── EditorSettings.tsx
│   │   └── EditorStatusBar.tsx
│   │
│   └── common/                 # Common components
│       ├── Loading.tsx
│       ├── ErrorMessage.tsx
│       ├── EmptyState.tsx
│       ├── ConfirmDialog.tsx
│       └── UserAvatar.tsx
│
├── lib/                        # Utility libraries
│   ├── api/                    # API client
│   │   ├── client.ts           # Base API client
│   │   ├── documents.ts        # Document API methods
│   │   ├── users.ts            # User API methods
│   │   └── render.ts           # Render API methods
│   │
│   ├── hooks/                  # Custom React hooks
│   │   ├── useDocuments.ts
│   │   ├── useDocument.ts
│   │   ├── useUser.ts
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── store/                  # Zustand stores
│   │   ├── uiStore.ts          # UI state (sidebar open, theme)
│   │   ├── editorStore.ts      # Editor state
│   │   └── authStore.ts        # Auth state (minimal)
│   │
│   ├── utils/                  # Utility functions
│   │   ├── cn.ts               # Class name merger
│   │   ├── format.ts           # Date/time formatting
│   │   ├── validation.ts       # Form validation
│   │   └── markdown.ts         # Markdown utilities
│   │
│   └── types/                  # TypeScript types
│       ├── document.ts
│       ├── user.ts
│       ├── api.ts
│       └── index.ts
│
├── styles/                     # Global styles
│   ├── globals.css             # Global CSS + Tailwind imports
│   ├── editor.css              # Editor-specific styles
│   └── markdown.css            # Markdown preview styles
│
├── public/                     # Static assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
│
├── middleware.ts               # Next.js middleware (auth)
├── next.config.js              # Next.js configuration
├── tailwind.config.ts          # Tailwind configuration
├── tsconfig.json               # TypeScript configuration
├── package.json
└── pnpm-lock.yaml
```

### Module Organization Principles

1. **Route Groups**: Use Next.js route groups `(name)` to organize routes without affecting URL structure
2. **Colocation**: Keep related files close (components, hooks, types used in one place)
3. **Separation of Concerns**: Separate UI, logic, and data layers
4. **Reusability**: Extract common patterns into reusable components

---

## Routing Architecture

### Route Map

```
Public Routes (No Auth Required):
/                         → Landing page
/login                    → Auth0 login redirect
/signup                   → Auth0 signup redirect

Protected Routes (Auth Required):
/dashboard                → User dashboard overview
/documents                → Document list
/documents/new            → Create new document
/documents/:id            → View/edit document
/documents/:id/edit       → Edit document (optional, or same as view)
/settings                 → User settings (redirect to /settings/profile)
/settings/profile         → Profile settings
/settings/preferences     → Editor preferences
/settings/security        → Security settings

API Routes:
/api/auth/[auth0]         → Auth0 callback handler
/api/auth/callback        → Custom callback logic
/api/auth/logout          → Logout handler

Error Routes:
/404                      → Not found page
/500                      → Server error page
/error                    → Generic error page
```

### Navigation Structure

```
┌─────────────────────────────────────────────────────┐
│                    Header/Nav                       │
│  [Logo] [Dashboard] [Documents]  [User] [Settings]  │
└─────────────────────────────────────────────────────┘
│
├─ / (Landing)
│  └─ [Get Started] → /login
│
├─ /dashboard
│  ├─ Recent Documents (3)
│  ├─ Quick Actions (New Document, Templates)
│  └─ Usage Stats
│
├─ /documents
│  ├─ [New Document] button
│  ├─ Search bar
│  ├─ Filter/Sort options
│  └─ Document grid/list
│     └─ Click → /documents/:id
│
├─ /documents/:id
│  ├─ Split view: Editor | Preview
│  ├─ Toolbar (Save, Export, Settings)
│  └─ Status bar
│
└─ /settings
   ├─ Sidebar navigation
   │  ├─ Profile
   │  ├─ Preferences
   │  └─ Security
   └─ Content area
```

### Middleware Configuration

**File: `middleware.ts`**

```typescript
import { withMiddlewareAuthRequired } from '@auth0/nextjs-auth0/edge';

export default withMiddlewareAuthRequired();

export const config = {
  matcher: [
    // Protect dashboard routes
    '/dashboard/:path*',
    '/documents/:path*',
    '/settings/:path*',

    // Exclude public routes
    '/((?!api|_next/static|_next/image|favicon.ico|images).*)',
  ],
};
```

---

## Page Specifications

### 1. Landing Page (`/`)

**Purpose**: Marketing page to introduce PyMD and drive signups

**Layout**:
```
┌────────────────────────────────────┐
│  Header: [Logo] [Login] [Sign Up] │
├────────────────────────────────────┤
│  Hero Section                      │
│  - Headline                        │
│  - Subheadline                     │
│  - CTA Button → /login             │
│  - Hero image/demo                 │
├────────────────────────────────────┤
│  Features Section                  │
│  - 3-4 key features                │
│  - Icons + descriptions            │
├────────────────────────────────────┤
│  How It Works                      │
│  - Step 1: Write PyMD              │
│  - Step 2: Render                  │
│  - Step 3: Export                  │
├────────────────────────────────────┤
│  CTA Section                       │
│  - "Get Started Free" button       │
├────────────────────────────────────┤
│  Footer                            │
│  - Links, Social, Copyright        │
└────────────────────────────────────┘
```

**Components**:
- `Hero` - Hero section with CTA
- `FeatureGrid` - Feature highlights
- `HowItWorks` - Step-by-step guide
- `CTASection` - Final call to action

**State**: None (static content)

---

### 2. Login Page (`/login`)

**Purpose**: Redirect to Auth0 Universal Login

**Implementation**:
```typescript
// Redirect to Auth0
export default function LoginPage() {
  useEffect(() => {
    window.location.href = '/api/auth/login';
  }, []);

  return <Loading message="Redirecting to login..." />;
}
```

**Alternative**: Show branded loading page while redirecting

---

### 3. Dashboard Page (`/dashboard`)

**Purpose**: User's home page after login

**Layout**:
```
┌──────────┬────────────────────────────────┐
│          │  Welcome, {User}!              │
│ Sidebar  ├────────────────────────────────┤
│          │  Quick Actions                 │
│          │  [+ New Document] [Templates]  │
│          ├────────────────────────────────┤
│          │  Recent Documents              │
│          │  ┌──────┐ ┌──────┐ ┌──────┐   │
│          │  │ Doc1 │ │ Doc2 │ │ Doc3 │   │
│          │  └──────┘ └──────┘ └──────┘   │
│          ├────────────────────────────────┤
│          │  Statistics                    │
│          │  - Total Documents: 24         │
│          │  - Storage Used: 2.3 MB        │
│          │  - Last Active: Today          │
└──────────┴────────────────────────────────┘
```

**Components**:
- `DashboardHeader` - Welcome message
- `QuickActions` - Action buttons
- `RecentDocuments` - Recent 3-6 documents
- `StatsCard` - Usage statistics

**Data Requirements**:
- Recent documents (API: `GET /documents?sort=updated&limit=6`)
- User statistics (API: `GET /users/me`)

**State**:
- Recent documents (React Query)
- User info (React Query)

---

### 4. Documents List Page (`/documents`)

**Purpose**: Browse and manage all user documents

**Layout**:
```
┌──────────┬────────────────────────────────────────┐
│          │  My Documents                          │
│ Sidebar  │  [+ New Document]                      │
│          ├────────────────────────────────────────┤
│          │  [Search...]  [Sort ▼] [Filter ▼]     │
│          ├────────────────────────────────────────┤
│          │  ┌─────────────────────────────────┐  │
│          │  │ Document Title 1                │  │
│          │  │ Preview text...                 │  │
│          │  │ Modified: 2 hours ago           │  │
│          │  │ [Edit] [Delete] [Export]        │  │
│          │  └─────────────────────────────────┘  │
│          │  ┌─────────────────────────────────┐  │
│          │  │ Document Title 2                │  │
│          │  │ ...                             │  │
│          │  └─────────────────────────────────┘  │
│          │  [Pagination]                          │
└──────────┴────────────────────────────────────────┘
```

**Components**:
- `DocumentListHeader` - Title + New button
- `DocumentSearch` - Search input
- `DocumentFilters` - Sort/filter controls
- `DocumentCard` - Individual document card
- `Pagination` - Page navigation

**Features**:
- Search (debounced, query: `?search=term`)
- Sort (created, updated, title)
- Filter (tags, format)
- Pagination (client-side or server-side)
- Bulk actions (future: select multiple, delete)

**Data Requirements**:
- Documents list (API: `GET /documents?page=1&limit=20&search=term&sort=updated`)

**State**:
- Search query (URL param + local state)
- Sort/filter options (URL params)
- Current page (URL param)
- Documents (React Query with params)

---

### 5. Document Editor Page (`/documents/:id`)

**Purpose**: Edit and preview PyMD documents

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  [< Back] Document Title          [Save] [▼]   │ ← Toolbar
├─────────────────┬───────────────────────────────┤
│                 │                               │
│  Monaco Editor  │  Preview Panel                │
│                 │                               │
│  PyMD content   │  Rendered output              │
│  here...        │  (HTML or Markdown)           │
│                 │                               │
│                 │                               │
├─────────────────┴───────────────────────────────┤
│  Status: Saved | Lines: 42 | Words: 256        │ ← Status Bar
└─────────────────────────────────────────────────┘
```

**Alternative Layouts**:
1. **Split View** (default) - Editor + Preview side-by-side
2. **Editor Only** - Full-width editor
3. **Preview Only** - Full-width preview
4. **Tab View** - Tabs to switch between editor and preview

**Components**:
- `DocumentToolbar` - Save, export, settings, layout toggle
- `MonacoEditor` - Code editor with PyMD syntax highlighting
- `DocumentPreview` - Rendered output with live updates
- `EditorStatusBar` - Status information
- `AutoSaveIndicator` - Show auto-save status

**Features**:
- **Auto-save**: Debounced saves every 30 seconds (configurable)
- **Real-time preview**: Re-render on content change (debounced)
- **Syntax highlighting**: PyMD syntax support in Monaco
- **Keyboard shortcuts**: Ctrl+S to save, Ctrl+B for bold, etc.
- **Full-screen mode**: Distraction-free editing
- **Export**: Download as HTML, Markdown, or PDF

**Data Requirements**:
- Document content (API: `GET /documents/:id`)
- Render preview (API: `POST /render/preview`)
- Save document (API: `PATCH /documents/:id`)

**State**:
- Document content (local state + debounced sync)
- Editor settings (Zustand store)
- Save status (local state)
- Preview content (React Query or local state)
- Layout mode (local storage + state)

---

### 6. Settings Pages (`/settings/*`)

**Purpose**: User profile and preferences management

#### 6.1 Profile Settings (`/settings/profile`)

**Layout**:
```
┌──────────────┬──────────────────────────────┐
│              │  Profile                     │
│  Settings    ├──────────────────────────────┤
│  Navigation  │  [Avatar Image]              │
│              │  [Upload new photo]          │
│  • Profile   │                              │
│  • Prefs     │  Name: [____________]        │
│  • Security  │  Email: user@example.com     │
│              │  Bio: [_________________]    │
│              │       [_________________]    │
│              │                              │
│              │  [Save Changes]              │
└──────────────┴──────────────────────────────┘
```

**Components**:
- `SettingsSidebar` - Navigation
- `ProfileForm` - Form with validation
- `AvatarUpload` - Image upload component

**Data Requirements**:
- User profile (API: `GET /users/me`)
- Update profile (API: `PATCH /users/me`)

#### 6.2 Preferences Settings (`/settings/preferences`)

**Layout**:
```
┌──────────────┬──────────────────────────────┐
│              │  Preferences                 │
│  Settings    ├──────────────────────────────┤
│  Navigation  │  Theme                       │
│              │  ○ Light ● Dark ○ Auto       │
│  • Profile   │                              │
│  • Prefs     │  Language                    │
│  • Security  │  [English ▼]                 │
│              │                              │
│              │  Editor Settings             │
│              │  Font Size: [14__] px        │
│              │  Tab Size: [4___] spaces     │
│              │  ☑ Word Wrap                 │
│              │  ☑ Line Numbers              │
│              │                              │
│              │  [Save Changes]              │
└──────────────┴──────────────────────────────┘
```

**Components**:
- `SettingsSidebar`
- `ThemeSelector` - Radio group for theme
- `EditorPreferences` - Editor settings form

**Data Requirements**:
- User settings (API: `GET /users/me/settings`)
- Update settings (API: `PATCH /users/me/settings`)

#### 6.3 Security Settings (`/settings/security`)

**Layout**:
```
┌──────────────┬──────────────────────────────┐
│              │  Security                    │
│  Settings    ├──────────────────────────────┤
│  Navigation  │  Change Password             │
│              │  [Managed by Auth0]          │
│  • Profile   │  [Go to Auth0 →]             │
│  • Prefs     │                              │
│  • Security  │  Two-Factor Authentication   │
│              │  Status: ☑ Enabled           │
│              │  [Manage 2FA →]              │
│              │                              │
│              │  Active Sessions             │
│              │  ┌─────────────────────────┐ │
│              │  │ Chrome - Current        │ │
│              │  │ Safari - 2 hours ago    │ │
│              │  │ [Revoke]                │ │
│              │  └─────────────────────────┘ │
└──────────────┴──────────────────────────────┘
```

**Components**:
- `SettingsSidebar`
- `PasswordSection` - Link to Auth0
- `TwoFactorSection` - 2FA management
- `SessionList` - Active sessions with revoke

**Data Requirements**:
- Active sessions (API: `GET /users/me/sessions`)
- Revoke session (API: `DELETE /sessions/:id`)

---

## Component Architecture

### Component Hierarchy

```
App (Root Layout)
├── AuthProvider (@auth0/nextjs-auth0)
├── QueryProvider (TanStack Query)
├── ThemeProvider (next-themes)
└── ToastProvider (sonner)

Page Layouts
├── PublicLayout (Landing, Login)
│   ├── Header
│   └── Footer
│
└── DashboardLayout (Protected pages)
    ├── DashboardHeader
    │   ├── Logo
    │   ├── Navigation
    │   └── UserMenu
    ├── Sidebar
    │   ├── NavLinks
    │   └── UserProfile
    └── Main Content (children)

Document Editor
├── DocumentToolbar
│   ├── BackButton
│   ├── TitleInput
│   ├── SaveButton
│   └── ActionMenu (Export, Settings)
├── EditorContainer (Split)
│   ├── MonacoEditor
│   │   └── EditorToolbar (Format, Insert)
│   └── DocumentPreview
│       ├── PreviewToolbar (Refresh, Copy)
│       └── PreviewContent
└── EditorStatusBar
    ├── SaveStatus
    ├── WordCount
    └── LineInfo
```

### Reusable UI Components (Shadcn/ui)

**Base Components**:
- `Button` - Primary, secondary, ghost, outline variants
- `Input` - Text input with validation states
- `Textarea` - Multi-line text input
- `Select` - Dropdown select
- `Dialog` - Modal dialog
- `Dropdown Menu` - Dropdown menu
- `Popover` - Popover overlay
- `Toast` - Toast notifications (using sonner)
- `Card` - Content card
- `Badge` - Small badge/tag
- `Avatar` - User avatar
- `Separator` - Visual separator

**Form Components** (React Hook Form):
- `FormField` - Form field wrapper with validation
- `FormLabel` - Accessible form label
- `FormMessage` - Error message display
- `FormDescription` - Help text

**Data Display**:
- `Table` - Data table with sorting
- `Pagination` - Page navigation
- `EmptyState` - Empty state UI
- `Loading` - Loading spinner/skeleton

**Feedback**:
- `Alert` - Alert message (info, success, warning, error)
- `ConfirmDialog` - Confirmation dialog
- `Progress` - Progress bar

---

## State Management

### State Management Strategy

```
┌─────────────────────────────────────────────────┐
│                State Layers                     │
├─────────────────────────────────────────────────┤
│  Server State (TanStack Query)                  │
│  - Documents, User data, Settings               │
│  - Automatic caching, refetching                │
├─────────────────────────────────────────────────┤
│  Client State (Zustand)                         │
│  - UI state (sidebar open, theme)               │
│  - Editor state (cursor position, settings)     │
├─────────────────────────────────────────────────┤
│  Form State (React Hook Form)                   │
│  - Form inputs, validation                      │
├─────────────────────────────────────────────────┤
│  Local Component State (useState)               │
│  - Temporary UI state (hover, focus)            │
│  - Component-specific state                     │
├─────────────────────────────────────────────────┤
│  URL State (Next.js searchParams)               │
│  - Search queries, filters, pagination          │
│  - Shareable state                              │
└─────────────────────────────────────────────────┘
```

### TanStack Query (Server State)

**Configuration**:
```typescript
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      gcTime: 1000 * 60 * 30,   // 30 minutes (cacheTime renamed)
      refetchOnWindowFocus: true,
      retry: 1,
    },
  },
});
```

**Query Keys Structure**:
```typescript
// lib/api/queryKeys.ts
export const queryKeys = {
  users: {
    me: ['users', 'me'] as const,
    settings: ['users', 'me', 'settings'] as const,
  },
  documents: {
    all: ['documents'] as const,
    list: (filters: DocumentFilters) => ['documents', 'list', filters] as const,
    detail: (id: string) => ['documents', 'detail', id] as const,
  },
  render: {
    preview: (content: string, format: string) =>
      ['render', 'preview', content, format] as const,
  },
};
```

**Custom Hooks**:
```typescript
// lib/hooks/useDocuments.ts
export function useDocuments(filters: DocumentFilters) {
  return useQuery({
    queryKey: queryKeys.documents.list(filters),
    queryFn: () => documentsApi.list(filters),
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: queryKeys.documents.detail(id),
    queryFn: () => documentsApi.getById(id),
    enabled: !!id,
  });
}

export function useUpdateDocument() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateDocumentInput) =>
      documentsApi.update(data.id, data),
    onSuccess: (data, variables) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({
        queryKey: queryKeys.documents.detail(variables.id)
      });
      queryClient.invalidateQueries({
        queryKey: queryKeys.documents.all
      });
    },
  });
}
```

### Zustand (Client State)

**UI Store**:
```typescript
// lib/store/uiStore.ts
interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark' | 'auto';
  editorLayout: 'split' | 'editor' | 'preview';

  toggleSidebar: () => void;
  setTheme: (theme: UIState['theme']) => void;
  setEditorLayout: (layout: UIState['editorLayout']) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      theme: 'auto',
      editorLayout: 'split',

      toggleSidebar: () => set((state) => ({
        sidebarOpen: !state.sidebarOpen
      })),
      setTheme: (theme) => set({ theme }),
      setEditorLayout: (layout) => set({ editorLayout: layout }),
    }),
    {
      name: 'pymd-ui-state',
      partialize: (state) => ({
        theme: state.theme,
        editorLayout: state.editorLayout
      }),
    }
  )
);
```

**Editor Store**:
```typescript
// lib/store/editorStore.ts
interface EditorState {
  fontSize: number;
  tabSize: number;
  wordWrap: boolean;
  lineNumbers: boolean;

  setFontSize: (size: number) => void;
  setTabSize: (size: number) => void;
  toggleWordWrap: () => void;
  toggleLineNumbers: () => void;
}

export const useEditorStore = create<EditorState>()(
  persist(
    (set) => ({
      fontSize: 14,
      tabSize: 4,
      wordWrap: true,
      lineNumbers: true,

      setFontSize: (fontSize) => set({ fontSize }),
      setTabSize: (tabSize) => set({ tabSize }),
      toggleWordWrap: () => set((state) => ({
        wordWrap: !state.wordWrap
      })),
      toggleLineNumbers: () => set((state) => ({
        lineNumbers: !state.lineNumbers
      })),
    }),
    { name: 'pymd-editor-settings' }
  )
);
```

### React Hook Form (Form State)

**Example Usage**:
```typescript
// components/ProfileForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  bio: z.string().max(500, 'Bio must be less than 500 characters').optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export function ProfileForm({ user }: { user: User }) {
  const form = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: user.name,
      bio: user.bio || '',
    },
  });

  const updateMutation = useUpdateUser();

  const onSubmit = async (data: ProfileFormData) => {
    await updateMutation.mutateAsync(data);
    toast.success('Profile updated successfully');
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={updateMutation.isPending}>
          Save Changes
        </Button>
      </form>
    </Form>
  );
}
```

---

## Styling Strategy

### Tailwind CSS Configuration

**File: `tailwind.config.ts`**

```typescript
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        // ... other colors
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [
    require('tailwindcss-animate'),
    require('@tailwindcss/typography'),
  ],
};

export default config;
```

### CSS Variables (Design Tokens)

**File: `styles/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    /* ... other variables */

    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 217.2 91.2% 59.8%;
    --primary-foreground: 222.2 47.4% 11.2%;
    /* ... other variables */
  }
}

@layer components {
  .prose-pymd {
    @apply prose prose-slate dark:prose-invert max-w-none;
  }
}
```

### Component Styling Patterns

**1. Using Tailwind Classes**:
```tsx
<button className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90">
  Click me
</button>
```

**2. Using `cn()` Utility for Conditional Classes**:
```tsx
import { cn } from '@/lib/utils/cn';

<button
  className={cn(
    "px-4 py-2 rounded-md",
    variant === 'primary' && "bg-primary text-primary-foreground",
    variant === 'secondary' && "bg-secondary text-secondary-foreground",
    disabled && "opacity-50 cursor-not-allowed"
  )}
>
  Click me
</button>
```

**3. Component Variants (CVA Pattern)**:
```tsx
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input hover:bg-accent",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

interface ButtonProps extends VariantProps<typeof buttonVariants> {
  // ...
}

export function Button({ variant, size, className, ...props }: ButtonProps) {
  return (
    <button
      className={cn(buttonVariants({ variant, size }), className)}
      {...props}
    />
  );
}
```

### Responsive Design

**Breakpoints**:
- `sm`: 640px (mobile landscape)
- `md`: 768px (tablet)
- `lg`: 1024px (laptop)
- `xl`: 1280px (desktop)
- `2xl`: 1536px (large desktop)

**Usage**:
```tsx
<div className="flex flex-col md:flex-row">
  <aside className="w-full md:w-64">Sidebar</aside>
  <main className="flex-1">Content</main>
</div>
```

---

## API Integration

### API Client

**File: `lib/api/client.ts`**

```typescript
import { getAccessToken } from '@auth0/nextjs-auth0';

interface ApiOptions extends RequestInit {
  requiresAuth?: boolean;
}

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  async request<T>(
    endpoint: string,
    options: ApiOptions = {}
  ): Promise<T> {
    const { requiresAuth = true, ...fetchOptions } = options;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...fetchOptions.headers,
    };

    // Add auth token if required
    if (requiresAuth) {
      const { accessToken } = await getAccessToken();
      if (accessToken) {
        headers['Authorization'] = `Bearer ${accessToken}`;
      }
    }

    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...fetchOptions,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText
      }));
      throw new ApiError(response.status, error.message, error);
    }

    return response.json();
  }

  get<T>(endpoint: string, options?: ApiOptions) {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  post<T>(endpoint: string, data?: unknown, options?: ApiOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  patch<T>(endpoint: string, data?: unknown, options?: ApiOptions) {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  delete<T>(endpoint: string, options?: ApiOptions) {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }
}

export const apiClient = new ApiClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
);

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
```

### API Module Example

**File: `lib/api/documents.ts`**

```typescript
import { apiClient } from './client';
import type { Document, CreateDocumentInput, UpdateDocumentInput } from '@/lib/types/document';

export const documentsApi = {
  async list(params: {
    page?: number;
    limit?: number;
    search?: string;
    sort?: string;
  }): Promise<{ items: Document[]; pagination: Pagination }> {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        searchParams.set(key, String(value));
      }
    });

    return apiClient.get(`/documents?${searchParams}`);
  },

  async getById(id: string): Promise<Document> {
    return apiClient.get(`/documents/${id}`);
  },

  async create(data: CreateDocumentInput): Promise<Document> {
    return apiClient.post('/documents', data);
  },

  async update(id: string, data: UpdateDocumentInput): Promise<Document> {
    return apiClient.patch(`/documents/${id}`, data);
  },

  async delete(id: string): Promise<void> {
    return apiClient.delete(`/documents/${id}`);
  },

  async duplicate(id: string): Promise<Document> {
    return apiClient.post(`/documents/${id}/duplicate`);
  },
};
```

---

## Real-time Features

### WebSocket Connection (Optional for MVP)

**For real-time preview updates:**

```typescript
// lib/websocket/client.ts
class WebSocketClient {
  private ws: WebSocket | null = null;
  private listeners: Map<string, Set<Function>> = new Map();

  connect(token: string) {
    this.ws = new WebSocket(`${WS_URL}?token=${token}`);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.emit(message.type, message.data);
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      // Reconnect logic
    };
  }

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  off(event: string, callback: Function) {
    this.listeners.get(event)?.delete(callback);
  }

  private emit(event: string, data: unknown) {
    this.listeners.get(event)?.forEach((callback) => callback(data));
  }

  send(type: string, data: unknown) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    }
  }

  disconnect() {
    this.ws?.close();
    this.ws = null;
  }
}

export const wsClient = new WebSocketClient();
```

**Alternative: Polling for MVP**

Use React Query's `refetchInterval` for simple real-time updates:

```typescript
useQuery({
  queryKey: ['document', id],
  queryFn: () => documentsApi.getById(id),
  refetchInterval: 5000, // Poll every 5 seconds
});
```

---

## Performance Optimization

### Code Splitting

**Dynamic Imports**:
```typescript
// Lazy load Monaco Editor
const MonacoEditor = dynamic(
  () => import('@/components/editor/MonacoEditor'),
  {
    ssr: false,
    loading: () => <Loading message="Loading editor..." />
  }
);
```

### Image Optimization

```tsx
import Image from 'next/image';

<Image
  src="/hero-image.png"
  alt="PyMD Editor"
  width={1200}
  height={600}
  priority // For above-the-fold images
  placeholder="blur"
/>
```

### Memoization

```typescript
import { memo, useMemo, useCallback } from 'react';

// Memoize expensive component
export const DocumentCard = memo(function DocumentCard({ document }: Props) {
  return <div>{document.title}</div>;
});

// Memoize expensive computation
const sortedDocuments = useMemo(() => {
  return documents.sort((a, b) => b.updatedAt - a.updatedAt);
}, [documents]);

// Memoize callback
const handleSave = useCallback(() => {
  saveDocument(content);
}, [content]);
```

### Debouncing

```typescript
import { useDebounce } from '@/lib/hooks/useDebounce';

function DocumentEditor() {
  const [content, setContent] = useState('');
  const debouncedContent = useDebounce(content, 500);

  // Only re-render preview when content stops changing
  useEffect(() => {
    renderPreview(debouncedContent);
  }, [debouncedContent]);
}
```

---

## User Experience

### Loading States

**Skeleton Loaders**:
```tsx
<Card>
  <Skeleton className="h-4 w-3/4" />
  <Skeleton className="h-4 w-1/2 mt-2" />
</Card>
```

### Error States

**Error Boundaries**:
```tsx
// app/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <Button onClick={reset}>Try again</Button>
    </div>
  );
}
```

### Empty States

```tsx
function EmptyDocuments() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <FileIcon className="w-16 h-16 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold">No documents yet</h3>
      <p className="text-muted-foreground mb-4">
        Create your first PyMD document to get started
      </p>
      <Button onClick={createDocument}>
        <PlusIcon className="mr-2" />
        Create Document
      </Button>
    </div>
  );
}
```

### Toast Notifications

```typescript
import { toast } from 'sonner';

// Success
toast.success('Document saved successfully');

// Error
toast.error('Failed to save document');

// Loading
const toastId = toast.loading('Saving document...');
// Later...
toast.success('Document saved', { id: toastId });

// With action
toast('Document deleted', {
  action: {
    label: 'Undo',
    onClick: () => restoreDocument(),
  },
});
```

### Keyboard Shortcuts

```typescript
import { useHotkeys } from 'react-hotkeys-hook';

function DocumentEditor() {
  useHotkeys('ctrl+s, cmd+s', (e) => {
    e.preventDefault();
    saveDocument();
  });

  useHotkeys('ctrl+b, cmd+b', () => {
    insertBold();
  });

  useHotkeys('ctrl+p, cmd+p', () => {
    togglePreview();
  });
}
```

### Accessibility

**Guidelines**:
- Semantic HTML elements
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- Color contrast (WCAG AA minimum)
- Screen reader compatibility

```tsx
<button
  aria-label="Save document"
  aria-pressed={isSaved}
  onClick={saveDocument}
>
  <SaveIcon />
</button>
```

---

**End of Frontend Architecture Plan**
