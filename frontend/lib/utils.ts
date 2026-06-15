import type { Check, CheckStatus, PriorityLabel, EffortLabel } from './types'

export const CATEGORY_ORDER = [
  'Meta',
  'Content',
  'URL',
  'Indexability',
  'Headings',
  'Schema',
  'Images',
  'Links',
  'Social',
  'HTTP',
  'Structure',
  'PageSpeed',
]

export const CATEGORY_TR: Record<string, string> = {
  Meta: 'Meta Etiketleri',
  Content: 'İçerik Analizi',
  URL: 'URL Kalitesi',
  Indexability: 'İndekslenebilirlik',
  Headings: 'Başlıklar',
  Schema: 'Schema Yapısı',
  Images: 'Görseller',
  Links: 'Bağlantılar',
  Social: 'Sosyal Etiketler',
  HTTP: 'HTTP & Teknik',
  Structure: 'Yapısal Etiketler',
  PageSpeed: 'PageSpeed',
}

export const STATUS_TR: Record<CheckStatus, string> = {
  passed: 'başarılı',
  warning: 'uyarı',
  failed: 'başarısız',
}

export const SOURCE_TR: Record<string, string> = {
  start: 'başlangıç',
  sitemap: 'sitemap',
  crawl: 'tarama',
}

export function scoreLabel(score: number): string {
  if (score >= 80) return 'İyi'
  if (score >= 50) return 'Geliştirilmeli'
  return 'Zayıf'
}

export function scoreRingColor(score: number): string {
  if (score >= 80) return '#10b981'
  if (score >= 50) return '#f59e0b'
  return '#ef4444'
}

export function scoreTextClass(score: number): string {
  if (score >= 80) return 'text-emerald-400'
  if (score >= 50) return 'text-amber-400'
  return 'text-red-400'
}

export function statusBadgeClass(status: CheckStatus): string {
  switch (status) {
    case 'passed':  return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/25'
    case 'warning': return 'bg-amber-500/10  text-amber-400  border-amber-500/25'
    case 'failed':  return 'bg-red-500/10    text-red-400    border-red-500/25'
  }
}

export function trunc(value: string | null, max: number): string {
  if (!value) return '—'
  return value.length > max ? value.slice(0, max) + '…' : value
}

function escapeCsvField(value: string): string {
  if (/[",\n\r]/.test(value)) {
    return `"${value.replace(/"/g, '""')}"`
  }
  return value
}

export function downloadCsv(filename: string, rows: string[][]): void {
  const content = '\uFEFF' + rows.map(row => row.map(escapeCsvField).join(',')).join('\n')
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function slugifyFilename(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    || 'export'
}

// \u2500\u2500 Priority / effort helpers \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500

export const PRIORITY_ORDER: Record<PriorityLabel, number> = {
  critical: 0,
  high: 1,
  medium: 2,
  low: 3,
}

export const PRIORITY_TR: Record<PriorityLabel, string> = {
  critical: 'Kritik',
  high: 'Y\u00fcksek',
  medium: 'Orta',
  low: 'D\u00fc\u015f\u00fck',
}

export const EFFORT_TR: Record<EffortLabel, string> = {
  low: 'Kolay',
  medium: 'Orta',
  high: 'Zor',
}

export function priorityBadgeClass(label: PriorityLabel): string {
  switch (label) {
    case 'critical': return 'bg-red-500/15 text-red-400 border-red-500/30'
    case 'high':     return 'bg-orange-500/15 text-orange-400 border-orange-500/30'
    case 'medium':   return 'bg-amber-500/15 text-amber-400 border-amber-500/30'
    case 'low':      return 'bg-zinc-500/15 text-zinc-400 border-zinc-600/40'
  }
}

export function effortBadgeClass(effort: EffortLabel): string {
  switch (effort) {
    case 'low':    return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
    case 'medium': return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
    case 'high':   return 'bg-purple-500/10 text-purple-400 border-purple-500/20'
  }
}

export function pageTopPriority(checks: Check[]): PriorityLabel | null {
  let best: PriorityLabel | null = null
  for (const c of checks) {
    if (c.status === 'passed' || !c.priority_label) continue
    if (best === null || PRIORITY_ORDER[c.priority_label] < PRIORITY_ORDER[best]) {
      best = c.priority_label
    }
  }
  return best
}
