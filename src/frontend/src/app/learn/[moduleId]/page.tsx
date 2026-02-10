'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'

interface CurriculumModule {
  id: string
  name: string
  order: number
  topics: string[]
  exercises_count: number
  description: string
}

interface QuizQuestion {
  id: string
  question: string
  options: string[]
  correct_answer: number
  explanation: string
}

interface Quiz {
  id: string
  module_id: string
  topic: string
  questions: QuizQuestion[]
}

export default function ModuleDetailPage() {
  const params = useParams()
  const moduleId = params.moduleId as string

  const [module, setModule] = useState<CurriculumModule | null>(null)
  const [loading, setLoading] = useState(true)
  const [quiz, setQuiz] = useState<Quiz | null>(null)
  const [quizLoading, setQuizLoading] = useState(false)
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number>>({})
  const [quizResults, setQuizResults] = useState<any>(null)
  const [conceptExplanation, setConceptExplanation] = useState<string>('')
  const [selectedTopic, setSelectedTopic] = useState<string>('')
  const [explaining, setExplaining] = useState(false)

  useEffect(() => {
    const fetchModule = async () => {
      try {
        const res = await fetch(`/api/curriculum/${moduleId}`)
        if (res.ok) setModule(await res.json())
      } catch {
        // Service may not be running
      }
      setLoading(false)
    }
    fetchModule()
  }, [moduleId])

  const handleExplainTopic = async (topic: string) => {
    setSelectedTopic(topic)
    setExplaining(true)
    setConceptExplanation('')
    try {
      const res = await fetch('/api/concepts/explain', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept: topic, level: 'beginner' }),
      })
      if (res.ok) {
        const data = await res.json()
        setConceptExplanation(data.explanation || data.content || JSON.stringify(data))
      }
    } catch {
      setConceptExplanation('Unable to load explanation. Make sure the concepts service is running.')
    }
    setExplaining(false)
  }

  const handleGenerateQuiz = async () => {
    if (!module) return
    setQuizLoading(true)
    setQuiz(null)
    setQuizResults(null)
    setSelectedAnswers({})
    try {
      const res = await fetch('/api/quizzes/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          module_id: module.id,
          topic: module.name,
          num_questions: 5,
        }),
      })
      if (res.ok) setQuiz(await res.json())
    } catch {
      // Service may not be running
    }
    setQuizLoading(false)
  }

  const handleSubmitQuiz = async () => {
    if (!quiz) return
    try {
      const res = await fetch(`/api/quizzes/${quiz.id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: selectedAnswers }),
      })
      if (res.ok) setQuizResults(await res.json())
    } catch {
      // Service may not be running
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">Loading module...</div>
      </div>
    )
  }

  if (!module) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400">Module not found</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="max-w-5xl mx-auto">
          <Link href="/learn" className="text-sm text-slate-400 hover:text-white mb-2 inline-block">&larr; Back to Curriculum</Link>
          <h1 className="text-2xl font-bold text-white">Module {module.order}: {module.name}</h1>
          <p className="text-slate-400 text-sm mt-1">{module.description}</p>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-8">
        {/* Topics */}
        <section className="mb-8">
          <h2 className="text-lg font-semibold text-white mb-4">Topics</h2>
          <div className="grid grid-cols-1 gap-3">
            {module.topics.map((topic) => (
              <div key={topic} className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center justify-between">
                  <span className="text-white font-medium">{topic}</span>
                  <button
                    onClick={() => handleExplainTopic(topic)}
                    className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                  >
                    {explaining && selectedTopic === topic ? 'Loading...' : 'Explain'}
                  </button>
                </div>
                {selectedTopic === topic && conceptExplanation && (
                  <div className="mt-3 p-3 bg-slate-900 rounded text-sm text-slate-300 whitespace-pre-wrap">
                    {conceptExplanation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Quick actions */}
        <section className="mb-8 flex gap-4">
          <Link
            href="/"
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-sm"
          >
            Open Editor
          </Link>
          <button
            onClick={handleGenerateQuiz}
            disabled={quizLoading}
            className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 transition-colors text-sm"
          >
            {quizLoading ? 'Generating Quiz...' : 'Take Quiz'}
          </button>
        </section>

        {/* Quiz section */}
        {quiz && !quizResults && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-4">Quiz: {quiz.topic}</h2>
            <div className="space-y-6">
              {quiz.questions.map((q, i) => (
                <div key={q.id} className="bg-slate-800 rounded-lg p-5 border border-slate-700">
                  <p className="text-white font-medium mb-3">
                    {i + 1}. {q.question}
                  </p>
                  <div className="space-y-2">
                    {q.options.map((opt, j) => (
                      <label
                        key={j}
                        className={`flex items-center gap-3 p-3 rounded cursor-pointer transition-colors ${
                          selectedAnswers[q.id] === j
                            ? 'bg-blue-600/20 border border-blue-500'
                            : 'bg-slate-700/50 border border-transparent hover:bg-slate-700'
                        }`}
                      >
                        <input
                          type="radio"
                          name={q.id}
                          checked={selectedAnswers[q.id] === j}
                          onChange={() => setSelectedAnswers({ ...selectedAnswers, [q.id]: j })}
                          className="text-blue-500"
                        />
                        <span className="text-slate-300 text-sm">{opt}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
              <button
                onClick={handleSubmitQuiz}
                disabled={Object.keys(selectedAnswers).length < quiz.questions.length}
                className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                Submit Quiz
              </button>
            </div>
          </section>
        )}

        {/* Quiz results */}
        {quizResults && (
          <section className="mb-8">
            <h2 className="text-lg font-semibold text-white mb-4">Quiz Results</h2>
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-4">
              <div className="text-center">
                <div className="text-4xl font-bold text-white">{quizResults.score}/{quizResults.total}</div>
                <div className="text-lg text-slate-400">{quizResults.percentage}%</div>
              </div>
            </div>
            <div className="space-y-3">
              {quizResults.results.map((r: any, i: number) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border ${
                    r.correct ? 'bg-green-900/20 border-green-700' : 'bg-red-900/20 border-red-700'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className={r.correct ? 'text-green-400' : 'text-red-400'}>
                      {r.correct ? 'Correct' : 'Incorrect'}
                    </span>
                  </div>
                  {r.explanation && (
                    <p className="text-sm text-slate-400">{r.explanation}</p>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}
      </main>
    </div>
  )
}
