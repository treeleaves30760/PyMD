'use client'

import { useState, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import {
  useDocuments,
  useDeleteDocument,
  useDuplicateDocument,
  useExportDocument,
} from '@/hooks/useDocuments'
import { DocumentList } from '@/components/documents/document-list'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useUIStore } from '@/stores/uiStore'
import { useToast } from '@/hooks/use-toast'
import { PlusCircle, Search, Grid3x3, List, SortAsc, SortDesc } from 'lucide-react'
import Link from 'next/link'
import { useDebounce } from '@/hooks/useDebounce'

export default function DocumentsPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [searchInput, setSearchInput] = useState('')
  const debouncedSearch = useDebounce(searchInput, 300)

  const { viewMode, sortBy, sortOrder, setViewMode, setSortBy, setSortOrder } = useUIStore()

  // Fetch documents
  const {
    data: documentsData,
    isLoading,
    error,
  } = useDocuments({
    page: 1,
    page_size: 50,
    search: debouncedSearch,
    sort_by: sortBy,
    sort_order: sortOrder,
  })

  const deleteMutation = useDeleteDocument()
  const duplicateMutation = useDuplicateDocument()
  const exportMutation = useExportDocument()

  const documents = documentsData?.documents || []

  const handleDelete = useCallback(
    async (id: string) => {
      if (!confirm('Are you sure you want to delete this document?')) return

      try {
        await deleteMutation.mutateAsync(id)
        toast({
          title: 'Document deleted',
          description: 'The document has been deleted successfully.',
        })
      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Delete failed',
          description: 'Failed to delete document. Please try again.',
        })
      }
    },
    [deleteMutation, toast]
  )

  const handleDuplicate = useCallback(
    async (id: string) => {
      try {
        const newDocument = await duplicateMutation.mutateAsync(id)
        toast({
          title: 'Document duplicated',
          description: 'The document has been duplicated successfully.',
        })
        router.push(`/documents/${newDocument.id}`)
      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Duplicate failed',
          description: 'Failed to duplicate document. Please try again.',
        })
      }
    },
    [duplicateMutation, toast, router]
  )

  const handleExport = useCallback(
    async (id: string, format: 'html' | 'markdown') => {
      try {
        const document = documents.find((d) => d.id === id)
        if (!document) return

        await exportMutation.mutateAsync({
          id,
          title: document.title,
          format
        })

        toast({
          title: 'Export successful',
          description: `Document exported as ${format.toUpperCase()}`,
        })
      } catch (error) {
        toast({
          variant: 'destructive',
          title: 'Export failed',
          description: 'Failed to export document. Please try again.',
        })
      }
    },
    [exportMutation, documents, toast]
  )

  const handleClearSearch = useCallback(() => {
    setSearchInput('')
  }, [])

  const toggleSortOrder = useCallback(() => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
  }, [sortOrder, setSortOrder])

  return (
    <div className="container mx-auto py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">My Documents</h1>
        <p className="text-muted-foreground">
          Create, edit, and manage your PyMD documents
        </p>
      </div>

      {/* Toolbar */}
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 items-center gap-2">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search documents..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              className="pl-9"
            />
          </div>

          <Select value={sortBy} onValueChange={(value: any) => setSortBy(value)}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="updated_at">Last Updated</SelectItem>
              <SelectItem value="created_at">Date Created</SelectItem>
              <SelectItem value="title">Title</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="icon"
            onClick={toggleSortOrder}
            title={sortOrder === 'asc' ? 'Ascending' : 'Descending'}
          >
            {sortOrder === 'asc' ? (
              <SortAsc className="h-4 w-4" />
            ) : (
              <SortDesc className="h-4 w-4" />
            )}
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 border rounded-md p-1">
            <Button
              variant={viewMode === 'grid' ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setViewMode('grid')}
              className="h-8 w-8"
            >
              <Grid3x3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'secondary' : 'ghost'}
              size="icon"
              onClick={() => setViewMode('list')}
              className="h-8 w-8"
            >
              <List className="h-4 w-4" />
            </Button>
          </div>

          <Button asChild>
            <Link href="/documents/new">
              <PlusCircle className="mr-2 h-4 w-4" />
              New Document
            </Link>
          </Button>
        </div>
      </div>

      {/* Document List */}
      {error ? (
        <div className="text-center py-12">
          <p className="text-destructive">Failed to load documents. Please try again.</p>
        </div>
      ) : (
        <DocumentList
          documents={documents}
          isLoading={isLoading}
          hasSearchQuery={!!debouncedSearch}
          onClearSearch={handleClearSearch}
          onDelete={handleDelete}
          onDuplicate={handleDuplicate}
          onExport={handleExport}
        />
      )}

      {/* Pagination (if needed later) */}
      {documentsData && documentsData.total > documentsData.page_size && (
        <div className="mt-8 flex items-center justify-center gap-2">
          <p className="text-sm text-muted-foreground">
            Showing {documents.length} of {documentsData.total} documents
          </p>
        </div>
      )}
    </div>
  )
}
