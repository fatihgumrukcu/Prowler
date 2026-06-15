'use client'

import { useEffect, useMemo, useState } from 'react'
import type { PageResult } from '@/lib/types'
import {
  scoreTextClass, pageTopPriority, priorityBadgeClass, PRIORITY_TR,
  downloadCsv,
} from '@/lib/utils'

type SortKey = 'url' | 'score' | 'failed' | 'warning' | 'status_code'
type SortDir = 'asc' | 'desc'

interface Props {
  pages: PageResult[]
  onSelect: (page: PageResult) => void
  selectedUrl?: string | null
  resetKey?: string
}

const PAGE_SIZE = 25

function HttpBadge({ code, error }: { code: number | null; error: string | null }) {
  if (error && !code) return <span className="text-[11px] font-mono text-red-400">ERR</span>
  if (!code) return <span className="text-[11px] text-zinc-700">—</span>
  const cls = code < 300 ? 'text-emerald-400' : code < 400 ? 'text-amber-400' : 'text-red-400'
  return <span className={`text-[11px] font-mono tabular-nums ${cls}`}>{code}</span>
}

function SortIcon({ active, dir }: { active: boolean; dir: SortDir }) {
  if (!active) return <span className="ml-0.5 text-zinc-700">↕</span>
  return <span className="ml-0.5 text-zinc-300">{dir === 'asc' ? '↑' : '↓'}</span>
}

