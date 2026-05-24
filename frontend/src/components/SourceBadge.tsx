import { resolveSourceColor } from '../lib/sourceColors'

interface SourceBadgeProps {
  name: string
  sourceId?: string | null
  color?: string | null
  className?: string
}

export default function SourceBadge({ name, sourceId, color, className = '' }: SourceBadgeProps) {
  const hex = resolveSourceColor(sourceId, color)
  return (
    <span className={`inline-flex items-center gap-1.5 text-[10px] font-mono ${className}`}>
      {hex && (
        <span
          className="w-2 h-2 rounded-full shrink-0 border border-black/10"
          style={{ backgroundColor: hex }}
          aria-hidden
        />
      )}
      <span className="text-silver truncate max-w-[120px]">{name}</span>
    </span>
  )
}
