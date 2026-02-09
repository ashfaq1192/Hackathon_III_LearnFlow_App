/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    serverComponentsExternalPackages: ['pg'],
  },
  async rewrites() {
    const triageUrl = process.env.TRIAGE_SERVICE_URL || 'http://triage-service:8000'
    const conceptsUrl = process.env.CONCEPTS_SERVICE_URL || 'http://concepts-service:8000'
    const exerciseUrl = process.env.EXERCISE_SERVICE_URL || 'http://exercise-service:8000'
    const executeUrl = process.env.CODE_EXECUTION_SERVICE_URL || 'http://code-execution-service:8000'

    return [
      {
        source: '/api/triage/:path*',
        destination: `${triageUrl}/api/triage/:path*`,
      },
      {
        source: '/api/concepts/:path*',
        destination: `${conceptsUrl}/api/concepts/:path*`,
      },
      {
        source: '/api/exercises/:path*',
        destination: `${exerciseUrl}/api/exercises/:path*`,
      },
      {
        source: '/api/execute/:path*',
        destination: `${executeUrl}/api/execute/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