export function DataTable({ pages, onSelect, selectedUrl, resetKey }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('score')
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [currentPage, setCurrentPage] = useState(1)

  useEffect(() => {
    setCurrentPage(1)
  }, [resetKey])

  const sorted = useMemo(() => {
    return [...pages].sort((a, b) => {
      let av: number | string
      let bv: number | string
      switch (sortKey) {
        case 'url':
          av = a.url; bv = b.url; break
        case 'score':
          av = a.score; bv = b.score; break
        case 'failed':
          av = a.checks.filter(c => c.status === 'failed').length
          bv = b.checks.filter(c => c.status === 'failed').length
          break
        case 'warning':
          av = a.checks.filter(c => c.status === 'warning').length
          bv = b.checks.filter(c => c.status === 'warning').length
          break
        case 'status_code':
          av = a.status_code ?? 0; bv = b.status_code ?? 0; break
        default:
          return 0
      }
      const cmp = av < bv ? -1 : av > bv ? 1 : 0
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [pages, sortKey, sortDir])

  const totalPages = Math.ceil(sorted.length / PAGE_SIZE)
  const rows = sorted.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)

  function toggleSort(key: SortKey) {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
    setCurrentPage(1)
  }

  function exportCsv() {
    const date = new Date().toISOString().slice(0, 10)
    const headers = ['URL', 'HTTP', 'Skor', 'Hatalı', 'Uyarılı', 'Başarılı', 'En Yüksek Öncelik']
    const rowData = sorted.map(p => [
      p.url,
      p.status_code != null ? String(p.status_code) : (p.error ?? ''),
      String(p.score),
      String(p.checks.filter(c => c.status === 'failed').length),
      String(p.checks.filter(c => c.status === 'warning').length),
      String(p.checks.filter(c => c.status === 'passed').length),
      pageTopPriority(p.checks) ?? '',
    ])
    downloadCsv(`prowler-sayfalar-${date}.csv`, [headers, ...rowData])
  }

  function Th({ label, sk }: { label: string; sk?: SortKey }) {
    if (!sk) {
      return (
        <th className="px-3 py-2.5 text-left text-[10px] font-semibold text-zinc-500 uppercase tracking-wider whitespace-nowrap">
          {label}
        </th>
      )
    }
    return (
      <th
        onClick={() => toggleSort(sk)}
        className="px-3 py-2.5 text-left text-[10px] font-semibold text-zinc-500 uppercase tracking-wider whitespace-nowrap cursor-pointer hover:text-zinc-300 select-none transition-colors"
      >
        {label}
        <SortIcon active={sortKey === sk} dir={sortDir} />
      </th>
    )
  }

  if (pages.length === 0) {
    return (
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl px-5 py-12 text-center text-sm text-zinc-600">
        Filtreyle eşleşen sayfa bulunamadı.
      </div>
    )
  }

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
      {/* Table toolbar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800">
        <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">
          Taranan Sayfalar
        </h3>
        <div className="flex items-center gap-3">
          <span className="text-xs text-zinc-600 tabular-nums">{pages.length} sayfa</span>
          <button
            onClick={exportCsv}
            className="text-xs px-3 py-1.5 rounded-lg border border-zinc-700 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors"
          >
            CSV İndir
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead className="bg-zinc-900/70 border-b border-zinc-800/60">
            <tr>
              <Th label="URL" sk="url" />
              <Th label="HTTP" sk="status_code" />
              <Th label="Skor" sk="score" />
              <Th label="Hatalı" sk="failed" />
              <Th label="Uyarılı" sk="warning" />
              <Th label="Öncelik" />
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/40">
            {rows.map(p => {
              const failed   = p.checks.filter(c => c.status === 'failed').length
              const warnings = p.checks.filter(c => c.status === 'warning').length
              const topPrio  = pageTopPriority(p.checks)
              const isSelected = p.url === selectedUrl

              return (
                <tr
                  key={p.url}
                  onClick={() => onSelect(p)}
                  className={`cursor-pointer group transition-colors ${
                    isSelected
                      ? 'bg-zinc-800/60 ring-1 ring-inset ring-zinc-600'
                      : 'hover:bg-zinc-800/25'
                  }`}
                >
                  {/* URL */}
                  <td className="px-3 py-2.5 max-w-xs sm:max-w-sm lg:max-w-md">
                    <div className="flex items-center gap-1.5 min-w-0">
                      <span
                        className="text-xs font-mono text-zinc-400 truncate group-hover:text-zinc-100 transition-colors"
                        title={p.url}
                      >
                        {p.url}
                      </span>
                      <a
                        href={p.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={e => e.stopPropagation()}
                        className="text-[10px] text-zinc-700 hover:text-blue-400 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Yeni sekmede aç"
                      >
                        ↗
                      </a>
                    </div>
                  </td>

                  {/* HTTP status */}
                  <td className="px-3 py-2.5 text-center">
                    <HttpBadge code={p.status_code} error={p.error} />
                  </td>

                  {/* Score */}
                  <td className="px-3 py-2.5 text-center">
                    <span className={`text-xs font-bold tabular-nums ${p.error ? 'text-red-400' : scoreTextClass(p.score)}`}>
                      {p.error ? '—' : p.score}
                    </span>
                  </td>

                  {/* Failed */}
                  <td className="px-3 py-2.5 text-center">
                    <span className={`text-xs tabular-nums ${failed > 0 ? 'text-red-400 font-semibold' : 'text-zinc-700'}`}>
                      {failed > 0 ? `✗ ${failed}` : '—'}
                    </span>
                  </td>

                  {/* Warning */}
                  <td className="px-3 py-2.5 text-center">
                    <span className={`text-xs tabular-nums ${warnings > 0 ? 'text-amber-400' : 'text-zinc-700'}`}>
                      {warnings > 0 ? `! ${warnings}` : '—'}
                    </span>
                  </td>

                  {/* Top priority */}
                  <td className="px-3 py-2.5">
                    {topPrio ? (
                      <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold border ${priorityBadgeClass(topPrio)}`}>
                        {PRIORITY_TR[topPrio]}
                      </span>
                    ) : (
                      <span className="text-[10px] text-zinc-700">—</span>
                    )}
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-800/60 gap-4">
          <span className="text-xs text-zinc-600 tabular-nums">
            {(currentPage - 1) * PAGE_SIZE + 1}–{Math.min(currentPage * PAGE_SIZE, sorted.length)} / {sorted.length}
          </span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="text-xs px-3 py-1.5 rounded-lg border border-zinc-700 text-zinc-400 hover:text-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              ← Önceki
            </button>
            <span className="text-xs text-zinc-500 tabular-nums min-w-[4rem] text-center">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="text-xs px-3 py-1.5 rounded-lg border border-zinc-700 text-zinc-400 hover:text-zinc-200 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Sonraki →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
