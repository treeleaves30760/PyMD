'use client'

import { use, useCallback, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels'
import { DocumentEditor } from '@/components/documents/document-editor'
import { DocumentPreview } from '@/components/documents/document-preview'
import { DocumentToolbar } from '@/components/documents/document-toolbar'
import { DocumentStatusBar } from '@/components/documents/document-status-bar'
import { useDocument, useUpdateDocument, useExportDocument } from '@/hooks/useDocuments'
import { useEditorStore } from '@/stores/editorStore'
import { useToast } from '@/hooks/use-toast'
import { Loader2, ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'
import Link from 'next/link'

export default function DocumentPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  const router = useRouter()
  const { toast } = useToast()
  const [localContent, setLocalContent] = useState('')
  const [hasLoaded, setHasLoaded] = useState(false)
  const [forceRenderTrigger, setForceRenderTrigger] = useState(0)

  // Editor store
  const { showPreview, isFullScreen, autoSaveEnabled, markAsSaved, reset } = useEditorStore()

  // Fetch document
  const { data: document, isLoading, error } = useDocument(id)

  // Update mutation
  const updateMutation = useUpdateDocument()

  // Export mutation
  const exportMutation = useExportDocument()

  // Initialize content when document loads
  useEffect(() => {
    if (document && !hasLoaded) {
      setLocalContent(document.content)
      setHasLoaded(true)
    }
  }, [document, hasLoaded])

  // Auto-save functionality
  useEffect(() => {
    if (!autoSaveEnabled || !hasLoaded) return

    const autoSaveInterval = setInterval(() => {
      if (localContent !== document?.content) {
        handleSave()
      }
    }, 30000) // Auto-save every 30 seconds

    return () => clearInterval(autoSaveInterval)
  }, [autoSaveEnabled, localContent, document?.content, hasLoaded])

  // Clean up on unmount
  useEffect(() => {
    return () => {
      reset()
    }
  }, [reset])

  const handleSave = useCallback(async () => {
    if (!document) return

    try {
      await updateMutation.mutateAsync({
        id: document.id,
        data: { content: localContent }
      })
      markAsSaved()
      toast({
        title: 'Document saved',
        description: 'Your changes have been saved successfully.',
      })
    } catch (error) {
      toast({
        variant: 'destructive',
        title: 'Save failed',
        description: 'Failed to save document. Please try again.',
      })
    }
  }, [document, localContent, updateMutation, markAsSaved, toast])

  const handleExport = useCallback(async (format: 'html' | 'markdown' | 'json') => {
    if (!document) return

    try {
      await exportMutation.mutateAsync({
        id: document.id,
        title: document.title,
        format,
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
  }, [document, exportMutation, toast])

  const handleReRender = useCallback(() => {
    setForceRenderTrigger(prev => prev + 1)
    toast({
      title: 'Re-rendering',
      description: 'Forcing preview to re-render...',
    })
  }, [toast])

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (error || !document) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4">
        <h1 className="text-2xl font-bold">Document not found</h1>
        <p className="text-muted-foreground">
          The document you're looking for doesn't exist or you don't have permission to view it.
        </p>
        <Button asChild>
          <Link href="/documents">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Documents
          </Link>
        </Button>
      </div>
    )
  }

  return (
    <div className={`flex flex-col ${isFullScreen ? 'h-screen' : 'h-[calc(100vh-4rem)]'}`}>
      {/* Toolbar */}
      <DocumentToolbar
        onSave={handleSave}
        onExport={handleExport}
        onReRender={handleReRender}
        isSaving={updateMutation.isPending}
        documentId={document.id}
      />

      {/* Editor and Preview */}
      <div className="flex-1 overflow-hidden">
        {showPreview ? (
          <PanelGroup direction="horizontal">
            <Panel defaultSize={50} minSize={30}>
              <DocumentEditor
                value={localContent}
                onChange={setLocalContent}
              />
            </Panel>
            <PanelResizeHandle className="w-2 bg-border hover:bg-primary/20 transition-colors" />
            <Panel defaultSize={50} minSize={30}>
              <DocumentPreview content={localContent} forceRenderTrigger={forceRenderTrigger} />
            </Panel>
          </PanelGroup>
        ) : (
          <DocumentEditor
            value={localContent}
            onChange={setLocalContent}
          />
        )}
      </div>

      {/* Status Bar */}
      <DocumentStatusBar />
    </div>
  )
}
