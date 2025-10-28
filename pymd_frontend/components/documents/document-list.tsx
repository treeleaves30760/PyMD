'use client'

import { DocumentCard } from './document-card'
import { DocumentListSkeleton } from './document-skeleton'
import { DocumentEmptyState } from './document-empty-state'
import { Document } from '@/types/document'
import { useUIStore } from '@/stores/uiStore'

interface DocumentListProps {
  documents: Document[]
  isLoading?: boolean
  hasSearchQuery?: boolean
  onClearSearch?: () => void
  onDelete?: (id: string) => void
  onDuplicate?: (id: string) => void
  onExport?: (id: string, format: 'html' | 'markdown') => void
}

export function DocumentList({
  documents,
  isLoading,
  hasSearchQuery,
  onClearSearch,
  onDelete,
  onDuplicate,
  onExport,
}: DocumentListProps) {
  const { viewMode } = useUIStore()

  if (isLoading) {
    return (
      <div className={viewMode === 'grid' ? 'grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3' : 'space-y-4'}>
        <DocumentListSkeleton count={6} viewMode={viewMode} />
      </div>
    )
  }

  if (documents.length === 0) {
    return <DocumentEmptyState hasSearchQuery={hasSearchQuery} onClearSearch={onClearSearch} />
  }

  return (
    <div className={viewMode === 'grid' ? 'grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3' : 'space-y-4'}>
      {documents.map((document) => (
        <DocumentCard
          key={document.id}
          document={document}
          viewMode={viewMode}
          onDelete={onDelete}
          onDuplicate={onDuplicate}
          onExport={onExport}
        />
      ))}
    </div>
  )
}
