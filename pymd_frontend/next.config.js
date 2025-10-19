/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',

  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000'],
    },
  },

  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL,
  },

  // Rewrites removed - using API route handler instead for proper authentication
  // See /app/api/backend/[...path]/route.ts
}

module.exports = nextConfig
