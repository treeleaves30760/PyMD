'use client'

import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { useEditorStore } from '@/stores/editorStore'
import {
  Save,
  Download,
  Eye,
  EyeOff,
  Maximize,
  Minimize,
  FileText,
  Settings,
} from 'lucide-react'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'

interface DocumentToolbarProps {
  onSave: () => void
  onExport: (format: 'html' | 'markdown' | 'json') => void
  isSaving?: boolean
  documentId?: string
}

export function DocumentToolbar({
  onSave,
  onExport,
  isSaving = false,
  documentId,
}: DocumentToolbarProps) {
  const {
    isDirty,
    isFullScreen,
    showPreview,
    toggleFullScreen,
    togglePreview,
  } = useEditorStore()

  return (
    <div className="flex h-14 items-center justify-between border-b bg-background px-4">
      <div className="flex items-center gap-2">
        <Button
          variant="default"
          size="sm"
          onClick={onSave}
          disabled={!isDirty || isSaving}
        >
          <Save className="mr-2 h-4 w-4" />
          {isSaving ? 'Saving...' : 'Save'}
        </Button>

        <Separator orientation="vertical" className="h-6" />

        <Button
          variant="ghost"
          size="sm"
          onClick={togglePreview}
          title={showPreview ? 'Hide Preview' : 'Show Preview'}
        >
          {showPreview ? (
            <>
              <EyeOff className="mr-2 h-4 w-4" />
              Hide Preview
            </>
          ) : (
            <>
              <Eye className="mr-2 h-4 w-4" />
              Show Preview
            </>
          )}
        </Button>

        <Button
          variant="ghost"
          size="sm"
          onClick={toggleFullScreen}
          title={isFullScreen ? 'Exit Full Screen' : 'Full Screen'}
        >
          {isFullScreen ? (
            <Minimize className="h-4 w-4" />
          ) : (
            <Maximize className="h-4 w-4" />
          )}
        </Button>

        <Separator orientation="vertical" className="h-6" />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="start">
            <DropdownMenuItem onClick={() => onExport('html')}>
              <FileText className="mr-2 h-4 w-4" />
              Export as HTML
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onExport('markdown')}>
              <FileText className="mr-2 h-4 w-4" />
              Export as Markdown
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => onExport('json')}>
              <FileText className="mr-2 h-4 w-4" />
              Export as JSON
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <div className="flex items-center gap-2">
        {isDirty && (
          <span className="text-sm text-muted-foreground">Unsaved changes</span>
        )}
      </div>
    </div>
  )
}
