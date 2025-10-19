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

  async rewrites() {
    const apiUrl = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/backend/:path*',
        destination: `${apiUrl}/api/v1/:path*`,
      },
    ];
  },
}

module.exports = nextConfig
