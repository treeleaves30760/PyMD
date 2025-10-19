'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from '@auth0/nextjs-auth0/client'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import { useCreateDocument } from '@/hooks/useDocuments'

export default function NewDocumentPage() {
  const router = useRouter()
  const { user, isLoading } = useUser()
  const [title, setTitle] = useState('')

  const createDocument = useCreateDocument()

  if (isLoading) {
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
    return null // Middleware will redirect
  }

  const handleCreate = async () => {
    if (!title.trim()) {
      alert('Please enter a document title')
      return
    }

    try {
      const document = await createDocument.mutateAsync({
        title: title.trim(),
        content: `# ${title.trim()}\n\nStart writing your PyMD document here...\n\n\`\`\`python\n# You can add Python code blocks like this\nprint("Hello, PyMD!")\n\`\`\`\n`,
        render_format: 'html',
      })

      router.push(`/documents/${document.id}`)
    } catch (error) {
      console.error('Error creating document:', error)
      alert('Failed to create document. Please try again.')
    }
  }

  return (
    <div className="container max-w-4xl mx-auto py-8">
      <div className="mb-6">
        <Link href="/dashboard">
          <Button variant="ghost" size="sm">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </Link>
      </div>

      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Create New Document</h1>
          <p className="text-muted-foreground mt-2">
            Create a new PyMD document with Python code execution capabilities
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label htmlFor="title" className="block text-sm font-medium mb-2">
              Document Title
            </label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter document title..."
              className="w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              autoFocus
            />
          </div>

          <div className="flex gap-4">
            <Button
              onClick={handleCreate}
              disabled={createDocument.isPending || !title.trim()}
              size="lg"
            >
              {createDocument.isPending ? 'Creating...' : 'Create Document'}
            </Button>
            <Link href="/dashboard">
              <Button variant="outline" size="lg">
                Cancel
              </Button>
            </Link>
          </div>
        </div>

        <div className="rounded-lg border p-6 bg-muted/50">
          <h3 className="font-semibold mb-2">What you can do with PyMD:</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
            <li>Write documentation with executable Python code blocks</li>
            <li>Create interactive tutorials and demos</li>
            <li>Share data analysis notebooks with real-time execution</li>
            <li>Collaborate with others in real-time</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
