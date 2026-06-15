'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import type { CrawlResult, PageResult } from '@/lib/types'
import {
  CATEGORY_ORDER, CATEGORY_TR,
  scoreLabel, scoreRingColor, scoreTextClass,
} from '@/lib/utils'
import { fetchPageSource } from '@/lib/api'
import { FilterBar, defaultFilters, type FilterState } from './filter-bar'
import { DataTable } from './data-table'
import { PageDetailDrawer } from './page-detail-drawer'
import { ExportButton } from './export-button'
import { SiteArchitectureGraph } from './site-architecture-graph'

type DashboardTab = 'overview' | 'architecture'

interface Props {
  result: CrawlResult
  jobId: string
}

// ── HTML kaynak kodu modalı ───────────────────────────────────────────────────
function SourceModal({ url, onClose }: { url: string; onClose: () => void }) {
  const [html, setHtml] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    fetchPageSource(url)
      .then(r => setHtml(r.html))
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [url])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}
    >
      <div className="bg-zinc-950 border border-zinc-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800 gap-3 flex-shrink-0">
          <p className="text-xs font-mono text-zinc-400 truncate flex-1">{url}</p>
          <div className="flex gap-2 flex-shrink-0">
            <a href={url} target="_blank" rel="noopener noreferrer"
              className="text-xs text-blue-400 hover:text-blue-300 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors">
              Sayfayı Aç ↗
            </a>
            {html && (
              <button
                onClick={() => navigator.clipboard.writeText(html).then(() => setCopied(true))}
                className="text-xs text-zinc-400 hover:text-zinc-200 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors"
              >
                {copied ? 'Kopyalandı ✓' : 'Kopyala'}
              </button>
            )}
            <button onClick={onClose}
              className="text-xs text-zinc-500 hover:text-zinc-200 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors">
              Kapat ✕
            </button>
          </div>
        </div>
        <div className="overflow-auto flex-1 p-1">
          {loading && (
            <div className="flex items-center justify-center py-20 text-zinc-600">
              <div className="w-5 h-5 border-2 border-zinc-700 border-t-zinc-400 rounded-full animate-spin mr-3" />
              <span className="text-sm">Yükleniyor…</span>
            </div>
          )}
          {error && <p className="p-5 text-sm text-red-400 font-mono">{error}</p>}
          {html && (
            <pre className="text-[11px] font-mono text-zinc-300 leading-relaxed p-4 whitespace-pre-wrap break-all">
              {html}
            </pre>
          )}
        </div>
      </div>
    </div>
  )
}

