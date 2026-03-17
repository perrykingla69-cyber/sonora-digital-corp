/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  basePath: '/panel',
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://sonoradigitalcorp.com/api',
  },
}

module.exports = nextConfig
