/**
 * App.jsx - Main React Component for AI Research Assistant
 * 
 * Features:
 * - Clean, ChatGPT-like UI
 * - "Fake streaming" status updates while waiting for API
 * - Markdown rendering for final report
 * - Displays research plan to show off the Level 3 logic
 */

import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

// Status messages for the "fake streaming" effect
const STATUS_MESSAGES = [
  "🧠 Analyzing your request...",
  "🔎 Generating search strategy...",
  "🌍 Searching the web (Tavily)...",
  "❌ Filtering irrelevant noise...",
  "✍️ Synthesizing final report..."
]

function App() {
  // State management
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [statusIndex, setStatusIndex] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // Fake streaming effect - cycle through status messages while loading
  useEffect(() => {
    let interval
    if (isLoading) {
      interval = setInterval(() => {
        setStatusIndex((prev) => (prev + 1) % STATUS_MESSAGES.length)
      }, 2500) // Change status every 2.5 seconds
    }
    return () => clearInterval(interval)
  }, [isLoading])

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setStatusIndex(0)
    setResult(null)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/api/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: query.trim() }),
      })

      if (!response.ok) {
        throw new Error('Research request failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Something went wrong')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="border-b border-gray-800 py-6">
        <div className="max-w-4xl mx-auto px-4">
          <h1 className="text-3xl font-bold text-center bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            🔬 AI Research Assistant
          </h1>
          <p className="text-gray-400 text-center mt-2">
            Level 3 Search Agent: Plans → Searches → Filters → Synthesizes
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Search Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Ask a research question..."
              className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-lg focus:outline-none focus:border-blue-500 transition-colors"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !query.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed px-6 py-3 rounded-lg font-semibold transition-colors"
            >
              {isLoading ? 'Researching...' : 'Research'}
            </button>
          </div>
        </form>

        {/* Loading Status */}
        {isLoading && (
          <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 mb-8 text-center">
            <div className="animate-pulse text-xl text-blue-400">
              {STATUS_MESSAGES[statusIndex]}
            </div>
            <div className="mt-4 flex justify-center gap-2">
              {STATUS_MESSAGES.map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full transition-colors ${i === statusIndex ? 'bg-blue-500' : 'bg-gray-700'
                    }`}
                />
              ))}
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-900/50 border border-red-700 rounded-lg p-4 mb-8">
            <p className="text-red-300">❌ Error: {error}</p>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="space-y-6">
            {/* Research Plan Box */}
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-blue-400 mb-4">
                📋 Research Plan
              </h2>
              <ul className="space-y-2">
                {result.plan.map((subQuery, i) => (
                  <li key={i} className="flex items-start gap-3">
                    <span className="bg-blue-600 text-white text-sm px-2 py-0.5 rounded">
                      {i + 1}
                    </span>
                    <span className="text-gray-300">{subQuery}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Report Box */}
            <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
              <h2 className="text-lg font-semibold text-green-400 mb-4">
                📄 Research Report
              </h2>
              <div className="prose prose-invert prose-blue max-w-none">
                <ReactMarkdown>{result.report}</ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-4 mt-8">
        <p className="text-center text-gray-500 text-sm">
          Built with FastAPI, OpenAI, and Tavily • Level 3 Search Agent
        </p>
      </footer>
    </div>
  )
}

export default App
