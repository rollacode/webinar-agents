import type { NextConfig } from 'next'

const nextConfig: NextConfig = {
  // Serve static assets from the medieval-war directory
  async rewrites() {
    return [
      {
        source: '/medieval-war/:path*',
        destination: '/api/medieval-war/:path*',
      },
    ]
  },
  // Copy medieval-war assets to public during build
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        path: false,
      }
    }
    return config
  },
}

export default nextConfig
