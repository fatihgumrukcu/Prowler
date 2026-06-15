'use client'

import type { CrawlJobResponse } from '@/lib/types'

interface Props {
  job: CrawlJobResponse
}

export function CrawlProgress({ job }: Props) {
  const { progress, live_urls, status } = job
  const done = progress?.pages_done ?? 0
  const found = progress?.pages_found ?? 0
  const failed = progress?.pages_failed ?? 0
  const pct = found > 0 ? Math.round((done / found) * 100) : 0

  const isRunning = status === 'running' || status === 'queued'

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          {isRunning && (
            <div className="w-3 h-3 border-2 border-zinc-600 border-t-blue-400 rounded-full animate-spin flex-shrink-0" />
          )}
          <span className="text-xs font-semibold text-zinc-300 uppercase tracking-wider">
            {status === 'queued' ? 'Sıraya Alındı…' : status === 'running' ? 'Taranıyor…' : 'Tamamlandı'}
          </span>
        </div>
        <span className="text-xs text-zinc-500 tabular-nums">
          {done} / {found > 0 ? found : '?'} sayfa
        </span>
      </div>

      {/* Progress bar */}
      <div className="w-full bg-zinc-800 rounded-full h-2 overflow-hidden">
        <div
          className="h-2 rounded-full bg-blue-500 transition-all duration-500"
          style={{ width: found > 0 ? `${pct}%` : isRunning ? '5%' : '100%' }}
        />
      </div>

      {/* Stats row */}
      <div className="flex gap-6 text-xs">
        <span className="text-zinc-500">
          <span className="text-blue-400 font-semibold tabular-nums">{done}</span> tamamlandı
        </span>
        {failed > 0 && (
          <span className="text-zinc-500">
            <span className="text-red-400 font-semibold tabular-nums">{failed}</span> hatalı
          </span>
        )}
        {found > 0 && (
          <span className="text-zinc-500">
            <span className="text-zinc-300 font-semibold tabular-nums">{found}</span> bulundu
          </span>
        )}
      </div>

      {/* Live URL feed */}
      {live_urls && live_urls.length > 0 && (
        <div className="border-t border-zinc-800 pt-4">
          <p className="text-xs text-zinc-600 uppercase tracking-widest mb-2">
            Taranan Bağlantılar
          </p>
          <div className="max-h-48 overflow-y-auto space-y-1 scrollbar-thin">
            {[...live_urls].reverse().map((url, i) => (
              <p
                key={i}
                className="text-xs font-mono text-zinc-500 truncate hover:text-zinc-300 transition-colors"
                title={url}
              >
                {url}
              </p>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
