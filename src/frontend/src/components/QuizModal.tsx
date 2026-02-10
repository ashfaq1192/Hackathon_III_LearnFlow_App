'use client'

import { useState } from 'react'

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

interface QuizResult {
  score: number
  total: number
  percentage: number
  results: {
    question_id: string
    correct: boolean
    selected: number
    correct_answer: number
    explanation: string
  }[]
}

interface QuizModalProps {
  quiz: Quiz
  onClose: () => void
  onComplete?: (result: QuizResult) => void
}

export default function QuizModal({ quiz, onClose, onComplete }: QuizModalProps) {
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [answers, setAnswers] = useState<Record<string, number>>({})
  const [results, setResults] = useState<QuizResult | null>(null)
  const [submitting, setSubmitting] = useState(false)

  const question = quiz.questions[currentQuestion]
  const totalQuestions = quiz.questions.length
  const allAnswered = Object.keys(answers).length === totalQuestions

  const handleSelect = (optionIndex: number) => {
    setAnswers({ ...answers, [question.id]: optionIndex })
  }

  const handleSubmit = async () => {
    setSubmitting(true)
    try {
      const res = await fetch(`/api/quizzes/${quiz.id}/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers }),
      })
      if (res.ok) {
        const result = await res.json()
        setResults(result)
        onComplete?.(result)
      }
    } catch {
      // Handle error
    }
    setSubmitting(false)
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-xl border border-slate-700 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700">
          <h2 className="text-lg font-semibold text-white">Quiz: {quiz.topic}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-white text-xl">&times;</button>
        </div>

        {!results ? (
          <div className="p-6">
            {/* Progress */}
            <div className="flex items-center gap-2 mb-6">
              {quiz.questions.map((_, i) => (
                <div
                  key={i}
                  className={`h-1.5 flex-1 rounded-full ${
                    i === currentQuestion ? 'bg-blue-500' : i < currentQuestion ? 'bg-green-500' : 'bg-slate-700'
                  }`}
                />
              ))}
            </div>

            <p className="text-sm text-slate-400 mb-4">
              Question {currentQuestion + 1} of {totalQuestions}
            </p>

            <p className="text-white font-medium mb-4">{question.question}</p>

            <div className="space-y-2 mb-6">
              {question.options.map((opt, i) => (
                <button
                  key={i}
                  onClick={() => handleSelect(i)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    answers[question.id] === i
                      ? 'bg-blue-600/20 border border-blue-500 text-white'
                      : 'bg-slate-700/50 border border-transparent text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                disabled={currentQuestion === 0}
                className="px-4 py-2 text-sm text-slate-300 hover:text-white disabled:opacity-50"
              >
                Previous
              </button>
              {currentQuestion < totalQuestions - 1 ? (
                <button
                  onClick={() => setCurrentQuestion(currentQuestion + 1)}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Next
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={!allAnswered || submitting}
                  className="px-6 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
                >
                  {submitting ? 'Submitting...' : 'Submit Quiz'}
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="p-6">
            <div className="text-center mb-6">
              <div className="text-4xl font-bold text-white">{results.score}/{results.total}</div>
              <div className="text-lg text-slate-400">{results.percentage}%</div>
              <div className="text-sm text-slate-500 mt-1">
                {results.percentage >= 80 ? 'Excellent work!' : results.percentage >= 50 ? 'Good effort!' : 'Keep practicing!'}
              </div>
            </div>
            <div className="space-y-3">
              {results.results.map((r, i) => (
                <div
                  key={i}
                  className={`p-3 rounded-lg border ${
                    r.correct ? 'bg-green-900/20 border-green-700' : 'bg-red-900/20 border-red-700'
                  }`}
                >
                  <span className={`text-sm font-medium ${r.correct ? 'text-green-400' : 'text-red-400'}`}>
                    Q{i + 1}: {r.correct ? 'Correct' : 'Incorrect'}
                  </span>
                  {r.explanation && <p className="text-xs text-slate-400 mt-1">{r.explanation}</p>}
                </div>
              ))}
            </div>
            <button
              onClick={onClose}
              className="w-full mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
