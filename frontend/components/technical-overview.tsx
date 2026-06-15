import type { AnalyzeResponse } from '@/lib/types'
import { trunc } from '@/lib/utils'

interface Props {
  data: AnalyzeResponse
}

function Row({ label, value }: { label: string; value: string }) {
  const isEmpty = value === '—'
  return (
    <div className="flex gap-4 py-3 border-b border-zinc-800/60 last:border-0">
      <span className="w-40 flex-shrink-0 text-xs text-zinc-500 pt-px">{label}</span>
      <span
        className={`flex-1 text-xs font-mono break-all ${isEmpty ? 'text-zinc-700' : 'text-zinc-300'}`}
      >
        {value}
      </span>
    </div>
  )
}

export function TechnicalOverview({ data }: Props) {
  const { url, final_url, status_code, redirected, metadata: m } = data

  const rows: [string, string][] = [
    ['URL', url],
    ['Son URL', final_url],
    ['HTTP Kodu', status_code ? String(status_code) : '—'],
    ['Yönlendirme', redirected ? 'Evet' : 'Hayır'],
    ['Başlık (Title)', trunc(m.title, 120)],
    ['Açıklama (Desc)', trunc(m.description, 180)],
    ['Canonical', trunc(m.canonical, 120)],
    ['Robots', m.robots ?? '—'],
    ['Dil (Lang)', m.lang ?? '—'],
    ['H1 Etiketleri', m.h1.length ? m.h1.join(' / ') : '—'],
    ['H2 Sayısı', String(m.h2_count)],
    ['Schema Türleri', m.schema_types.length ? m.schema_types.join(', ') : '—'],
    ['İç Bağlantılar', String(m.internal_links)],
    ['Dış Bağlantılar', String(m.external_links)],
    ['Toplam Görsel', String(m.images_total)],
    ['Alt Eksik Görsel', String(m.images_missing_alt)],
  ]

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
      <div className="px-5 py-3.5 border-b border-zinc-800">
        <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">
          Teknik Özet
        </h3>
      </div>
      <div className="px-5 py-1">
        {rows.map(([label, value]) => (
          <Row key={label} label={label} value={value} />
        ))}
      </div>
    </div>
  )
}
