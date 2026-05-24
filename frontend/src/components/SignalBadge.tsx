const statusLabels: Record<string, string> = {
  high: '\u9ad8\u4fe1\u53f7',
  medium: '\u89c2\u5bdf',
  low: '\u4f4e\u4fe1\u53f7',
}

interface SignalBadgeProps {
  status: string | null
  score?: number | null
}

export default function SignalBadge({ status, score }: SignalBadgeProps) {
  if (!status) return null
  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-[10px]">
      <span className="border border-ink px-1.5 py-0.5">{statusLabels[status] ?? status}</span>
      {score != null && <span className="text-silver">{`${Math.round(score)}\u5206`}</span>}
    </span>
  )
}
