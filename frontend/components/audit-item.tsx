import type { Check } from '@/lib/types'
import { statusBadgeClass, STATUS_TR } from '@/lib/utils'

interface Props {
  check: Check
}

export function AuditItem({ check }: Props) {
  return (
    <div className="py-4 border-b border-zinc-800/60 last:border-0">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-sm font-medium text-zinc-200">{check.label}</span>
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border uppercase tracking-wide ${statusBadgeClass(check.status)}`}
        >
          {STATUS_TR[check.status]}
        </span>
      </div>

      <p className="text-sm text-zinc-400 leading-relaxed">{check.message}</p>

      {check.value && (
        <p className="mt-2 text-xs font-mono text-zinc-500 bg-zinc-950/70 border border-zinc-800 rounded px-3 py-2 break-all">
          {check.value}
        </p>
      )}

      {check.recommendation && (
        <p className="mt-2 text-xs text-indigo-400 leading-relaxed">
          <span className="text-indigo-600 mr-1">→</span>
          {check.recommendation}
        </p>
      )}
    </div>
  )
}
