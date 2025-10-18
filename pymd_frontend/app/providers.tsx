'use client'

import { UserProvider } from '@auth0/nextjs-auth0/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
          },
        },
      })
  )

  return (
    <UserProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </UserProvider>
  )
}
