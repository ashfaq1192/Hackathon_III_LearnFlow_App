'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface User {
  id: string
  name: string
  email: string
  image?: string
  createdAt?: string
}

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSession = async () => {
      try {
        const res = await fetch('/api/auth/get-session', {
          credentials: 'include',
        })
        if (res.ok) {
          const data = await res.json()
          if (data?.user) {
            setUser(data.user)
          }
        }
      } catch {
        // Not logged in
      }
      setLoading(false)
    }
    fetchSession()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-slate-400 mb-4">You need to be logged in to view your profile.</p>
          <Link href="/login" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            Login
          </Link>
        </div>
      </div>
    )
  }

  const initials = user.name
    ? user.name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
    : user.email[0].toUpperCase()

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="flex items-center justify-between px-6 py-3 bg-slate-800 border-b border-slate-700">
        <Link href="/" className="text-lg font-bold text-white hover:text-blue-400 transition-colors">
          LearnFlow
        </Link>
      </header>

      <main className="max-w-2xl mx-auto px-6 py-12">
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-8">
          <div className="flex items-center gap-6 mb-8">
            <div className="w-20 h-20 bg-blue-600 rounded-full flex items-center justify-center text-white text-2xl font-bold">
              {initials}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{user.name || 'LearnFlow User'}</h1>
              <p className="text-slate-400">{user.email}</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-slate-700">
              <span className="text-sm text-slate-400">User ID</span>
              <span className="text-sm text-slate-200 font-mono">{user.id}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-700">
              <span className="text-sm text-slate-400">Email</span>
              <span className="text-sm text-slate-200">{user.email}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-slate-700">
              <span className="text-sm text-slate-400">Name</span>
              <span className="text-sm text-slate-200">{user.name || 'Not set'}</span>
            </div>
            {user.createdAt && (
              <div className="flex justify-between items-center py-3 border-b border-slate-700">
                <span className="text-sm text-slate-400">Member since</span>
                <span className="text-sm text-slate-200">
                  {new Date(user.createdAt).toLocaleDateString()}
                </span>
              </div>
            )}
          </div>

          <div className="mt-8 flex gap-3">
            <Link
              href="/"
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
            >
              Back to Editor
            </Link>
          </div>
        </div>
      </main>
    </div>
  )
}
