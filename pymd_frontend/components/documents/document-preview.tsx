'use client'

import { useEffect, useState } from 'react'
import { useRenderPreview } from '@/hooks/useDocuments'
import { Loader2, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

interface DocumentPreviewProps {
  content: string
}

export function DocumentPreview({ content }: DocumentPreviewProps) {
  const [debouncedContent, setDebouncedContent] = useState(content)
  const { mutate: renderPreview, data, isPending, error } = useRenderPreview()

  // Debounce content changes
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedContent(content)
    }, 500)

    return () => clearTimeout(timer)
  }, [content])

  // Render when debounced content changes
  useEffect(() => {
    if (debouncedContent) {
      renderPreview({ content: debouncedContent })
    }
  }, [debouncedContent, renderPreview])

  if (isPending) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Preview Error</AlertTitle>
          <AlertDescription>
            {error.message || 'Failed to render preview'}
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  if (!data?.rendered) {
    return (
      <div className="flex h-full items-center justify-center text-muted-foreground">
        <p>Start typing to see preview...</p>
      </div>
    )
  }

  return (
    <div className="h-full overflow-auto">
      <div
        className="prose prose-slate dark:prose-invert max-w-none p-6"
        dangerouslySetInnerHTML={{ __html: data.rendered }}
      />
    </div>
  )
}
