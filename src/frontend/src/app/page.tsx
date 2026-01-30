'use client'

import { useState } from 'react'
import CodeEditor from '@/components/CodeEditor'
import ExercisePanel from '@/components/ExercisePanel'
import AIAssistant from '@/components/AIAssistant'

export default function Home() {
  const [code, setCode] = useState('# Write your Python code here\nprint("Hello, LearnFlow!")\n')
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)

  const runCode = async () => {
    setIsRunning(true)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      })
      const result = await response.json()
      setOutput(result.output || result.error || 'No output')
    } catch (error) {
      setOutput(`Error: ${error}`)
    }
    setIsRunning(false)
  }

  return (
    <main className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-center">LearnFlow</h1>
        <p className="text-center text-gray-600 mt-2">
          AI-Powered Python Learning Platform
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Exercise Panel */}
        <div className="lg:col-span-1">
          <ExercisePanel />
        </div>

        {/* Code Editor */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-lg p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">Code Editor</h2>
              <button
                onClick={runCode}
                disabled={isRunning}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
              >
                {isRunning ? 'Running...' : 'Run Code'}
              </button>
            </div>

            <CodeEditor code={code} onChange={setCode} />

            {/* Output */}
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Output:</h3>
              <pre className="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm min-h-[100px]">
                {output || 'Click "Run Code" to see output'}
              </pre>
            </div>
          </div>
        </div>
      </div>

      {/* AI Assistant */}
      <div className="mt-8">
        <AIAssistant code={code} />
      </div>
    </main>
  )
}
