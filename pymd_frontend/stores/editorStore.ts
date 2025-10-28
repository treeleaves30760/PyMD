import { create } from 'zustand'

interface EditorState {
  // Current document content
  content: string
  // Whether content has unsaved changes
  isDirty: boolean
  // Whether editor is in full-screen mode
  isFullScreen: boolean
  // Whether preview is visible
  showPreview: boolean
  // Current cursor position
  cursorPosition: { line: number; column: number }
  // Word count
  wordCount: number
  // Character count
  charCount: number
  // Whether auto-save is enabled
  autoSaveEnabled: boolean
  // Last saved timestamp
  lastSaved: Date | null

  // Actions
  setContent: (content: string) => void
  setIsDirty: (isDirty: boolean) => void
  toggleFullScreen: () => void
  togglePreview: () => void
  setCursorPosition: (position: { line: number; column: number }) => void
  updateCounts: (wordCount: number, charCount: number) => void
  toggleAutoSave: () => void
  markAsSaved: () => void
  reset: () => void
}

const initialState = {
  content: '',
  isDirty: false,
  isFullScreen: false,
  showPreview: true,
  cursorPosition: { line: 1, column: 1 },
  wordCount: 0,
  charCount: 0,
  autoSaveEnabled: true,
  lastSaved: null,
}

export const useEditorStore = create<EditorState>((set) => ({
  ...initialState,

  setContent: (content) => set({ content, isDirty: true }),

  setIsDirty: (isDirty) => set({ isDirty }),

  toggleFullScreen: () => set((state) => ({ isFullScreen: !state.isFullScreen })),

  togglePreview: () => set((state) => ({ showPreview: !state.showPreview })),

  setCursorPosition: (position) => set({ cursorPosition: position }),

  updateCounts: (wordCount, charCount) => set({ wordCount, charCount }),

  toggleAutoSave: () => set((state) => ({ autoSaveEnabled: !state.autoSaveEnabled })),

  markAsSaved: () => set({ isDirty: false, lastSaved: new Date() }),

  reset: () => set(initialState),
}))
