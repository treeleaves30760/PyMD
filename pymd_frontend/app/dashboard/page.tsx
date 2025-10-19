'use client'

import { useUser } from '@auth0/nextjs-auth0/client'
import { Button } from '@/components/ui/button'
import { FileText, Plus, Calendar, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { useDocuments } from '@/hooks/useDocuments'

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useUser()

  // Fetch recent documents (limited to 5 for dashboard)
  const { data: documentsData, isLoading: docsLoading } = useDocuments({
    page: 1,
    page_size: 5,
    sort_by: 'updated_at',
    sort_order: 'desc',
  })

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Middleware will redirect, but this prevents flash
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-muted-foreground">
            Manage your PyMD documents and projects
          </p>
        </div>
        <Link href="/documents/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Document
          </Button>
        </Link>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="rounded-lg border bg-card p-6">
          <div className="flex items-center space-x-4">
            <FileText className="h-8 w-8 text-primary" />
            <div>
              <p className="text-sm font-medium text-muted-foreground">
                Total Documents
              </p>
              {docsLoading ? (
                <div className="flex items-center gap-2">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="text-sm">Loading...</span>
                </div>
              ) : (
                <h3 className="text-2xl font-bold">{documentsData?.total || 0}</h3>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Documents</h2>
          {documentsData && documentsData.total > 0 && (
            <Link href="/documents">
              <Button variant="ghost" size="sm">
                View All
              </Button>
            </Link>
          )}
        </div>

        {docsLoading ? (
          <div className="text-center py-12">
            <Loader2 className="mx-auto h-12 w-12 mb-4 animate-spin text-primary" />
            <p className="text-muted-foreground">Loading documents...</p>
          </div>
        ) : documentsData && documentsData.documents.length > 0 ? (
          <div className="space-y-2">
            {documentsData.documents.map((doc) => (
              <Link
                key={doc.id}
                href={`/documents/${doc.id}`}
                className="block p-4 rounded-lg border hover:bg-accent transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium">{doc.title}</h3>
                    <div className="flex items-center gap-4 mt-1 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {formatDate(doc.updated_at)}
                      </span>
                      <span className="capitalize">{doc.render_format}</span>
                    </div>
                  </div>
                  <FileText className="h-5 w-5 text-muted-foreground" />
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground">
            <FileText className="mx-auto h-12 w-12 mb-4 opacity-20" />
            <p>No documents yet</p>
            <p className="text-sm">Create your first PyMD document to get started</p>
          </div>
        )}
      </div>
    </div>
  )
}
