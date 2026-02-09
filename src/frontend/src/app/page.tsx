'use client'

import { useState } from 'react'
import CodeEditor from '@/components/CodeEditor'
import ExercisePanel from '@/components/ExercisePanel'
import AIAssistant from '@/components/AIAssistant'
import UserMenu from '@/components/UserMenu'

export default function Home() {
  const [code, setCode] = useState('# Write your Python code here\nprint("Hello, LearnFlow!")\n')
  const [output, setOutput] = useState('')
  const [isRunning, setIsRunning] = useState(false)

  const runCode = async () => {
    setIsRunning(true)
    setOutput('')
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || ''}/api/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      })
      const contentType = response.headers.get('content-type') || ''
      if (!response.ok) {
        setOutput(`Error: Code execution service unavailable (${response.status})`)
        setIsRunning(false)
        return
      }
      if (!contentType.includes('application/json')) {
        setOutput('Error: Code execution service returned unexpected response. Backend may not be running.')
        setIsRunning(false)
        return
      }
      const result = await response.json()
      setOutput(result.output || result.error || 'No output')
    } catch (error) {
      setOutput(`Error: ${error instanceof Error ? error.message : error}`)
    }
    setIsRunning(false)
  }

  const handleExerciseSelect = (exercise: { starter_code?: string }) => {
    if (exercise.starter_code) {
      setCode(exercise.starter_code)
      setOutput('')
    }
  }

  return (
    <div className="h-screen flex flex-col bg-slate-900">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700 shrink-0">
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-bold text-white">LearnFlow</h1>
          <span className="text-xs text-slate-500">AI-Powered Python Learning</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            <span className="text-xs text-slate-400">Connected</span>
          </div>
          <UserMenu />
        </div>
      </header>

      {/* Main content */}
      <div className="flex flex-1 min-h-0">
        {/* Left sidebar - Exercises */}
        <aside className="w-72 border-r border-slate-700 overflow-y-auto shrink-0 bg-slate-800/50">
          <ExercisePanel onSelectExercise={handleExerciseSelect} />
        </aside>

        {/* Main area */}
        <main className="flex-1 flex flex-col min-w-0">
          {/* Editor toolbar */}
          <div className="flex items-center justify-between px-4 py-2 bg-slate-800/30 border-b border-slate-700 shrink-0">
            <span className="text-sm text-slate-400">main.py</span>
            <button
              onClick={runCode}
              disabled={isRunning}
              className="px-4 py-1.5 bg-green-600 text-white text-sm font-medium rounded hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {isRunning ? 'Running...' : 'Run Code'}
            </button>
          </div>

          {/* Editor */}
          <div className="flex-1 min-h-0">
            <CodeEditor code={code} onChange={setCode} />
          </div>

          {/* Output panel */}
          <div className="h-40 border-t border-slate-700 shrink-0 flex flex-col">
            <div className="px-4 py-1.5 bg-slate-800/30 border-b border-slate-700 shrink-0">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Output</span>
            </div>
            <pre className="flex-1 px-4 py-2 bg-slate-900 text-green-400 font-mono text-sm overflow-auto">
              {output || 'Click "Run Code" to see output'}
            </pre>
          </div>

          {/* AI Assistant panel */}
          <div className="border-t border-slate-700 shrink-0">
            <AIAssistant code={code} />
          </div>
        </main>
      </div>
    </div>
  )
}
