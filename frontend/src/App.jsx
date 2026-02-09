import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'

const STATUS_MESSAGES = [
  "Analyzing request...",
  "Planning research...",
  "Searching sources...",
  "Filtering content...",
  "Writing report..."
]

function App() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [statusIndex, setStatusIndex] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [showColdStartNotice, setShowColdStartNotice] = useState(false)

  useEffect(() => {
    const hasSeenNotice = localStorage.getItem('hasSeenColdStartNotice')
    if (!hasSeenNotice) {
      setShowColdStartNotice(true)
    }
  }, [])

  const dismissColdStartNotice = () => {
    localStorage.setItem('hasSeenColdStartNotice', 'true')
    setShowColdStartNotice(false)
  }

  useEffect(() => {
    let interval
    if (isLoading) {
      interval = setInterval(() => {
        setStatusIndex((prev) => (prev + 1) % STATUS_MESSAGES.length)
      }, 2500)
    }
    return () => clearInterval(interval)
  }, [isLoading])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setStatusIndex(0)
    setResult(null)
    setError(null)

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${API_URL}/api/research`, {
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

  const parseReport = (fullReport) => {
    if (!fullReport) return { content: '', references: [] }

    const parts = fullReport.split('## 📚 References')
    const content = parts[0]
    const rawRefs = parts[1] || ''

    const refs = []
    if (rawRefs) {
      const refLines = rawRefs.split('\n').filter(line => line.trim())
      refLines.forEach(line => {
        const match = line.match(/^\d+\.\s+\[(.*?)\]\((.*?)\)/)
        if (match) {
          refs.push({ title: match[1], url: match[2] })
        }
      })
    }

    return { content, references: refs }
  }

  const { content: reportContent, references } = result ? parseReport(result.report) : { content: '', references: [] }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 font-sans selection:bg-blue-100 selection:text-blue-900">

      {showColdStartNotice && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <div className="flex items-start gap-3 mb-4">
              <div className="flex-shrink-0 w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-slate-900 mb-2">First Query Notice</h3>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Backend hosted on Render with 15-min auto-sleep. First query may take 30-60s due to cold start.
                </p>
              </div>
            </div>
            <button
              onClick={dismissColdStartNotice}
              className="w-full bg-slate-900 hover:bg-slate-800 text-white font-medium py-2.5 px-4 rounded-xl transition-colors"
            >
              Got it
            </button>
          </div>
        </div>
      )}

      <nav className="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-slate-900">WebScout</span>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-6 py-10">

        <section className="mb-10 text-center">
          <h1 className="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">
            Research Assistant
          </h1>
          <p className="text-slate-500 mb-8 text-lg max-w-xl mx-auto leading-relaxed">
            Deep research into any topic, synthesized for you.
          </p>

          <form onSubmit={handleSubmit} className="relative max-w-2xl mx-auto">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What do you want to research?"
              className="w-full bg-white border border-slate-200 text-slate-900 text-lg rounded-2xl pl-12 pr-32 py-4 shadow-sm hover:border-slate-300 focus:border-blue-500 focus:ring-4 focus:ring-blue-50/50 focus:outline-none transition-all placeholder:text-slate-400"
              disabled={isLoading}
            />
            <div className="absolute right-2 top-2 bottom-2">
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="h-full px-6 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-xl disabled:bg-slate-200 disabled:text-slate-400 transition-all shadow-sm"
              >
                {isLoading ? '...' : 'Search'}
              </button>
            </div>
          </form>
        </section>

        {isLoading && (
          <div className="max-w-2xl mx-auto mb-12">
            <div className="text-center">
              <span className="text-sm font-medium text-slate-500 animate-pulse tracking-wide">
                {STATUS_MESSAGES[statusIndex]}
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="max-w-2xl mx-auto mb-8 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm flex items-center gap-3 shadow-sm">
            <svg className="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {error}
          </div>
        )}

        {result && (
          <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-6 duration-700">

            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm">
              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Research Plan
              </h2>
              <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                {result.plan.map((subQuery, i) => (
                  <div key={i} className="bg-slate-50 rounded-xl p-3 text-sm text-slate-700 border border-slate-100 flex items-start gap-2">
                    <span className="flex-shrink-0 w-5 h-5 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 text-xs font-bold mt-0.5">
                      {i + 1}
                    </span>
                    <span className="leading-snug">{subQuery}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-8 sm:p-10 shadow-sm relative overflow-hidden">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500"></div>

              <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-8 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Research Report
              </h2>

              <div className="prose prose-slate max-w-none 
                prose-headings:text-slate-900 prose-headings:font-bold prose-h1:text-3xl prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-4
                prose-p:text-slate-600 prose-p:leading-relaxed prose-p:mb-6
                prose-li:text-slate-600
                prose-strong:text-slate-800 prose-strong:font-semibold
                prose-a:text-blue-600 prose-a:font-medium prose-a:no-underline hover:prose-a:underline hover:prose-a:text-blue-700 transition-colors
                prose-blockquote:border-l-4 prose-blockquote:border-blue-200 prose-blockquote:bg-blue-50/50 prose-blockquote:p-4 prose-blockquote:rounded-r-lg prose-blockquote:text-slate-700 prose-blockquote:italic
                prose-code:bg-slate-100 prose-code:text-slate-700 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:before:content-none prose-code:after:content-none">
                <ReactMarkdown
                  components={{
                    a: ({ node, ...props }) => (
                      <a {...props} className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded text-sm font-medium hover:bg-blue-100 transition-colors inline-block mx-0.5 no-underline border border-blue-100" target="_blank" rel="noopener noreferrer" />
                    )
                  }}
                >
                  {reportContent}
                </ReactMarkdown>
              </div>
            </div>

            {references.length > 0 && (
              <div className="bg-slate-100 rounded-2xl p-6 border border-slate-200/50">
                <h2 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4 flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                  </svg>
                  Sources Used
                </h2>
                <div className="grid gap-3 sm:grid-cols-2 md:grid-cols-3">
                  {references.map((ref, i) => (
                    <a
                      key={i}
                      href={ref.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="group bg-white p-4 rounded-xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all flex flex-col justify-between h-full"
                    >
                      <span className="text-sm font-medium text-slate-800 line-clamp-2 mb-2 group-hover:text-blue-700 transition-colors">
                        {ref.title}
                      </span>
                      <span className="text-xs text-slate-400 truncate flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                        </svg>
                        {new URL(ref.url).hostname.replace('www.', '')}
                      </span>
                    </a>
                  ))}
                </div>
              </div>
            )}

          </div>
        )}

      </main>


    </div>
  )
}

export default App
