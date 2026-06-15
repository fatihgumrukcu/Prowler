import type { Summary } from '@/lib/types'

interface Props {
  summary: Summary
}

const items = [
  {
    key: 'passed' as const,
    label: 'Başarılı',
    color: 'text-emerald-400',
    border: 'border-emerald-500/20',
    bg: 'bg-emerald-500/5',
  },
  {
    key: 'warnings' as const,
    label: 'Uyarı',
    color: 'text-amber-400',
    border: 'border-amber-500/20',
    bg: 'bg-amber-500/5',
  },
  {
    key: 'failed' as const,
    label: 'Başarısız',
    color: 'text-red-400',
    border: 'border-red-500/20',
    bg: 'bg-red-500/5',
  },
]

export function SummaryCards({ summary }: Props) {
  return (
    <div className="grid grid-cols-3 gap-3">
      {items.map(({ key, label, color, border, bg }) => (
        <div
          key={key}
          className={`border rounded-xl p-4 text-center ${border} ${bg}`}
        >
          <p className={`text-3xl font-bold tabular-nums ${color}`}>
            {summary[key]}
          </p>
          <p className="text-xs text-zinc-500 mt-1 tracking-wide">{label}</p>
        </div>
      ))}
    </div>
  )
}
