'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface CurriculumModule {
  id: string
  name: string
  order: number
  topics: string[]
  exercises_count: number
  description: string
}

interface ModuleProgress {
  mastery: number
  mastery_level: string
  exercises_completed: number
  quizzes_taken: number
}

const MASTERY_COLORS: Record<string, string> = {
  beginner: 'bg-red-500',
  learning: 'bg-yellow-500',
  proficient: 'bg-green-500',
  mastered: 'bg-blue-500',
}

export default function LearnPage() {
  const [curriculum, setCurriculum] = useState<CurriculumModule[]>([])
  const [progress, setProgress] = useState<Record<string, ModuleProgress>>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      try {
        const currRes = await fetch('/api/curriculum')
        if (currRes.ok) setCurriculum(await currRes.json())

        const sessionRes = await fetch('/api/auth/get-session', { credentials: 'include' })
        if (sessionRes.ok) {
          const session = await sessionRes.json()
          if (session?.user?.id) {
            const progRes = await fetch(`/api/progress/${session.user.id}`)
            if (progRes.ok) {
              const data = await progRes.json()
              setProgress(data.modules || {})
            }
          }
        }
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
        <div className="text-slate-400">Loading curriculum...</div>
      </div>
    )
  }

  const modules = curriculum.sort((a, b) => a.order - b.order)

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between max-w-5xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-white">Python Curriculum</h1>
            <p className="text-slate-400 text-sm mt-1">8 modules to Python mastery</p>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/dashboard" className="text-sm text-slate-300 hover:text-white">Dashboard</Link>
            <Link href="/" className="text-sm text-slate-300 hover:text-white">Editor</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        <div className="space-y-4">
          {modules.map((mod) => {
            const modProgress = progress[mod.id]
            const mastery = modProgress?.mastery || 0
            const level = modProgress?.mastery_level || 'beginner'

            return (
              <Link
                key={mod.id}
                href={`/learn/${mod.id}`}
                className="block bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-500 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-slate-500 font-mono text-sm">#{mod.order}</span>
                      <h2 className="text-lg font-semibold text-white">{mod.name}</h2>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium text-white ${MASTERY_COLORS[level]}`}>
                        {level}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400 mb-3">{mod.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {mod.topics.map((topic) => (
                        <span key={topic} className="px-2 py-1 bg-slate-700 rounded text-xs text-slate-300">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="ml-6 text-right shrink-0">
                    <div className="text-2xl font-bold text-white">{mastery}%</div>
                    <div className="text-xs text-slate-500">{mod.exercises_count} exercises</div>
                  </div>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-1.5 mt-4">
                  <div
                    className={`h-1.5 rounded-full transition-all ${MASTERY_COLORS[level]}`}
                    style={{ width: `${mastery}%` }}
                  />
                </div>
              </Link>
            )
          })}
        </div>
      </main>
    </div>
  )
}
