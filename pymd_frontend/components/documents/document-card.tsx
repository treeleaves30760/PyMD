'use client'

import { Document } from '@/types/document'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { formatDistanceToNow } from 'date-fns'
import { FileText, MoreVertical, Edit, Copy, Download, Trash2 } from 'lucide-react'
import Link from 'next/link'

interface DocumentCardProps {
  document: Document
  onDelete?: (id: string) => void
  onDuplicate?: (id: string) => void
  onExport?: (id: string, format: 'html' | 'markdown') => void
  viewMode?: 'grid' | 'list'
}

export function DocumentCard({
  document,
  onDelete,
  onDuplicate,
  onExport,
  viewMode = 'grid'
}: DocumentCardProps) {
  const updatedAt = new Date(document.updated_at)
  const contentPreview = document.content.slice(0, 150) + (document.content.length > 150 ? '...' : '')

  if (viewMode === 'list') {
    return (
      <Card className="hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between p-4">
          <Link href={`/documents/${document.id}`} className="flex-1">
            <div className="flex items-start gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
                <FileText className="h-5 w-5 text-primary" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold hover:text-primary transition-colors">
                  {document.title}
                </h3>
                <p className="text-sm text-muted-foreground line-clamp-1">
                  {contentPreview}
                </p>
                <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                  <span>Updated {formatDistanceToNow(updatedAt, { addSuffix: true })}</span>
                </div>
              </div>
            </div>
          </Link>
          <DocumentActions
            document={document}
            onDelete={onDelete}
            onDuplicate={onDuplicate}
            onExport={onExport}
          />
        </div>
      </Card>
    )
  }

  return (
    <Card className="group hover:shadow-md transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-primary/10">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1">
              <CardTitle className="text-lg">
                <Link
                  href={`/documents/${document.id}`}
                  className="hover:text-primary transition-colors"
                >
                  {document.title}
                </Link>
              </CardTitle>
            </div>
          </div>
          <DocumentActions
            document={document}
            onDelete={onDelete}
            onDuplicate={onDuplicate}
            onExport={onExport}
          />
        </div>
        <CardDescription className="line-clamp-2 mt-2">
          {contentPreview}
        </CardDescription>
      </CardHeader>
      <CardFooter className="flex items-center justify-between text-xs text-muted-foreground">
        <span>Updated {formatDistanceToNow(updatedAt, { addSuffix: true })}</span>
      </CardFooter>
    </Card>
  )
}

function DocumentActions({
  document,
  onDelete,
  onDuplicate,
  onExport,
}: {
  document: Document
  onDelete?: (id: string) => void
  onDuplicate?: (id: string) => void
  onExport?: (id: string, format: 'html' | 'markdown') => void
}) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="h-8 w-8">
          <MoreVertical className="h-4 w-4" />
          <span className="sr-only">Open menu</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem asChild>
          <Link href={`/documents/${document.id}`}>
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Link>
        </DropdownMenuItem>
        {onDuplicate && (
          <DropdownMenuItem onClick={() => onDuplicate(document.id)}>
            <Copy className="mr-2 h-4 w-4" />
            Duplicate
          </DropdownMenuItem>
        )}
        <DropdownMenuSeparator />
        {onExport && (
          <>
            <DropdownMenuItem onClick={() => onExport(document.id, 'html')}>
              <Download className="mr-2 h-4 w-4" />
              Export as HTML
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onExport(document.id, 'markdown')}>
              <Download className="mr-2 h-4 w-4" />
              Export as Markdown
            </DropdownMenuItem>
            <DropdownMenuSeparator />
          </>
        )}
        {onDelete && (
          <DropdownMenuItem
            onClick={() => onDelete(document.id)}
            className="text-destructive focus:text-destructive"
          >
            <Trash2 className="mr-2 h-4 w-4" />
            Delete
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
