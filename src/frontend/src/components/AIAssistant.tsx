'use client'

import { useState } from 'react'

interface AIAssistantProps {
  code: string
}

export default function AIAssistant({ code }: AIAssistantProps) {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const askAI = async () => {
    if (!question.trim()) return

    setIsLoading(true)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/ai/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          context: { code },
        }),
      })
      const data = await res.json()
      setResponse(data.response || 'No response from AI')
    } catch (error) {
      setResponse(`Error: ${error}`)
    }
    setIsLoading(false)
  }

  const getHelp = async () => {
    setIsLoading(true)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/triage`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      })
      const data = await res.json()
      setResponse(data.analysis || 'Analysis complete')
    } catch (error) {
      setResponse(`Error: ${error}`)
    }
    setIsLoading(false)
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-xl font-semibold mb-4">AI Assistant</h2>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your code..."
          className="flex-1 px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          onKeyPress={(e) => e.key === 'Enter' && askAI()}
        />
        <button
          onClick={askAI}
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          Ask
        </button>
        <button
          onClick={getHelp}
          disabled={isLoading}
          className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
        >
          Get Help
        </button>
      </div>

      {response && (
        <div className="p-4 bg-gray-50 rounded">
          <h3 className="font-semibold mb-2">AI Response:</h3>
          <p className="text-gray-700 whitespace-pre-wrap">{response}</p>
        </div>
      )}

      {isLoading && (
        <div className="text-center py-4">
          <div className="animate-spin inline-block w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full"></div>
          <p className="mt-2 text-gray-600">Thinking...</p>
        </div>
      )}
    </div>
  )
}
