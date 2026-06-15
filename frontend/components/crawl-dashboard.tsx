'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import type { CrawlResult, PageResult, Check } from '@/lib/types'
import {
  CATEGORY_ORDER, CATEGORY_TR,
  scoreLabel, scoreRingColor, scoreTextClass, SOURCE_TR, statusBadgeClass, STATUS_TR,
} from '@/lib/utils'
import { fetchPageSource } from '@/lib/api'

interface Props { result: CrawlResult }

// ── Küçük skor halkası (modal başlığı için) ───────────────────────────────────
function ScoreRing({ score, size = 96 }: { score: number; size?: number }) {
  const R = size / 2 - 8
  const C = 2 * Math.PI * R
  return (
    <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={R} fill="none" stroke="#27272a" strokeWidth="8" />
        <circle cx={size/2} cy={size/2} r={R} fill="none" strokeWidth="8" strokeLinecap="round"
          strokeDasharray={`${(score / 100) * C} ${C}`}
          style={{ stroke: scoreRingColor(score) }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className={`font-bold tabular-nums leading-none ${scoreTextClass(score)}`}
          style={{ fontSize: size * 0.27 }}>{score}</span>
        <span className="text-zinc-600 mt-0.5" style={{ fontSize: size * 0.1 }}>/ 100</span>
      </div>
    </div>
  )
}

// ── Kaynak kodu modalı ────────────────────────────────────────────────────────
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}>
      <div className="bg-zinc-950 border border-zinc-800 rounded-xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800 gap-3 flex-shrink-0">
          <p className="text-xs font-mono text-zinc-400 truncate flex-1">{url}</p>
          <div className="flex gap-2 flex-shrink-0">
            <a href={url} target="_blank" rel="noopener noreferrer"
              className="text-xs text-blue-400 hover:text-blue-300 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors">
              Sayfayı Aç ↗
            </a>
            {html && (
              <button onClick={() => navigator.clipboard.writeText(html).then(() => setCopied(true))}
                className="text-xs text-zinc-400 hover:text-zinc-200 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors">
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

// ── Sayfa detay modalı ────────────────────────────────────────────────────────
function PageDetailModal({ page, onClose, onSource }: {
  page: PageResult
  onClose: () => void
  onSource: () => void
}) {
  const passed   = page.checks.filter(c => c.status === 'passed').length
  const warnings = page.checks.filter(c => c.status === 'warning').length
  const failed   = page.checks.filter(c => c.status === 'failed').length

  // Tüm check'leri kategoriye göre grupla
  const grouped: Record<string, Check[]> = {}
  for (const c of page.checks) {
    if (!grouped[c.category]) grouped[c.category] = []
    grouped[c.category].push(c)
  }
  const orderedCats = [
    ...CATEGORY_ORDER.filter(c => grouped[c]),
    ...Object.keys(grouped).filter(c => !CATEGORY_ORDER.includes(c)),
  ]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={e => { if (e.target === e.currentTarget) onClose() }}>
      <div className="bg-zinc-950 border border-zinc-800 rounded-xl w-full max-w-3xl max-h-[90vh] flex flex-col shadow-2xl">

        {/* ── Modal başlık ── */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-zinc-800 gap-3 flex-shrink-0">
          <div className="flex items-center gap-4 min-w-0">
            <ScoreRing score={page.score} size={64} />
            <div className="min-w-0">
              <p className={`text-lg font-bold ${scoreTextClass(page.score)}`}>
                {scoreLabel(page.score)}
              </p>
              <p className="text-xs font-mono text-zinc-500 truncate mt-0.5" title={page.url}>
                {page.url}
              </p>
              <div className="flex gap-3 mt-1.5 text-xs tabular-nums">
                <span className="text-emerald-500">✓ {passed} başarılı</span>
                <span className="text-amber-400">! {warnings} uyarı</span>
                <span className="text-red-400">✗ {failed} hatalı</span>
              </div>
            </div>
          </div>
          <div className="flex gap-2 flex-shrink-0 self-start">
            <a href={page.url} target="_blank" rel="noopener noreferrer"
              className="text-xs text-blue-400 hover:text-blue-300 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors whitespace-nowrap">
              ↗ Aç
            </a>
            <button onClick={onSource}
              className="text-xs text-zinc-400 hover:text-zinc-200 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors">
              &lt;/&gt;
            </button>
            <button onClick={onClose}
              className="text-xs text-zinc-500 hover:text-zinc-200 px-3 py-1.5 border border-zinc-700 rounded-lg transition-colors">
              ✕
            </button>
          </div>
        </div>

        {/* ── İçerik ── */}
        {page.error ? (
          <p className="p-6 text-sm text-red-400 font-mono">{page.error}</p>
        ) : (
          <div className="overflow-y-auto flex-1 px-5 py-4 space-y-5">
            {orderedCats.map(cat => {
              const checks = grouped[cat]
              const catFailed   = checks.filter(c => c.status === 'failed').length
              const catWarnings = checks.filter(c => c.status === 'warning').length
              const catPassed   = checks.filter(c => c.status === 'passed').length
              const dotColor = catFailed > 0 ? 'bg-red-500' : catWarnings > 0 ? 'bg-amber-500' : 'bg-emerald-500'

              return (
                <div key={cat}>
                  {/* Kategori başlığı */}
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`w-2 h-2 rounded-full flex-shrink-0 ${dotColor}`} />
                    <h4 className="text-xs font-semibold text-zinc-300 uppercase tracking-wider flex-1">
                      {CATEGORY_TR[cat] ?? cat}
                    </h4>
                    <span className="text-xs text-zinc-600 tabular-nums">
                      {catPassed}/{checks.length} başarılı
                    </span>
                  </div>

                  {/* Check satırları */}
                  <div className="space-y-2 border-l border-zinc-800 pl-4">
                    {checks.map(c => (
                      <div key={c.id} className="flex gap-3">
                        {/* Durum rozeti */}
                        <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold border flex-shrink-0 mt-px ${statusBadgeClass(c.status)}`}>
                          {STATUS_TR[c.status]}
                        </span>
                        <div className="min-w-0 flex-1">
                          <p className="text-xs text-zinc-200 font-medium">{c.label}</p>
                          <p className="text-xs text-zinc-500 mt-0.5 leading-relaxed">{c.message}</p>
                          {c.value && (
                            <p className="text-[11px] font-mono text-zinc-600 bg-zinc-900 border border-zinc-800 rounded px-2 py-1 mt-1 break-all">
                              {c.value}
                            </p>
                          )}
                          {c.recommendation && (
                            <p className="text-xs text-indigo-400/80 mt-1">→ {c.recommendation}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Büyük site skoru halkası ──────────────────────────────────────────────────
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

// ── Kompakt URL satırı ────────────────────────────────────────────────────────
function PageRow({ page, selectedCategory }: { page: PageResult; selectedCategory: string | null }) {
  const [detailOpen, setDetailOpen] = useState(false)
  const [sourceOpen, setSourceOpen] = useState(false)

  const passed   = page.checks.filter(c => c.status === 'passed').length
  const warnings = page.checks.filter(c => c.status === 'warning').length
  const failed   = page.checks.filter(c => c.status === 'failed').length
  const tc       = scoreTextClass(page.score)

  const catChecks = selectedCategory
    ? page.checks
        .filter(c => c.category === selectedCategory && c.status !== 'passed')
        .sort((a, b) => (a.status === 'failed' ? -1 : 1) - (b.status === 'failed' ? -1 : 1))
    : []

  return (
    <>
      {detailOpen && (
        <PageDetailModal
          page={page}
          onClose={() => setDetailOpen(false)}
          onSource={() => { setDetailOpen(false); setSourceOpen(true) }}
        />
      )}
      {sourceOpen && (
        <SourceModal url={page.url} onClose={() => setSourceOpen(false)} />
      )}

      <div className="border-b border-zinc-800/50 last:border-0 group hover:bg-zinc-800/20 transition-colors">
        <div className="flex items-center gap-3 px-4 py-2.5">
          {/* Skor */}
          <span className={`text-xs font-bold tabular-nums w-7 flex-shrink-0 text-right ${page.error ? 'text-red-400' : tc}`}>
            {page.error ? '—' : page.score}
          </span>

          {/* URL — tıklayınca detay modalı açılır */}
          <button
            onClick={() => setDetailOpen(true)}
            className="flex-1 min-w-0 text-xs font-mono text-zinc-400 hover:text-zinc-100 truncate transition-colors text-left"
            title={page.url}
          >
            {page.url}
          </button>

          {/* Mini istatistikler */}
          <div className="hidden sm:flex items-center gap-2 text-xs tabular-nums flex-shrink-0">
            {page.error ? (
              <span className="text-red-400 text-[10px]">hata</span>
            ) : (
              <>
                {passed   > 0 && <span className="text-emerald-600">✓{passed}</span>}
                {warnings > 0 && <span className="text-amber-500">!{warnings}</span>}
                {failed   > 0 && <span className="text-red-500">✗{failed}</span>}
              </>
            )}
          </div>

          {/* Yeni sekmede aç */}
          <a
            href={page.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={e => e.stopPropagation()}
            className="text-[10px] text-zinc-700 hover:text-blue-400 flex-shrink-0 transition-colors opacity-0 group-hover:opacity-100 px-1"
            title="Sayfayı yeni sekmede aç"
          >
            ↗
          </a>

          {/* Kaynak kodu */}
          <button
            onClick={() => setSourceOpen(true)}
            className="text-[10px] text-zinc-700 hover:text-zinc-400 flex-shrink-0 transition-colors opacity-0 group-hover:opacity-100 px-1"
            title="Kaynak kodu"
          >
            &lt;/&gt;
          </button>
        </div>

        {/* Seçili kategorideki hatalı/uyarılı check'ler */}
        {catChecks.length > 0 && (
          <div className="px-4 pb-2.5 space-y-1 ml-10">
            {catChecks.map(c => (
              <div key={c.id} className="flex items-start gap-2">
                <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold border flex-shrink-0 mt-px ${statusBadgeClass(c.status)}`}>
                  {STATUS_TR[c.status]}
                </span>
                <div className="min-w-0">
                  <p className="text-[11px] text-zinc-300 font-medium leading-tight">{c.label}</p>
                  <p className="text-[11px] text-zinc-600 leading-snug">{c.message}</p>
                  {c.value && (
                    <p className="text-[10px] font-mono text-zinc-600 bg-zinc-900 border border-zinc-800/60 rounded px-2 py-0.5 mt-0.5 break-all">
                      {c.value}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

// ── Ana bileşen ───────────────────────────────────────────────────────────────
export function CrawlDashboard({ result }: Props) {
  const [pageFilter, setPageFilter]       = useState<'all' | 'failed' | 'warning'>('all')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showAll, setShowAll]             = useState(false)
  const PAGE_SIZE = 100
  const pageListRef = useRef<HTMLDivElement>(null)

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

  const filteredPages = useMemo(() => {
    let pages = result.pages

    // Kategori filtresi: yalnızca o kategoride sorunlu olan sayfalar
    if (selectedCategory) {
      pages = pages
        .filter(p => p.checks.some(c => c.category === selectedCategory && c.status !== 'passed'))
        .slice()
        .sort((a, b) => {
          const failA = a.checks.filter(c => c.category === selectedCategory && c.status === 'failed').length
          const failB = b.checks.filter(c => c.category === selectedCategory && c.status === 'failed').length
          if (failB !== failA) return failB - failA
          const warnA = a.checks.filter(c => c.category === selectedCategory && c.status === 'warning').length
          const warnB = b.checks.filter(c => c.category === selectedCategory && c.status === 'warning').length
          return warnB - warnA
        })
      return pages
    }

    // Durum filtresi (kategori seçili değilken)
    if (pageFilter === 'failed')  return pages.filter(p => p.checks.some(c => c.status === 'failed') || !!p.error)
    if (pageFilter === 'warning') return pages.filter(p => p.checks.some(c => c.status === 'warning'))
    return pages
  }, [result.pages, selectedCategory, pageFilter])

  const displayPages = showAll ? filteredPages : filteredPages.slice(0, PAGE_SIZE)

  function selectCategory(cat: string) {
    const isDeselect = selectedCategory === cat
    setSelectedCategory(isDeselect ? null : cat)
    setShowAll(false)
    if (!isDeselect) {
      setTimeout(() => {
        pageListRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 50)
    }
  }

  return (
    <div className="space-y-5">

      {/* ── 1. Kontrol Listesi ─────────────────────────────────────────────── */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
        <div className="px-5 py-3.5 border-b border-zinc-800">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">Kontrol Listesi</h3>
            <p className="text-[10px] text-zinc-600">Kategori seç → listeyi filtrele</p>
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
            const isActive = selectedCategory === cat

            return (
              <button
                key={cat}
                onClick={() => selectCategory(cat)}
                className={`w-full flex items-center gap-4 px-5 py-3 transition-colors text-left
                  ${isActive
                    ? 'bg-zinc-800/70 ring-1 ring-inset ring-zinc-600'
                    : 'hover:bg-zinc-800/30'
                  }`}
              >
                <span className={`text-sm font-bold w-4 flex-shrink-0 ${iconColor}`}>{icon}</span>
                <span className={`text-sm w-40 flex-shrink-0 ${isActive ? 'text-zinc-100 font-semibold' : 'text-zinc-300'}`}>
                  {CATEGORY_TR[cat] ?? cat}
                </span>
                <div className="flex-1 bg-zinc-800 rounded-full h-1.5 overflow-hidden">
                  <div className="h-full rounded-full bg-emerald-500"
                    style={{ width: `${Math.round((s.passed / total) * 100)}%` }} />
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

      {/* ── 2. Sayfa Listesi ───────────────────────────────────────────────── */}
      <div ref={pageListRef} className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3.5 border-b border-zinc-800 gap-3">
          <div className="flex items-center gap-3 flex-wrap min-w-0">
            <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider flex-shrink-0">
              Taranan Sayfalar
            </h3>
            <span className="text-xs text-zinc-600 tabular-nums flex-shrink-0">
              {filteredPages.length} URL
            </span>
            {selectedCategory && (
              <div className="flex items-center gap-1.5 bg-zinc-800 rounded-full pl-3 pr-1.5 py-1">
                <span className="text-xs text-zinc-300">{CATEGORY_TR[selectedCategory] ?? selectedCategory}</span>
                <button
                  onClick={() => { setSelectedCategory(null); setShowAll(false) }}
                  className="text-zinc-500 hover:text-zinc-200 transition-colors text-xs leading-none px-1"
                  title="Filtreyi kaldır"
                >
                  ✕
                </button>
              </div>
            )}
          </div>
          {!selectedCategory && (
            <div className="flex gap-1 flex-shrink-0">
              {(['all', 'failed', 'warning'] as const).map(f => (
                <button key={f}
                  onClick={() => { setPageFilter(f); setShowAll(false) }}
                  className={`text-xs px-3 py-1.5 rounded-lg transition-colors ${
                    pageFilter === f ? 'bg-zinc-700 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'
                  }`}>
                  {f === 'all' ? 'Tümü' : f === 'failed' ? 'Hatalı' : 'Uyarılı'}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Kolon başlıkları */}
        <div className="flex items-center gap-3 px-4 py-2 bg-zinc-900/60 border-b border-zinc-800/60">
          <span className="text-[10px] text-zinc-600 w-7 text-right flex-shrink-0">SKOR</span>
          <span className="text-[10px] text-zinc-600 flex-1">URL — tıkla → detay</span>
          <span className="text-[10px] text-zinc-600 hidden sm:block w-24 text-right flex-shrink-0">✓ / ! / ✗</span>
          <span className="w-10 flex-shrink-0" />
        </div>

        <div>
          {filteredPages.length === 0 ? (
            <p className="px-5 py-8 text-sm text-zinc-600 text-center">
              {selectedCategory
                ? `"${CATEGORY_TR[selectedCategory] ?? selectedCategory}" kategorisinde sorunlu sayfa bulunamadı.`
                : 'Sonuç bulunamadı.'
              }
            </p>
          ) : (
            displayPages.map(page => <PageRow key={page.url} page={page} selectedCategory={selectedCategory} />)
          )}
        </div>

        {filteredPages.length > PAGE_SIZE && !showAll && (
          <button onClick={() => setShowAll(true)}
            className="w-full py-3 text-xs text-zinc-500 hover:text-zinc-300 border-t border-zinc-800/50 transition-colors">
            {filteredPages.length - PAGE_SIZE} URL daha göster
          </button>
        )}
      </div>

      {/* ── 3. Toplam Site Skoru ───────────────────────────────────────────── */}
      <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6">
        <p className="text-xs text-zinc-500 uppercase tracking-widest text-center mb-6">
          Toplam Site SEO Skoru
        </p>
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

    </div>
  )
}
