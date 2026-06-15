'use client'

import { CATEGORY_TR } from '@/lib/utils'
import type { PriorityLabel } from '@/lib/types'

export type StatusFilter = 'all' | 'failed' | 'warning' | 'passed'

export interface FilterState {
  search: string
  status: StatusFilter
  category: string | null
  scoreMin: number
  scoreMax: number
  priority: 'all' | PriorityLabel
}

export const defaultFilters: FilterState = {
  search: '',
  status: 'all',
  category: null,
  scoreMin: 0,
  scoreMax: 100,
  priority: 'all',
}

interface Props {
  filters: FilterState
  categories: string[]
  onChange: (f: FilterState) => void
  totalCount: number
  filteredCount: number
}

const STATUS_LABELS: Record<StatusFilter, string> = {
  all: 'Tümü',
  failed: 'Hatalı',
  warning: 'Uyarılı',
  passed: 'Başarılı',
}

const STATUS_ACTIVE_CLASS: Record<StatusFilter, string> = {
  all:     'bg-zinc-700 border-zinc-600 text-zinc-100',
  failed:  'bg-red-500/20 border-red-500/40 text-red-400',
  warning: 'bg-amber-500/20 border-amber-500/40 text-amber-400',
  passed:  'bg-emerald-500/20 border-emerald-500/40 text-emerald-400',
}

export function FilterBar({ filters, categories, onChange, totalCount, filteredCount }: Props) {
  const set = <K extends keyof FilterState>(k: K, v: FilterState[K]) =>
    onChange({ ...filters, [k]: v })

  const isDefault =
    filters.search === '' &&
    filters.status === 'all' &&
    filters.category === null &&
    filters.scoreMin === 0 &&
    filters.scoreMax === 100 &&
    filters.priority === 'all'

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 space-y-3">
      {/* Row 1: search + status pills */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* URL search */}
        <div className="relative flex-1">
          <input
            type="text"
            placeholder="URL ara…"
            value={filters.search}
            onChange={e => set('search', e.target.value)}
            className="w-full bg-zinc-800/60 border border-zinc-700/60 rounded-lg px-3 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-zinc-500 transition-colors"
          />
          {filters.search && (
            <button
              onClick={() => set('search', '')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-600 hover:text-zinc-300 text-xs leading-none px-1 transition-colors"
            >
              ✕
            </button>
          )}
        </div>

        {/* Status pills */}
        <div className="flex gap-1 flex-shrink-0">
          {(['all', 'failed', 'warning', 'passed'] as const).map(s => (
            <button
              key={s}
              onClick={() => set('status', s)}
              className={`text-xs px-3 py-2 rounded-lg border transition-colors whitespace-nowrap ${
                filters.status === s
                  ? STATUS_ACTIVE_CLASS[s]
                  : 'border-zinc-700/50 text-zinc-500 hover:text-zinc-300 hover:border-zinc-600'
              }`}
            >
              {STATUS_LABELS[s]}
            </button>
          ))}
        </div>
      </div>

      {/* Row 2: category, priority, score range, count */}
      <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center">
        {/* Category dropdown */}
        <select
          value={filters.category ?? ''}
          onChange={e => set('category', e.target.value || null)}
          className="bg-zinc-800/60 border border-zinc-700/60 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-zinc-500 transition-colors"
        >
          <option value="">Tüm kategoriler</option>
          {categories.map(cat => (
            <option key={cat} value={cat}>{CATEGORY_TR[cat] ?? cat}</option>
          ))}
        </select>

        {/* Priority dropdown */}
        <select
          value={filters.priority}
          onChange={e => set('priority', e.target.value as FilterState['priority'])}
          className="bg-zinc-800/60 border border-zinc-700/60 rounded-lg px-3 py-2 text-sm text-zinc-300 focus:outline-none focus:border-zinc-500 transition-colors"
        >
          <option value="all">Tüm öncelikler</option>
          <option value="critical">Kritik</option>
          <option value="high">Yüksek ve üstü</option>
          <option value="medium">Orta ve üstü</option>
          <option value="low">Düşük ve üstü</option>
        </select>

        {/* Score range */}
        <div className="flex items-center gap-2 text-xs text-zinc-500 flex-shrink-0">
          <span>Skor</span>
          <input
            type="number" min="0" max="100"
            value={filters.scoreMin}
            onChange={e => set('scoreMin', Math.min(Number(e.target.value), filters.scoreMax))}
            className="w-14 bg-zinc-800/60 border border-zinc-700/60 rounded px-2 py-1.5 text-zinc-300 text-xs focus:outline-none focus:border-zinc-500 text-center transition-colors"
          />
          <span>–</span>
          <input
            type="number" min="0" max="100"
            value={filters.scoreMax}
            onChange={e => set('scoreMax', Math.max(Number(e.target.value), filters.scoreMin))}
            className="w-14 bg-zinc-800/60 border border-zinc-700/60 rounded px-2 py-1.5 text-zinc-300 text-xs focus:outline-none focus:border-zinc-500 text-center transition-colors"
          />
        </div>

        {/* Count + reset */}
        <div className="flex items-center gap-3 flex-1 justify-end flex-wrap">
          <span className="text-xs text-zinc-500 tabular-nums whitespace-nowrap">
            {filteredCount === totalCount
              ? `${totalCount} sayfa`
              : `${filteredCount} / ${totalCount} sayfa`}
          </span>
          {!isDefault && (
            <button
              onClick={() => onChange(defaultFilters)}
              className="text-xs text-zinc-500 hover:text-zinc-200 underline underline-offset-2 transition-colors whitespace-nowrap"
            >
              Sıfırla
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
