'use client'

import { useEffect, useState } from 'react'
import type { Check, PageResult } from '@/lib/types'
import {
  CATEGORY_ORDER,
  scoreRingColor, scoreTextClass,
  PRIORITY_ORDER,
  priorityBadgeClass, PRIORITY_TR,
  effortBadgeClass, EFFORT_TR,
} from '@/lib/utils'
import { AuditItem } from './audit-item'
import { AuditSection } from './audit-section'

interface Props {
  page: PageResult | null
  onClose: () => void
  onSource?: (url: string) => void
}

function ScoreRing({ score, size = 56 }: { score: number; size?: number }) {
  const R = size / 2 - 6
  const C = 2 * Math.PI * R
  return (
    <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size / 2} cy={size / 2} r={R} fill="none" stroke="#27272a" strokeWidth="6" />
        <circle
          cx={size / 2} cy={size / 2} r={R}
          fill="none" strokeWidth="6" strokeLinecap="round"
          strokeDasharray={`${(score / 100) * C} ${C}`}
          style={{ stroke: scoreRingColor(score) }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span
          className={`font-bold tabular-nums leading-none ${scoreTextClass(score)}`}
          style={{ fontSize: size * 0.28 }}
        >
          {score}
        </span>
      </div>
    </div>
  )
}

type Tab = 'top' | 'all'

export function PageDetailDrawer({ page, onClose, onSource }: Props) {
  const [tab, setTab] = useState<Tab>('top')

  useEffect(() => {
    if (!page) return
    setTab('top')
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [page, onClose])

  if (!page) return null

  const topIssues: Check[] = [...page.checks]
    .filter(c => c.status !== 'passed' && c.priority_label)
    .sort((a, b) =>
      (PRIORITY_ORDER[a.priority_label!] ?? 99) -
      (PRIORITY_ORDER[b.priority_label!] ?? 99)
    )
    .slice(0, 5)

  const grouped: Record<string, Check[]> = {}
  for (const c of page.checks) {
    if (!grouped[c.category]) grouped[c.category] = []
    grouped[c.category].push(c)
  }
  const orderedCats = [
    ...CATEGORY_ORDER.filter(c => grouped[c]),
    ...Object.keys(grouped).filter(c => !CATEGORY_ORDER.includes(c)),
  ]

  const passed   = page.checks.filter(c => c.status === 'passed').length
  const warnings = page.checks.filter(c => c.status === 'warning').length
  const failed   = page.checks.filter(c => c.status === 'failed').length

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 z-40 bg-black/60 backdrop-blur-[2px]"
        onClick={onClose}
      />

      {/* Drawer panel */}
      <div className="fixed right-0 top-0 h-full z-50 w-full max-w-2xl bg-zinc-950 border-l border-zinc-800 flex flex-col shadow-2xl">

        {/* Header */}
        <div className="flex items-start gap-4 px-5 py-4 border-b border-zinc-800 flex-shrink-0">
          <ScoreRing score={page.score} />
          <div className="flex-1 min-w-0 pt-0.5">
            <p
              className="text-xs font-mono text-zinc-500 truncate leading-relaxed"
              title={page.url}
            >
              {page.url}
            </p>
            <div className="flex items-center gap-3 mt-1.5 flex-wrap">
              {page.status_code && (
                <span className={`text-xs font-mono tabular-nums ${page.status_code < 300 ? 'text-emerald-500' : 'text-red-400'}`}>
                  HTTP {page.status_code}
                </span>
              )}
              <span className="text-xs text-emerald-500 tabular-nums">✓ {passed}</span>
              <span className="text-xs text-amber-400 tabular-nums">! {warnings}</span>
              <span className="text-xs text-red-400 tabular-nums">✗ {failed}</span>
            </div>
          </div>
          <div className="flex gap-1.5 flex-shrink-0 self-start">
            {onSource && (
              <button
                onClick={() => onSource(page.url)}
                className="text-xs px-2.5 py-1.5 border border-zinc-700 rounded-lg text-zinc-400 hover:text-zinc-200 transition-colors"
                title="HTML kaynak kodu"
              >
                &lt;/&gt;
              </button>
            )}
            <a
              href={page.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs px-2.5 py-1.5 border border-zinc-700 rounded-lg text-blue-400 hover:text-blue-300 transition-colors"
            >
              ↗ Aç
            </a>
            <button
              onClick={onClose}
              className="text-xs px-2.5 py-1.5 border border-zinc-700 rounded-lg text-zinc-500 hover:text-zinc-200 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-zinc-800 flex-shrink-0">
          {[
            { id: 'top' as Tab, label: `Kritik Sorunlar (${topIssues.length})` },
            { id: 'all' as Tab, label: `Tüm Kontroller (${page.checks.length})` },
          ].map(t => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex-1 py-3 text-xs font-medium transition-colors ${
                tab === t.id
                  ? 'text-zinc-100 border-b-2 border-zinc-300'
                  : 'text-zinc-500 hover:text-zinc-300 border-b-2 border-transparent'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Body */}
        <div className="overflow-y-auto flex-1 p-5">
          {tab === 'top' ? (
            topIssues.length > 0 ? (
              <div>
                {topIssues.map(c => (
                  <AuditItem key={c.id} check={c} />
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <span className="text-3xl mb-3">✓</span>
                <p className="text-sm text-zinc-500">Bu sayfada öncelikli sorun bulunamadı.</p>
              </div>
            )
          ) : (
            <div className="space-y-4">
              {orderedCats.map(cat => (
                <AuditSection key={cat} category={cat} checks={grouped[cat]} />
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  )
}
