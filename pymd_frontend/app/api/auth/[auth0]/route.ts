import { handleAuth, handleLogin, handleCallback } from '@auth0/nextjs-auth0'

export const GET = handleAuth({
  login: handleLogin({
    returnTo: '/dashboard',
  }),
  callback: handleCallback({
    async afterCallback(req, session) {
      // Sync user with backend
      const backendUrl = process.env.NEXT_PUBLIC_API_URL
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
