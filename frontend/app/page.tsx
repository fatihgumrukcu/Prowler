'use client'

import { useEffect, useRef, useState } from 'react'
import type { AnalyzeResponse, CrawlJobResponse } from '@/lib/types'
import { analyzeUrl, startCrawl, getCrawlJob } from '@/lib/api'
import { CATEGORY_ORDER, CATEGORY_TR } from '@/lib/utils'
import { cacheSet, cacheGet, cacheGetLast, cacheClear } from '@/lib/cache'
import { AnalyzerForm } from '@/components/analyzer-form'
import { ScoreCard } from '@/components/score-card'
import { SummaryCards } from '@/components/summary-cards'
import { TechnicalOverview } from '@/components/technical-overview'
import { AuditSection } from '@/components/audit-section'
import { CrawlProgress } from '@/components/crawl-progress'
import { CrawlDashboard } from '@/components/crawl-dashboard'

type Mode = 'analyze' | 'crawl'

export default function HomePage() {
  const [mode, setMode] = useState<Mode>('analyze')
  const [analyzeResult, setAnalyzeResult] = useState<AnalyzeResponse | null>(null)
  const [crawlJob, setCrawlJob] = useState<CrawlJobResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastUrl, setLastUrl] = useState<string>('')
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Restore last result from cache on mount
  useEffect(() => {
    const last = cacheGetLast()
    if (!last) return
    if (last.mode === 'analyze') {
      const cached = cacheGet<AnalyzeResponse>('analyze', last.url)
      if (cached) {
        setAnalyzeResult(cached)
        setMode('analyze')
        setLastUrl(last.url)
      }
    } else if (last.mode === 'crawl') {
      const cached = cacheGet<CrawlJobResponse>('crawl', last.url)
      if (cached && cached.status === 'done') {
        setCrawlJob(cached)
        setMode('crawl')
        setLastUrl(last.url)
      }
    }
  }, [])

  function stopPolling() {
    if (pollRef.current) {
      clearInterval(pollRef.current)
      pollRef.current = null
    }
  }

  async function handleAnalyze(url: string) {
    stopPolling()
    setMode('analyze')
    setLoading(true)
    setError(null)
    setAnalyzeResult(null)
    setCrawlJob(null)
    setLastUrl(url)
    try {
      const data = await analyzeUrl(url)
      setAnalyzeResult(data)
      cacheSet('analyze', url, data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Beklenmeyen bir hata oluştu')
    } finally {
      setLoading(false)
    }
  }

  async function handleCrawl(url: string, maxPages: number) {
    stopPolling()
    setMode('crawl')
    setLoading(true)
    setError(null)
    setAnalyzeResult(null)
    setCrawlJob(null)
    setLastUrl(url)
    cacheClear('crawl', url)
    try {
      const { job_id } = await startCrawl(url, maxPages)
      pollRef.current = setInterval(async () => {
        try {
          const job = await getCrawlJob(job_id)
          setCrawlJob(job)
          if (job.status === 'done') {
            stopPolling()
            setLoading(false)
            cacheSet('crawl', url, job)
          } else if (job.status === 'error') {
            stopPolling()
            setLoading(false)
            setError(job.error ?? 'Tarama sırasında hata oluştu')
          }
        } catch {
          stopPolling()
          setLoading(false)
          setError('Tarama durumu alınamadı')
        }
      }, 2000)
    } catch (err) {
      setLoading(false)
      setError(err instanceof Error ? err.message : 'Tarama başlatılamadı')
    }
  }

  // Group checks for analyze mode
  const groupedChecks: Record<string, AnalyzeResponse['checks']> = {}
  if (analyzeResult) {
    const allCats = [...new Set(analyzeResult.checks.map((c) => c.category))]
    const ordered = [
      ...CATEGORY_ORDER.filter((c) => allCats.includes(c)),
      ...allCats.filter((c) => !CATEGORY_ORDER.includes(c)),
    ]
    for (const cat of ordered) {
      const checks = analyzeResult.checks.filter((c) => c.category === cat)
      if (checks.length) groupedChecks[cat] = checks
    }
  }

  const isCrawling = loading && mode === 'crawl'
  const crawlDone = crawlJob?.status === 'done' && crawlJob.result

  return (
    <div className="min-h-screen bg-[#09090b] text-zinc-100">
      {/* Sticky header */}
      <header className="sticky top-0 z-20 border-b border-zinc-800 bg-zinc-950/80 backdrop-blur-md">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between gap-4">
          <div className="leading-none">
            <span className="text-base font-bold text-zinc-100 tracking-tight">Prowler</span>
            <p className="text-xs text-zinc-500 mt-0.5 tracking-wide">Teknik SEO Analiz Aracı</p>
          </div>
          {lastUrl && !loading && (
            <span className="text-xs text-zinc-500 font-mono hidden sm:block truncate max-w-xs">
              {lastUrl.replace(/^https?:\/\//, '')}
            </span>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-5">
        {/* URL input */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-5">
          <p className="text-xs text-zinc-500 uppercase tracking-widest mb-3">
            Analiz edilecek URL
          </p>
          <AnalyzerForm
            onAnalyze={handleAnalyze}
            onCrawl={handleCrawl}
            loading={loading}
          />
        </div>

        {/* Analyze: loading spinner */}
        {loading && mode === 'analyze' && (
          <div className="flex items-center justify-center py-20 text-zinc-600">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 border-2 border-zinc-700 border-t-zinc-400 rounded-full animate-spin" />
              <span className="text-sm">Sayfa getiriliyor ve analiz ediliyor…</span>
            </div>
          </div>
        )}

        {/* Crawl: progress bar + live feed */}
        {isCrawling && crawlJob && <CrawlProgress job={crawlJob} />}
        {isCrawling && !crawlJob && (
          <div className="flex items-center justify-center py-12 text-zinc-600">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 border-2 border-zinc-700 border-t-blue-400 rounded-full animate-spin" />
              <span className="text-sm">Tarama başlatılıyor…</span>
            </div>
          </div>
        )}

        {/* Error */}
        {error && !loading && (
          <div className="bg-red-500/8 border border-red-500/20 rounded-xl p-5">
            <p className="text-sm font-semibold text-red-400 mb-1">Hata</p>
            <p className="text-xs text-red-400/60 font-mono">{error}</p>
          </div>
        )}

        {/* Analyze results */}
        {analyzeResult && !loading && mode === 'analyze' && (
          <>
            <div className="grid grid-cols-1 gap-4">
              <ScoreCard
                score={analyzeResult.score}
                finalUrl={analyzeResult.final_url}
                statusCode={analyzeResult.status_code}
                redirected={analyzeResult.redirected}
              />
              <SummaryCards summary={analyzeResult.summary} />
            </div>
            <TechnicalOverview data={analyzeResult} />
            <div className="space-y-3">
              <p className="text-xs text-zinc-500 uppercase tracking-widest">Denetim Sonuçları</p>
              {Object.entries(groupedChecks).map(([category, checks]) => (
                <AuditSection key={category} category={category} checks={checks} />
              ))}
            </div>
          </>
        )}

        {/* Crawl: done — show dashboard */}
        {crawlDone && !loading && (
          <CrawlDashboard result={crawlJob!.result!} />
        )}

        {/* Empty state */}
        {!analyzeResult && !crawlJob && !loading && !error && (
          <div className="text-center py-20 text-zinc-700">
            <p className="text-base">Teknik SEO denetimi başlatmak için yukarıya bir URL girin</p>
          </div>
        )}
      </main>
    </div>
  )
}
