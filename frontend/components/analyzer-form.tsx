'use client'

import { type FormEvent, useState } from 'react'

interface Props {
  onAnalyze: (url: string) => void
  onCrawl: (url: string, maxPages: number) => void
  loading: boolean
}

export function AnalyzerForm({ onAnalyze, onCrawl, loading }: Props) {
  const [url, setUrl] = useState('')
  const [maxPages, setMaxPages] = useState(1000)
  const [rawInput, setRawInput] = useState('1000')

  function handleAnalyze(e: FormEvent | React.MouseEvent) {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) return
    onAnalyze(trimmed)
  }

  function handleCrawl(e: React.MouseEvent) {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) return
    onCrawl(trimmed, maxPages)
  }

  function handleMaxPagesChange(val: string) {
    setRawInput(val)
    const n = parseInt(val, 10)
    if (!isNaN(n) && n >= 1) {
      setMaxPages(Math.min(n, 1000))
    }
  }

  return (
    <div className="space-y-3">
      <input
        type="text"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        onKeyDown={(e) => { if (e.key === 'Enter') handleAnalyze(e as unknown as FormEvent) }}
        placeholder="https://example.com"
        disabled={loading}
        spellCheck={false}
        className="
          w-full bg-zinc-900 border border-zinc-700 rounded-lg
          px-4 py-2.5 text-sm font-mono text-zinc-100
          placeholder:text-zinc-600
          focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500/50
          disabled:opacity-50 disabled:cursor-not-allowed
          transition-colors
        "
      />
      <div className="flex gap-2 items-center flex-wrap">
        <button
          onClick={handleAnalyze}
          disabled={loading || !url.trim()}
          className="
            px-5 py-2.5 bg-zinc-100 text-zinc-900 text-sm font-semibold rounded-lg
            hover:bg-white active:scale-[0.98]
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-all whitespace-nowrap
          "
        >
          {loading ? 'Analiz ediliyor…' : 'Tek Sayfa Analiz'}
        </button>
        <button
          onClick={handleCrawl}
          disabled={loading || !url.trim()}
          className="
            px-5 py-2.5 bg-blue-600 text-white text-sm font-semibold rounded-lg
            hover:bg-blue-500 active:scale-[0.98]
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-all whitespace-nowrap
          "
        >
          {loading ? 'Taranıyor…' : 'Siteyi Tara'}
        </button>

        <div className="flex items-center gap-2 ml-auto">
          <label className="text-xs text-zinc-500 whitespace-nowrap">Maks. sayfa</label>
          <input
            type="number"
            min={1}
            max={1000}
            value={rawInput}
            onChange={(e) => handleMaxPagesChange(e.target.value)}
            disabled={loading}
            className="
              w-20 bg-zinc-900 border border-zinc-700 rounded-lg
              px-3 py-2 text-sm text-zinc-200 text-center tabular-nums
              focus:outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500/50
              disabled:opacity-40
              [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none
            "
          />
        </div>
      </div>
    </div>
  )
}
