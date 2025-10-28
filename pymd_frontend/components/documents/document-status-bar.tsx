'use client'

import { useEditorStore } from '@/stores/editorStore'
import { formatDistanceToNow } from 'date-fns'
import { Clock, FileText, Hash } from 'lucide-react'

export function DocumentStatusBar() {
  const { cursorPosition, wordCount, charCount, lastSaved, autoSaveEnabled } = useEditorStore()

  return (
    <div className="flex h-8 items-center justify-between border-t bg-muted/50 px-4 text-xs text-muted-foreground">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1">
          <FileText className="h-3 w-3" />
          <span>{wordCount} words</span>
        </div>

        <div className="flex items-center gap-1">
          <Hash className="h-3 w-3" />
          <span>{charCount} characters</span>
        </div>

        <div>
          Ln {cursorPosition.line}, Col {cursorPosition.column}
        </div>
      </div>

      <div className="flex items-center gap-4">
        {autoSaveEnabled && (
          <span className="text-green-600 dark:text-green-400">Auto-save enabled</span>
        )}

        {lastSaved && (
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span>
              Saved {formatDistanceToNow(lastSaved, { addSuffix: true })}
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
