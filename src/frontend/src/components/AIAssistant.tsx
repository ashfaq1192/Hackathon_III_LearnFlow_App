'use client'

import { useState } from 'react'

interface AIAssistantProps {
  code: string
}

export default function AIAssistant({ code }: AIAssistantProps) {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''

  const safeFetchJson = async (url: string, options: RequestInit) => {
    const res = await fetch(url, options)
    const contentType = res.headers.get('content-type') || ''
    if (!res.ok) {
      throw new Error(`Service unavailable (${res.status})`)
    }
    if (!contentType.includes('application/json')) {
      throw new Error('Service returned non-JSON response. Backend may not be running.')
    }
    return res.json()
  }

  const askAI = async () => {
    if (!question.trim()) return
    setIsLoading(true)
    setResponse('')
    try {
      const data = await safeFetchJson(`${apiUrl}/api/triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      setResponse(data.suggestion || data.analysis || 'No response from AI')
    } catch (error) {
      setResponse(`Error: ${error instanceof Error ? error.message : error}`)
    }
    setIsLoading(false)
  }

  const explainConcept = async () => {
    if (!question.trim()) return
    setIsLoading(true)
    setResponse('')
    try {
      const data = await safeFetchJson(`${apiUrl}/api/concepts/explain`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ concept: question }),
      })
      setResponse(data.explanation || 'No explanation available')
    } catch (error) {
      setResponse(`Error: ${error instanceof Error ? error.message : error}`)
    }
    setIsLoading(false)
  }

  const getHelp = async () => {
    setIsLoading(true)
    setResponse('')
    try {
      const codeSnippet = code.length > 500 ? code.slice(0, 500) + '...' : code
      const data = await safeFetchJson(`${apiUrl}/api/triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: `Help me with this Python code:\n${codeSnippet}`,
        }),
      })
      setResponse(data.suggestion || data.analysis || 'Analysis complete')
    } catch (error) {
      setResponse(`Error: ${error instanceof Error ? error.message : error}`)
    }
    setIsLoading(false)
  }

  return (
    <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
        AI Assistant
      </h2>

      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question or enter a concept..."
          className="flex-1 px-3 py-2 bg-slate-900 border border-slate-600 rounded text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          onKeyDown={(e) => e.key === 'Enter' && askAI()}
        />
        <button
          onClick={askAI}
          disabled={isLoading || !question.trim()}
          className="px-3 py-2 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Ask
        </button>
        <button
          onClick={explainConcept}
          disabled={isLoading || !question.trim()}
          className="px-3 py-2 bg-emerald-600 text-white text-sm rounded hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Explain
        </button>
        <button
          onClick={getHelp}
          disabled={isLoading}
          className="px-3 py-2 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Get Help
        </button>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 py-3 text-slate-400 text-sm">
          <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          Thinking...
        </div>
      )}

      {response && !isLoading && (
        <div className="p-3 bg-slate-900 border border-slate-700 rounded text-sm text-slate-300 whitespace-pre-wrap max-h-48 overflow-y-auto">
          {response}
        </div>
      )}
    </div>
  )
}
