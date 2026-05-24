interface HeatBadgeProps {
  level: 'high' | 'medium' | 'low'
  className?: string
}

const labels = { high: '高热', medium: '中热', low: '低热' }

export default function HeatBadge({ level, className = '' }: HeatBadgeProps) {
  return (
    <span className={`inline-block text-[10px] font-mono border border-ink px-1.5 py-0.5 ${className}`}>
      {labels[level]}
    </span>
  )
}
