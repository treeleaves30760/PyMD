import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'

interface DocumentSkeletonProps {
  viewMode?: 'grid' | 'list'
}

export function DocumentSkeleton({ viewMode = 'grid' }: DocumentSkeletonProps) {
  if (viewMode === 'list') {
    return (
      <Card>
        <div className="flex items-center justify-between p-4">
          <div className="flex items-start gap-4 flex-1">
            <Skeleton className="h-10 w-10 rounded-md" />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-5 w-1/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-3 w-1/4" />
            </div>
          </div>
          <Skeleton className="h-8 w-8" />
        </div>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2 flex-1">
            <Skeleton className="h-10 w-10 rounded-md" />
            <Skeleton className="h-5 w-2/3" />
          </div>
          <Skeleton className="h-8 w-8" />
        </div>
        <div className="space-y-2 mt-2">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-4/5" />
        </div>
      </CardHeader>
      <CardFooter className="flex items-center justify-between">
        <Skeleton className="h-3 w-1/4" />
        <Skeleton className="h-5 w-16" />
      </CardFooter>
    </Card>
  )
}

export function DocumentListSkeleton({ count = 6, viewMode = 'grid' }: { count?: number; viewMode?: 'grid' | 'list' }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <DocumentSkeleton key={i} viewMode={viewMode} />
      ))}
    </>
  )
}
