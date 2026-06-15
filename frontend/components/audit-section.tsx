import type { Check } from '@/lib/types'
import { CATEGORY_TR } from '@/lib/utils'
import { AuditItem } from './audit-item'

interface Props {
  category: string
  checks: Check[]
}

export function AuditSection({ category, checks }: Props) {
  const passed = checks.filter((c) => c.status === 'passed').length
  const total = checks.length
  const allPassed = passed === total
  const anyFailed = checks.some((c) => c.status === 'failed')

  const headerDot = anyFailed
    ? 'bg-red-500'
    : !allPassed
    ? 'bg-amber-500'
    : 'bg-emerald-500'

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl overflow-hidden">
      {/* Section header */}
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-zinc-800">
        <div className="flex items-center gap-2">
          <span className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${headerDot}`} />
          <h3 className="text-sm font-semibold text-zinc-300 uppercase tracking-wider">
            {CATEGORY_TR[category] ?? category}
          </h3>
        </div>
        <span className="text-xs text-zinc-500 tabular-nums">
          {passed}/{total} başarılı
        </span>
      </div>

      {/* Items */}
      <div className="px-5">
        {checks.map((check) => (
          <AuditItem key={check.id} check={check} />
        ))}
      </div>
    </div>
  )
}
