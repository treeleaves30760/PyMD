import { handleAuth, handleLogin, handleCallback } from '@auth0/nextjs-auth0'
import { NextRequest, NextResponse } from 'next/server'

const authHandlers = handleAuth({
  login: handleLogin({
    returnTo: '/dashboard',
    authorizationParams: {
      prompt: 'select_account',
    },
  }),
  async logout(_req: NextRequest) {
    // Custom logout handler to force Auth0 logout
    // NOTE: We do NOT use 'federated' parameter to avoid logging out from Google/social providers
    // This only clears Auth0 session, allowing users to switch accounts without losing their Google session

    // Build Auth0 logout URL (without federated parameter)
    const auth0Domain = process.env.AUTH0_ISSUER_BASE_URL
    const clientId = process.env.AUTH0_CLIENT_ID
    const returnTo = encodeURIComponent(`${process.env.AUTH0_BASE_URL}/`)

    const logoutUrl = `${auth0Domain}/v2/logout?client_id=${clientId}&returnTo=${returnTo}`

    // Clear the session cookie
    const response = NextResponse.redirect(logoutUrl)
    response.cookies.delete('appSession')

    return response
  },
  callback: handleCallback({
    async afterCallback(_req: any, session: any) {
      // Sync user with backend
      // Use internal Docker network URL for server-side requests
      const backendUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      if (backendUrl && session.user) {
        try {
          await fetch(`${backendUrl}/api/v1/auth/callback`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${session.accessToken}`,
            },
            body: JSON.stringify({
              sub: session.user.sub,
              email: session.user.email,
              name: session.user.name,
              picture: session.user.picture,
              email_verified: session.user.email_verified,
            }),
          })
        } catch (error) {
          console.error('Failed to sync user with backend:', error)
        }
      }
      return session
    },
  }),
})

// Wrapper to handle async params for Next.js 15
export async function GET(
  request: NextRequest,
  context: { params: Promise<{ auth0: string }> }
) {
  // Await params to satisfy Next.js 15 requirement
  const params = await context.params

  // Create a modified context with the resolved params
  const modifiedContext = {
    params: params as any, // Auth0 SDK expects sync params
  }

  return authHandlers(request, modifiedContext)
}
