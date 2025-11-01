'use client'

import { useEffect, useState } from 'react'
import { useRenderPreview } from '@/hooks/useDocuments'
import { Loader2, AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

interface DocumentPreviewProps {
  content: string
  forceRenderTrigger?: number
}

export function DocumentPreview({ content, forceRenderTrigger }: DocumentPreviewProps) {
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

  // Force re-render when trigger changes
  useEffect(() => {
    if (forceRenderTrigger !== undefined && forceRenderTrigger > 0 && content) {
      renderPreview({ content })
    }
  }, [forceRenderTrigger, content, renderPreview])

  if (isPending) {
    return (
      <div className="preview-panel flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="preview-panel p-4 h-full">
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
      <div className="preview-panel flex h-full items-center justify-center">
        <p className="text-muted-foreground">Start typing to see preview...</p>
      </div>
    )
  }

  return (
    <div className="preview-panel h-full overflow-auto">
      <div
        className="prose max-w-none p-6"
        dangerouslySetInnerHTML={{ __html: data.rendered }}
      />
    </div>
  )
}
