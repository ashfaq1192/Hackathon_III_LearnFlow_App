'use client'

import { useState } from 'react'
import Link from 'next/link'

export default function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState<'student' | 'teacher'>('student')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const res = await fetch('/api/auth/sign-up/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, role }),
      })

      if (!res.ok) {
        const text = await res.text()
        let message = 'Signup failed'
        try {
          const data = JSON.parse(text)
          message = data.message || message
        } catch {
          if (text) message = text
        }
        throw new Error(message)
      }

      window.location.href = role === 'teacher' ? '/teacher' : '/dashboard'
    } catch (err: any) {
      setError(err.message)
    }
    setLoading(false)
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-slate-900">
      <div className="max-w-md w-full p-8 bg-slate-800 rounded-lg shadow-lg border border-slate-700">
        <h1 className="text-2xl font-bold text-center mb-6 text-white">Create Account</h1>

        {error && (
          <div className="mb-4 p-3 bg-red-900/50 text-red-300 rounded border border-red-700">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-slate-300">I am a...</label>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setRole('student')}
                className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all text-sm font-medium ${
                  role === 'student'
                    ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                    : 'border-slate-600 bg-slate-700 text-slate-300 hover:border-slate-500'
                }`}
              >
                <div className="text-lg mb-1">Student</div>
                <div className="text-xs opacity-70">Learn Python with AI</div>
              </button>
              <button
                type="button"
                onClick={() => setRole('teacher')}
                className={`flex-1 py-3 px-4 rounded-lg border-2 transition-all text-sm font-medium ${
                  role === 'teacher'
                    ? 'border-purple-500 bg-purple-500/10 text-purple-400'
                    : 'border-slate-600 bg-slate-700 text-slate-300 hover:border-slate-500'
                }`}
              >
                <div className="text-lg mb-1">Teacher</div>
                <div className="text-xs opacity-70">Monitor & guide students</div>
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1 text-slate-300">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

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
              minLength={8}
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-400">
          Already have an account?{' '}
          <Link href="/login" className="text-blue-400 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </main>
  )
}
