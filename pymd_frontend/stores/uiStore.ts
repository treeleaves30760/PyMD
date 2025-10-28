import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type ViewMode = 'grid' | 'list'
type SortBy = 'updated_at' | 'created_at' | 'title'
type SortOrder = 'asc' | 'desc'

interface UIState {
  // Document list view mode
  viewMode: ViewMode
  // Document list sort settings
  sortBy: SortBy
  sortOrder: SortOrder
  // Search query
  searchQuery: string
  // Sidebar collapsed state
  sidebarCollapsed: boolean
  // Editor settings
  editorSettings: {
    fontSize: number
    lineHeight: number
    tabSize: number
    wordWrap: boolean
    minimap: boolean
    lineNumbers: boolean
  }

  // Actions
  setViewMode: (mode: ViewMode) => void
  setSortBy: (sortBy: SortBy) => void
  setSortOrder: (order: SortOrder) => void
  setSearchQuery: (query: string) => void
  toggleSidebar: () => void
  updateEditorSettings: (settings: Partial<UIState['editorSettings']>) => void
  reset: () => void
}

const initialState = {
  viewMode: 'grid' as ViewMode,
  sortBy: 'updated_at' as SortBy,
  sortOrder: 'desc' as SortOrder,
  searchQuery: '',
  sidebarCollapsed: false,
  editorSettings: {
    fontSize: 14,
    lineHeight: 1.6,
    tabSize: 2,
    wordWrap: true,
    minimap: true,
    lineNumbers: true,
  },
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      ...initialState,

      setViewMode: (mode) => set({ viewMode: mode }),

      setSortBy: (sortBy) => set({ sortBy }),

      setSortOrder: (order) => set({ sortOrder: order }),

      setSearchQuery: (query) => set({ searchQuery: query }),

      toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),

      updateEditorSettings: (settings) =>
        set((state) => ({
          editorSettings: { ...state.editorSettings, ...settings }
        })),

      reset: () => set(initialState),
    }),
    {
      name: 'pymd-ui-storage',
    }
  )
)