// ── Site skor halkası ─────────────────────────────────────────────────────────
function SiteScoreRing({ score }: { score: number }) {
  const R = 56, C = 2 * Math.PI * R
  return (
    <div className="relative flex-shrink-0 w-[136px] h-[136px]">
      <svg width="136" height="136" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="68" cy="68" r={R} fill="none" stroke="#27272a" strokeWidth="10" />
        <circle cx="68" cy="68" r={R} fill="none" strokeWidth="10" strokeLinecap="round"
          strokeDasharray={`${(score / 100) * C} ${C}`}
          style={{ stroke: scoreRingColor(score), transition: 'stroke-dasharray 0.8s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`text-4xl font-bold tabular-nums ${scoreTextClass(score)}`}>{score}</span>
        <span className="text-xs text-zinc-600 mt-1">/ 100</span>
      </div>
    </div>
  )
}

// ── Ana bileşen ───────────────────────────────────────────────────────────────
export function CrawlDashboard({ result, jobId }: Props) {
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview')
  const [filters, setFilters] = useState<FilterState>(defaultFilters)
  const [selectedPage, setSelectedPage] = useState<PageResult | null>(null)
  const [sourceUrl, setSourceUrl] = useState<string | null>(null)
  const tableRef = useRef<HTMLDivElement>(null)

  // Kategori bazlı istatistikler (checklist için)
  const categoryStats = useMemo(() => {
    const stats: Record<string, { passed: number; warning: number; failed: number }> = {}
    for (const page of result.pages) {
      for (const check of page.checks) {
        if (!stats[check.category]) stats[check.category] = { passed: 0, warning: 0, failed: 0 }
        stats[check.category][check.status]++
      }
    }
    return stats
  }, [result.pages])

  const checklistCategories = [
    ...CATEGORY_ORDER.filter(c => categoryStats[c]),
    ...Object.keys(categoryStats).filter(c => !CATEGORY_ORDER.includes(c)),
  ]

  // Priority filtresi için sayısal sıra
  const PORDER: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 }

  // Filtrelenmiş sayfa listesi
  const filteredPages = useMemo(() => {
    return result.pages.filter(page => {
      if (filters.search && !page.url.toLowerCase().includes(filters.search.toLowerCase())) return false
      if (filters.status === 'failed' && !page.checks.some(c => c.status === 'failed') && !page.error) return false
      if (filters.status === 'warning' && !page.checks.some(c => c.status === 'warning')) return false
      if (filters.status === 'passed' && page.checks.some(c => c.status !== 'passed')) return false
      if (filters.category && !page.checks.some(c => c.category === filters.category && c.status !== 'passed')) return false
      if (page.score < filters.scoreMin || page.score > filters.scoreMax) return false
      if (filters.priority !== 'all') {
        const threshold = PORDER[filters.priority] ?? 3
        if (!page.checks.some(c =>
          c.status !== 'passed' &&
          c.priority_label != null &&
          (PORDER[c.priority_label] ?? 99) <= threshold
        )) return false
      }
      return true
    })
  }, [result.pages, filters])

  // Checklist kategori seçimi → FilterBar kategori filtresi güncellenir
  function selectCategory(cat: string) {
    const next = filters.category === cat ? null : cat
    setFilters(f => ({ ...f, category: next }))
    if (next) {
      setTimeout(() => tableRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 60)
    }
  }

  // Drawer kapatılınca seçimi sıfırla
  function handleDrawerClose() {
    setSelectedPage(null)
  }

  // Filter key: DataTable'ın sayfa numarasını sıfırlaması için
  const filterKey = `${filters.search}|${filters.status}|${filters.category ?? ''}|${filters.scoreMin}|${filters.scoreMax}|${filters.priority}`

  return (
    <div className="space-y-5">
      {/* Modaller */}
      {sourceUrl && <SourceModal url={sourceUrl} onClose={() => setSourceUrl(null)} />}
      <PageDetailDrawer
        page={selectedPage}
        onClose={handleDrawerClose}
        onSource={url => { setSelectedPage(null); setSourceUrl(url) }}
      />

      {/* ── Tab seçici ────────────────────────────────────────────────────── */}
      <div className="flex gap-1 p-1 bg-zinc-900 border border-zinc-800 rounded-xl w-fit">
        {([['overview', 'Genel Bakış'], ['architecture', 'Mimari Graf']] as const).map(([tab, label]) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-zinc-700 text-zinc-100'
                : 'text-zinc-500 hover:text-zinc-300'
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── Mimari Graf sekmesi ───────────────────────────────────────────── */}
      {activeTab === 'architecture' && (
        <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5">
          <SiteArchitectureGraph
            jobId={jobId}
            pages={result.pages}
            onSelectPage={setSelectedPage}
          />
        </div>
      )}

      {/* ── Genel Bakış sekmesi ───────────────────────────────────────────── */}
      {activeTab === 'overview' && <>

      {/* ── 1. Site Skoru ─────────────────────────────────────────────────── */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <p className="text-xs text-zinc-500 uppercase tracking-widest flex-1 text-center">
            Toplam Site SEO Skoru
          </p>
          <ExportButton jobId={jobId} />
        </div>
        <div className="flex flex-col sm:flex-row items-center gap-8">
          <SiteScoreRing score={result.site_score} />
          <div className="flex-1 w-full space-y-4">
            <p className={`text-2xl font-bold ${scoreTextClass(result.site_score)}`}>
              {scoreLabel(result.site_score)}
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Taranan', value: result.pages_crawled, color: 'text-zinc-100' },
                { label: 'Hatalı', value: result.pages_failed, color: 'text-red-400' },
                ...(result.sitemap_urls_found > 0 ? [
                  { label: 'Sitemap URL', value: result.sitemap_urls_found, color: 'text-blue-400' },
                  { label: 'Erişilemeyen', value: result.sitemap_urls_unreachable, color: 'text-zinc-500' },
                ] : []),
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-zinc-800/40 rounded-lg p-3 text-center">
                  <p className={`text-xl font-bold tabular-nums ${color}`}>{value}</p>
                  <p className="text-xs text-zinc-600 mt-0.5">{label}</p>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[
                { key: 'passed',   label: 'Başarılı',  color: 'text-emerald-400', bg: 'bg-emerald-500/5 border-emerald-500/20' },
                { key: 'warnings', label: 'Uyarı',     color: 'text-amber-400',   bg: 'bg-amber-500/5 border-amber-500/20' },
                { key: 'failed',   label: 'Başarısız', color: 'text-red-400',     bg: 'bg-red-500/5 border-red-500/20' },
              ].map(({ key, label, color, bg }) => (
                <div key={key} className={`border rounded-xl p-3 text-center ${bg}`}>
                  <p className={`text-2xl font-bold tabular-nums ${color}`}>
                    {result.site_summary[key as keyof typeof result.site_summary]}
                  </p>
                  <p className="text-xs text-zinc-500 mt-1">{label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* ── 2. Kategori Kontrol Listesi ───────────────────────────────────── */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-zinc-800">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Kontrol Listesi</h3>
            <p className="text-[10px] text-zinc-600">Kategori seç → tabloyu filtrele</p>
          </div>
        </div>
        <div className="divide-y divide-zinc-800/40">
          {checklistCategories.map(cat => {
            const s = categoryStats[cat]
            const total = s.passed + s.warning + s.failed
            const failRatio = s.failed / total
            const warnRatio = s.warning / total
            const icon = failRatio > 0.2 ? '✗' : warnRatio > 0.3 ? '!' : '✓'
            const iconColor = failRatio > 0.2 ? 'text-red-400' : warnRatio > 0.3 ? 'text-amber-400' : 'text-emerald-400'
            const isActive = filters.category === cat

            return (
              <button
                key={cat}
                onClick={() => selectCategory(cat)}
                className={`w-full flex items-center gap-4 px-5 py-3 transition-colors text-left ${
                  isActive
                    ? 'bg-zinc-800/70 ring-1 ring-inset ring-zinc-600'
                    : 'hover:bg-zinc-800/30'
                }`}
              >
                <span className={`text-sm font-bold w-4 flex-shrink-0 ${iconColor}`}>{icon}</span>
                <span className={`text-sm w-40 flex-shrink-0 ${isActive ? 'text-zinc-100 font-semibold' : 'text-zinc-300'}`}>
                  {CATEGORY_TR[cat] ?? cat}
                </span>
                <div className="flex-1 bg-zinc-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${Math.round((s.passed / total) * 100)}%` }}
                  />
                </div>
                <div className="flex gap-3 text-xs tabular-nums flex-shrink-0">
                  <span className="text-emerald-500">✓{s.passed}</span>
                  {s.warning > 0 && <span className="text-amber-400">!{s.warning}</span>}
                  {s.failed  > 0 && <span className="text-red-400">✗{s.failed}</span>}
                </div>
                {isActive && (
                  <span className="text-[10px] text-zinc-400 border border-zinc-600 rounded px-1.5 py-0.5 flex-shrink-0">
                    seçili
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* ── 3. Filtreli Sayfa Tablosu ─────────────────────────────────────── */}
      <div ref={tableRef} className="space-y-3 scroll-mt-4">
        <FilterBar
          filters={filters}
          categories={checklistCategories}
          onChange={setFilters}
          totalCount={result.pages.length}
          filteredCount={filteredPages.length}
        />
        <DataTable
          pages={filteredPages}
          onSelect={setSelectedPage}
          selectedUrl={selectedPage?.url ?? null}
          resetKey={filterKey}
        />
      </div>

      </> /* end overview tab */}
    </div>
  )
}
