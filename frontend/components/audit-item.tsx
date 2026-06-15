import type { Check } from '@/lib/types'
import {
  statusBadgeClass, STATUS_TR,
  priorityBadgeClass, PRIORITY_TR,
  effortBadgeClass, EFFORT_TR,
} from '@/lib/utils'
import { KNOWLEDGE_TR } from '@/lib/knowledge-tr'

interface Props {
  check: Check
}

export function AuditItem({ check }: Props) {
  const showPriorityMeta = check.status !== 'passed' && (check.priority_label || check.effort)
  const kb = KNOWLEDGE_TR[check.id]
  const why  = check.status !== 'passed' ? (kb?.why  ?? check.why_it_matters)  : null
  const fix  = check.status !== 'passed' ? (kb?.fix  ?? check.how_to_fix ?? check.recommendation) : null

  return (
    <div className="py-4 border-b border-zinc-800/60 last:border-0">
      {/* Label row */}
      <div className="flex items-center gap-2 mb-2 flex-wrap">
        <span className="text-sm font-medium text-zinc-200">{check.label}</span>
        <span
          className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold border uppercase tracking-wide ${statusBadgeClass(check.status)}`}
        >
          {STATUS_TR[check.status]}
        </span>
        {check.priority_label && check.status !== 'passed' && (
          <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold border ${priorityBadgeClass(check.priority_label)}`}>
            {PRIORITY_TR[check.priority_label]}
          </span>
        )}
        {check.effort && check.status !== 'passed' && (
          <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium border ${effortBadgeClass(check.effort)}`}>
            {EFFORT_TR[check.effort]}
          </span>
        )}
      </div>

      <p className="text-sm text-zinc-400 leading-relaxed">{check.message}</p>

      {check.value && (
        <p className="mt-2 text-xs font-mono text-zinc-500 bg-zinc-950/70 border border-zinc-800 rounded px-3 py-2 break-all">
          {check.value}
        </p>
      )}

      {why && (
        <p className="mt-2 text-xs text-zinc-600 leading-relaxed">
          <span className="text-zinc-700 font-medium mr-1">Neden önemli?</span>
          {why}
        </p>
      )}

      {fix && (
        <p className="mt-2 text-xs text-indigo-400 leading-relaxed">
          <span className="text-indigo-600 mr-1">→</span>
          {fix}
        </p>
      )}
    </div>
  )
}
