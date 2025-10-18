import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-3xl text-center">
        <h1 className="text-5xl font-bold mb-6">
          Welcome to PyMD
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          Create, edit, and execute PyMD documents with real-time collaboration.
          A powerful platform for Python-based markdown with live code execution.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/api/auth/login">
            <Button size="lg">Get Started</Button>
          </Link>
          <Link href="/docs">
            <Button size="lg" variant="outline">
              Learn More
            </Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
