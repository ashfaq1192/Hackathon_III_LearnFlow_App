'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const res = await fetch('/api/auth/sign-in/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.message || 'Login failed')
      }

      window.location.href = '/'
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }

  const handleOAuth = (provider: string) => {
    window.location.href = `/api/auth/sign-in/${provider}`
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="max-w-md w-full p-8 bg-slate-800 rounded-lg shadow-lg border border-slate-700">
        <h1 className="text-2xl font-bold text-center mb-6 text-white">Login to LearnFlow</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-900/50 text-red-300 rounded border border-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-slate-300">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-slate-300">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* OAuth providers - uncomment when credentials are configured
        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-600"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-slate-800 text-slate-400">Or continue with</span>
            </div>
          </div>
          <div className="mt-4 flex gap-4">
            <button
              onClick={() => handleOAuth('google')}
              className="flex-1 py-2 border border-slate-600 rounded text-slate-300 hover:bg-slate-700 transition-colors"
            >
              Google
            </button>
            <button
              onClick={() => handleOAuth('github')}
              className="flex-1 py-2 border border-slate-600 rounded text-slate-300 hover:bg-slate-700 transition-colors"
            >
              GitHub
            </button>
          </div>
        </div>
        */}

        <p className="mt-6 text-center text-sm text-slate-400">
          Don't have an account?{' '}
          <Link href="/signup" className="text-blue-400 hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </main>
  )
}
