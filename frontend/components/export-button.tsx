'use client'

import { useState } from 'react'
import { exportCrawl } from '@/lib/api'
import { downloadCsv } from '@/lib/utils'
import type { AnalyzeResponse } from '@/lib/types'

interface CrawlProps {
  jobId: string
  analyzeResult?: never
}

interface AnalyzeProps {
  analyzeResult: AnalyzeResponse
  jobId?: never
}

type Props = CrawlProps | AnalyzeProps

// ── Client-side JSON download ─────────────────────────────────────────────────
function downloadJson(data: unknown, filename: string) {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// ── Client-side CSV for single-URL analysis ───────────────────────────────────
function exportAnalyzeCsv(result: AnalyzeResponse) {
  const date = new Date().toISOString().slice(0, 10)
  const domain = new URL(result.final_url).hostname.replace(/\./g, '-')
  const headers = ['id', 'kategori', 'kontrol', 'durum', 'öncelik', 'efor', 'mesaj', 'değer', 'öneri']
  const rows = result.checks.map(c => [
    c.id,
    c.category,
    c.label,
    c.status,
    c.priority_label ?? '',
    c.effort ?? '',
    c.message,
    c.value ?? '',
    c.how_to_fix ?? c.recommendation ?? '',
  ])
  downloadCsv(`prowler-analiz-${domain}-${date}.csv`, [headers, ...rows])
}

export function ExportButton({ jobId, analyzeResult }: Props) {
  const [busy, setBusy] = useState<'csv' | 'json' | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handle(format: 'csv' | 'json') {
    setError(null)
    setBusy(format)
    try {
      if (jobId) {
        await exportCrawl(jobId, format)
      } else if (analyzeResult) {
        const date = new Date().toISOString().slice(0, 10)
        const domain = new URL(analyzeResult.final_url).hostname.replace(/\./g, '-')
        if (format === 'json') {
          downloadJson(analyzeResult, `prowler-analiz-${domain}-${date}.json`)
        } else {
          exportAnalyzeCsv(analyzeResult)
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'İndirme başarısız')
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {error && (
        <span className="text-xs text-red-400 mr-1">{error}</span>
      )}
      {(['csv', 'json'] as const).map(fmt => (
        <button
          key={fmt}
          onClick={() => handle(fmt)}
          disabled={busy !== null}
          className="text-xs px-3 py-1.5 rounded-lg border border-zinc-700 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors whitespace-nowrap"
        >
          {busy === fmt ? '…' : `↓ ${fmt.toUpperCase()}`}
        </button>
      ))}
    </div>
  )
}
