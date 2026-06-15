'use client'

import { useState } from 'react'
import type { Check, SiteIssue, PriorityLabel } from '@/lib/types'
import { PRIORITY_TR, PRIORITY_ORDER } from '@/lib/utils'
import { AuditItem } from './audit-item'

interface Props {
  checks?: Check[]
  siteIssues?: SiteIssue[]
  title?: string
}

// Visual config per priority tier
const TIER: Record<PriorityLabel, {
  headerBg: string
  borderL: string
  dot: string
  countCls: string
  defaultOpen: boolean
}> = {
  critical: {
    headerBg: 'bg-red-500/10 hover:bg-red-500/15',
    borderL: 'border-l-red-500',
    dot: 'bg-red-500',
    countCls: 'bg-red-500/20 text-red-400 border-red-500/30',
    defaultOpen: true,
  },
  high: {
    headerBg: 'bg-orange-500/10 hover:bg-orange-500/15',
    borderL: 'border-l-orange-500',
    dot: 'bg-orange-400',
    countCls: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
    defaultOpen: true,
  },
  medium: {
    headerBg: 'bg-amber-500/8 hover:bg-amber-500/12',
    borderL: 'border-l-amber-400',
    dot: 'bg-amber-400',
    countCls: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    defaultOpen: false,
  },
  low: {
    headerBg: 'bg-zinc-800/30 hover:bg-zinc-800/50',
    borderL: 'border-l-zinc-600',
    dot: 'bg-zinc-600',
    countCls: 'bg-zinc-700/50 text-zinc-400 border-zinc-600/40',
    defaultOpen: false,
  },
}

const PRIORITY_KEYS: PriorityLabel[] = ['critical', 'high', 'medium', 'low']

// Convert a SiteIssue into a Check-shaped object so AuditItem can render it.
function toCheck(si: SiteIssue): Check {
  const examples = si.example_urls.slice(0, 3)
  return {
    id: si.check_id,
    category: si.category,
    label: si.label,
    status: si.status,
    message:
      si.page_count === 1
        ? '1 sayfada tespit edildi'
        : `${si.page_count} sayfada tespit edildi`,
    value: examples.length > 0 ? examples.join('\n') : null,
    recommendation: null,
    priority_label: si.priority_label,
    effort: si.effort,
    why_it_matters: si.why_it_matters,
    how_to_fix: si.how_to_fix,
  }
}

export function HintsPanel({ checks, siteIssues, title = 'Öncelikli Aksiyonlar' }: Props) {
  const [open, setOpen] = useState<Record<PriorityLabel, boolean>>(() => ({
    critical: true,
    high: true,
    medium: false,
    low: false,
  }))

  // Normalize both input sources to Check[]
  const items: Check[] = [
    ...(checks ?? []).filter(c => c.status !== 'passed' && c.priority_label != null),
    ...(siteIssues ?? []).filter(si => si.priority_label != null).map(toCheck),
  ]

  if (items.length === 0) return null

  // Group by priority, preserving PRIORITY_ORDER within each group
  const grouped: Record<PriorityLabel, Check[]> = {
    critical: [],
    high: [],
    medium: [],
    low: [],
  }
  for (const item of items) {
    grouped[item.priority_label!].push(item)
  }

  const urgentCount = grouped.critical.length + grouped.high.length

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
      {/* Panel header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800">
        <div className="flex items-center gap-2.5">
          <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">
            {title}
          </h3>
          {urgentCount > 0 && (
            <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold border bg-red-500/15 text-red-400 border-red-500/30">
              {urgentCount} acil
            </span>
          )}
        </div>
        <span className="text-xs text-zinc-600 tabular-nums">{items.length} sorun</span>
      </div>

      {/* Accordion groups */}
      <div className="divide-y divide-zinc-800/40">
        {PRIORITY_KEYS.map(key => {
          const group = grouped[key]
          if (group.length === 0) return null
          const t = TIER[key]
          const isOpen = open[key]

          return (
            <div key={key}>
              {/* Group toggle */}
              <button
                onClick={() => setOpen(o => ({ ...o, [key]: !o[key] }))}
                className={`w-full flex items-center gap-3 px-5 py-3 border-l-2 transition-colors text-left ${t.headerBg} ${t.borderL}`}
              >
                <span className={`w-2 h-2 rounded-full flex-shrink-0 ${t.dot}`} />
                <span className="text-sm font-semibold text-zinc-200 flex-1">
                  {PRIORITY_TR[key]}
                </span>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border tabular-nums ${t.countCls}`}>
                  {group.length}
                </span>
                <span
                  className="text-zinc-500 text-xs transition-transform duration-150"
                  style={{ display: 'inline-block', transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)' }}
                >
                  ▾
                </span>
              </button>

              {/* Group items — reuse AuditItem */}
              {isOpen && (
                <div className="px-5 border-t border-zinc-800/30">
                  {group.map(c => (
                    <AuditItem key={`${c.id}-${c.status}`} check={c} />
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
