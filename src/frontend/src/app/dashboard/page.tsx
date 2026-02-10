'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface ModuleProgress {
  module_id: string
  module_name: string
  mastery: number
  mastery_level: string
  exercises_completed: number
  quizzes_taken: number
}

interface UserProgress {
  user_id: string
  modules: Record<string, ModuleProgress>
  streak: number
  total_exercises: number
  total_quizzes: number
}

interface CurriculumModule {
  id: string
  name: string
  order: number
  topics: string[]
  exercises_count: number
  description: string
}

const MASTERY_COLORS: Record<string, string> = {
  beginner: 'bg-red-500',
  learning: 'bg-yellow-500',
  proficient: 'bg-green-500',
  mastered: 'bg-blue-500',
}

export default function DashboardPage() {
  const [progress, setProgress] = useState<UserProgress | null>(null)
  const [curriculum, setCurriculum] = useState<CurriculumModule[]>([])
  const [user, setUser] = useState<{ id: string; name: string; role: string } | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      try {
        const sessionRes = await fetch('/api/auth/get-session', { credentials: 'include' })
        if (!sessionRes.ok) {
          window.location.href = '/login'
          return
        }
        const session = await sessionRes.json()
        if (!session?.user) {
          window.location.href = '/login'
          return
        }
        setUser(session.user)

        const [progressRes, curriculumRes] = await Promise.all([
          fetch(`/api/progress/${session.user.id}`),
          fetch('/api/curriculum'),
        ])

        if (progressRes.ok) setProgress(await progressRes.json())
        if (curriculumRes.ok) setCurriculum(await curriculumRes.json())
      } catch {
        // Services may not be running
      }
      setLoading(false)
    }
    init()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading dashboard...</div>
      </div>
    )
  }

  const modules = curriculum.sort((a, b) => a.order - b.order)
  const overallMastery = progress
    ? Math.round(
        Object.values(progress.modules).reduce((sum, m) => sum + m.mastery, 0) /
          Object.values(progress.modules).length
      )
    : 0

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-white">Welcome back, {user?.name || 'Student'}!</h1>
            <p className="text-slate-400 text-sm mt-1">Your Python learning journey</p>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/learn" className="text-sm text-slate-300 hover:text-white">Learn</Link>
            <Link href="/" className="text-sm text-slate-300 hover:text-white">Editor</Link>
            <Link href="/profile" className="text-sm text-slate-300 hover:text-white">Profile</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats row */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <div className="text-3xl font-bold text-white">{overallMastery}%</div>
            <div className="text-sm text-slate-400">Overall Mastery</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <div className="text-3xl font-bold text-white">{progress?.streak || 0}</div>
            <div className="text-sm text-slate-400">Day Streak</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <div className="text-3xl font-bold text-white">{progress?.total_exercises || 0}</div>
            <div className="text-sm text-slate-400">Exercises Done</div>
          </div>
          <div className="bg-slate-800 rounded-lg p-4 border border-slate-700">
            <div className="text-3xl font-bold text-white">{progress?.total_quizzes || 0}</div>
            <div className="text-sm text-slate-400">Quizzes Taken</div>
          </div>
        </div>

        {/* Module progress grid */}
        <h2 className="text-xl font-semibold text-white mb-4">Your Modules</h2>
        <div className="grid grid-cols-2 gap-4">
          {modules.map((mod) => {
            const modProgress = progress?.modules[mod.id]
            const mastery = modProgress?.mastery || 0
            const level = modProgress?.mastery_level || 'beginner'

            return (
              <Link
                key={mod.id}
                href={`/learn/${mod.id}`}
                className="bg-slate-800 rounded-lg p-5 border border-slate-700 hover:border-slate-500 transition-colors"
              >
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-white">
                    Module {mod.order}: {mod.name}
                  </h3>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium text-white ${MASTERY_COLORS[level]}`}>
                    {level}
                  </span>
                </div>
                <p className="text-sm text-slate-400 mb-3">{mod.description}</p>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${MASTERY_COLORS[level]}`}
                    style={{ width: `${mastery}%` }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-xs text-slate-500">
                  <span>{mastery}% mastery</span>
                  <span>{modProgress?.exercises_completed || 0} exercises</span>
                </div>
              </Link>
            )
          })}
        </div>
      </main>
    </div>
  )
}
