'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface StruggleAlert {
  user_id: string
  struggle_type: string
  module_id: string
  details: Record<string, any>
  timestamp: number
}

const STRUGGLE_LABELS: Record<string, string> = {
  low_quiz_score: 'Low Quiz Score',
  repeated_failures: 'Repeated Code Failures',
  repeated_error: 'Repeated Same Error',
  verbal_expression: 'Student Expressed Difficulty',
}

export default function TeacherDashboardPage() {
  const [user, setUser] = useState<any>(null)
  const [struggles, setStruggles] = useState<StruggleAlert[]>([])
  const [loading, setLoading] = useState(true)

  // Exercise generator state
  const [genTopic, setGenTopic] = useState('')
  const [genDifficulty, setGenDifficulty] = useState('beginner')
  const [genCount, setGenCount] = useState(3)
  const [generatedExercises, setGeneratedExercises] = useState<any[]>([])
  const [generating, setGenerating] = useState(false)
  const [genError, setGenError] = useState('')

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

        const strugglesRes = await fetch('/api/progress/struggles')
        if (strugglesRes.ok) setStruggles(await strugglesRes.json())
      } catch {
        // Services may not be running
      }
      setLoading(false)
    }
    init()
  }, [])

  const handleGenerate = async () => {
    if (!genTopic.trim()) return
    setGenerating(true)
    setGeneratedExercises([])
    setGenError('')
    try {
      const res = await fetch('/api/exercises/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic: genTopic, difficulty: genDifficulty, count: genCount }),
      })
      if (res.ok) {
        setGeneratedExercises(await res.json())
      } else {
        setGenError(`Generation failed (${res.status})`)
      }
    } catch {
      setGenError('Exercise service unavailable')
    }
    setGenerating(false)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading teacher dashboard...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div>
            <h1 className="text-2xl font-bold text-white">Teacher Dashboard</h1>
            <p className="text-slate-400 text-sm mt-1">Monitor students and create exercises</p>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/learn" className="text-sm text-slate-300 hover:text-white">Curriculum</Link>
            <Link href="/" className="text-sm text-slate-300 hover:text-white">Editor</Link>
            <Link href="/profile" className="text-sm text-slate-300 hover:text-white">Profile</Link>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-2 gap-8">
          {/* Struggle Alerts */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">
              Struggle Alerts
              {struggles.length > 0 && (
                <span className="ml-2 px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">
                  {struggles.length}
                </span>
              )}
            </h2>
            {struggles.length === 0 ? (
              <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 text-center text-slate-400">
                No active struggle alerts. All students are doing well!
              </div>
            ) : (
              <div className="space-y-3">
                {struggles.map((s, i) => (
                  <div key={i} className="bg-slate-800 rounded-lg p-4 border border-red-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-red-400">
                        {STRUGGLE_LABELS[s.struggle_type] || s.struggle_type}
                      </span>
                      <span className="text-xs text-slate-500">
                        {new Date(s.timestamp * 1000).toLocaleTimeString()}
                      </span>
                    </div>
                    <p className="text-sm text-slate-300">
                      Student: {s.user_id}
                      {s.module_id && ` | Module: ${s.module_id}`}
                    </p>
                    {s.details && Object.keys(s.details).length > 0 && (
                      <p className="text-xs text-slate-500 mt-1">
                        {JSON.stringify(s.details)}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Exercise Generator */}
          <section>
            <h2 className="text-xl font-semibold text-white mb-4">AI Exercise Generator</h2>
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Topic</label>
                  <input
                    type="text"
                    value={genTopic}
                    onChange={(e) => setGenTopic(e.target.value)}
                    placeholder="e.g., for loops, list comprehensions"
                    className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white placeholder-slate-400 text-sm"
                  />
                </div>
                <div className="flex gap-4">
                  <div className="flex-1">
                    <label className="block text-sm font-medium text-slate-300 mb-1">Difficulty</label>
                    <select
                      value={genDifficulty}
                      onChange={(e) => setGenDifficulty(e.target.value)}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm"
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="advanced">Advanced</option>
                    </select>
                  </div>
                  <div className="w-24">
                    <label className="block text-sm font-medium text-slate-300 mb-1">Count</label>
                    <input
                      type="number"
                      value={genCount}
                      onChange={(e) => setGenCount(Number(e.target.value))}
                      min={1}
                      max={10}
                      className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded text-white text-sm"
                    />
                  </div>
                </div>
                <button
                  onClick={handleGenerate}
                  disabled={generating || !genTopic.trim()}
                  className="w-full py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 transition-colors text-sm"
                >
                  {generating ? 'Generating...' : 'Generate Exercises'}
                </button>
              </div>

              {genError && (
                <p className="mt-3 text-sm text-red-400">{genError}</p>
              )}

              {generatedExercises.length > 0 && (
                <div className="mt-6 space-y-3">
                  <h3 className="text-sm font-medium text-slate-300">Generated Exercises:</h3>
                  {generatedExercises.map((ex, i) => (
                    <div key={i} className="p-3 bg-slate-700 rounded">
                      <div className="font-medium text-white text-sm">{ex.title}</div>
                      <p className="text-xs text-slate-400 mt-1">{ex.description}</p>
                      {ex.starter_code && (
                        <pre className="mt-2 p-2 bg-slate-900 rounded text-xs text-green-400 overflow-x-auto">
                          {ex.starter_code}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  )
}
