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
    const debugUrl = process.env.DEBUG_SERVICE_URL || 'http://debug-service:8000'
    const reviewUrl = process.env.CODE_REVIEW_SERVICE_URL || 'http://code-review-service:8000'
    const progressUrl = process.env.PROGRESS_SERVICE_URL || 'http://progress-service:8000'

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
      {
        source: '/api/debug/:path*',
        destination: `${debugUrl}/api/debug/:path*`,
      },
      {
        source: '/api/review/:path*',
        destination: `${reviewUrl}/api/review/:path*`,
      },
      {
        source: '/api/progress/:path*',
        destination: `${progressUrl}/api/progress/:path*`,
      },
      {
        source: '/api/curriculum/:path*',
        destination: `${progressUrl}/api/curriculum/:path*`,
      },
      {
        source: '/api/quizzes/:path*',
        destination: `${exerciseUrl}/api/quizzes/:path*`,
      },
    ]
  },
}

module.exports = nextConfig
