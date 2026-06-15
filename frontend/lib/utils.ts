import type { CheckStatus } from './types'

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
