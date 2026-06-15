import { scoreLabel, scoreRingColor, scoreTextClass } from '@/lib/utils'

interface Props {
  score: number
  finalUrl: string
  statusCode: number | null
  redirected: boolean
}

const RADIUS = 52
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export function ScoreCard({ score, finalUrl, statusCode, redirected }: Props) {
  const progress = (score / 100) * CIRCUMFERENCE
  const ringColor = scoreRingColor(score)
  const textClass = scoreTextClass(score)
  const label = scoreLabel(score)

  return (
    <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-6 flex items-center gap-6">
      {/* Ring */}
      <div className="relative flex-shrink-0 w-[128px] h-[128px]">
        <svg
          width="128"
          height="128"
          style={{ transform: 'rotate(-90deg)' }}
          aria-hidden="true"
        >
          <circle cx="64" cy="64" r={RADIUS} fill="none" stroke="#27272a" strokeWidth="9" />
          <circle
            cx="64"
            cy="64"
            r={RADIUS}
            fill="none"
            strokeWidth="9"
            strokeLinecap="round"
            strokeDasharray={`${progress} ${CIRCUMFERENCE}`}
            style={{ stroke: ringColor, transition: 'stroke-dasharray 0.6s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold tabular-nums ${textClass}`}>{score}</span>
          <span className="text-[10px] text-zinc-600 mt-0.5 tracking-wide">/ 100</span>
        </div>
      </div>

      {/* Info */}
      <div className="min-w-0">
        <p className="text-xs text-zinc-500 uppercase tracking-widest mb-1">SEO Skoru</p>
        <p className={`text-xl font-semibold mb-3 ${textClass}`}>{label}</p>
        <div className="space-y-1">
          <p className="text-sm text-zinc-500 font-mono truncate">{finalUrl}</p>
          <div className="flex items-center gap-3 text-xs text-zinc-500">
            {statusCode && (
              <span
                className={
                  statusCode < 300
                    ? 'text-emerald-500'
                    : statusCode < 400
                    ? 'text-amber-500'
                    : 'text-red-500'
                }
              >
                HTTP {statusCode}
              </span>
            )}
            {redirected && <span className="text-amber-600">Yönlendirme</span>}
          </div>
        </div>
      </div>
    </div>
  )
}
