import { FileText, PlusCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

interface DocumentEmptyStateProps {
  hasSearchQuery?: boolean
  onClearSearch?: () => void
}

export function DocumentEmptyState({ hasSearchQuery, onClearSearch }: DocumentEmptyStateProps) {
  if (hasSearchQuery) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <FileText className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No documents found</h3>
        <p className="text-muted-foreground mb-4">
          We couldn't find any documents matching your search.
        </p>
        {onClearSearch && (
          <Button variant="outline" onClick={onClearSearch}>
            Clear search
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <FileText className="h-12 w-12 text-muted-foreground mb-4" />
      <h3 className="text-lg font-semibold mb-2">No documents yet</h3>
      <p className="text-muted-foreground mb-4">
        Get started by creating your first PyMD document.
      </p>
      <Button asChild>
        <Link href="/documents/new">
          <PlusCircle className="mr-2 h-4 w-4" />
          Create Document
        </Link>
      </Button>
    </div>
  )
}
