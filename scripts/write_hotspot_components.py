from pathlib import Path

content = r'''import type { Hotspot } from '../types'
import HeatBadge from './HeatBadge'
import SignalBadge from './SignalBadge'

interface HotCardProps {
  hotspot: Hotspot
  rank?: number
}

export default function HotCard({ hotspot, rank }: HotCardProps) {
  const date = new Date(hotspot.fetched_at).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <a
      href={hotspot.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block border border-ink bg-paper p-4 hover:bg-mist transition-colors h-full"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="flex items-center gap-2 flex-wrap">
          {rank != null && (
            <span className="font-serif text-lg font-semibold text-silver w-6">{rank}</span>
          )}
          <HeatBadge level={hotspot.heat_level} />
          {hotspot.is_new && (
            <span className="text-[10px] font-mono border border-ink px-1.5 py-0.5">NEW</span>
          )}
          {hotspot.cross_source_count > 0 && (
            <span className="text-[10px] font-mono text-silver">
              {hotspot.cross_source_count + 1}\u6e90
            </span>
          )}
        </div>
        <SignalBadge status={hotspot.signal_status} score={hotspot.signal_score} />
      </div>
      <h3 className="font-serif text-base font-medium leading-snug group-hover:underline underline-offset-2 line-clamp-2">
        {hotspot.title}
      </h3>
      {hotspot.summary && (
        <p className="text-xs text-ash mt-2 leading-relaxed line-clamp-2">{hotspot.summary}</p>
      )}
      <div className="mt-3 flex items-center justify-between text-[10px] font-mono text-silver">
        <span>{hotspot.source}</span>
        <span>{date}</span>
      </div>
    </a>
  )
}
'''

text = content.encode('utf-8').decode('unicode_escape')
Path(r'c:\Users\user\Desktop\ai-know(1)\frontend\src\components\HotCard.tsx').write_text(text, encoding='utf-8')

heat = r'''interface HeatBadgeProps {
  level: 'high' | 'medium' | 'low'
  className?: string
}

const labels = { high: '\u9ad8\u70ed', medium: '\u4e2d\u70ed', low: '\u4f4e\u70ed' }

export default function HeatBadge({ level, className = '' }: HeatBadgeProps) {
  return (
    <span className={`inline-block text-[10px] font-mono border border-ink px-1.5 py-0.5 ${className}`}>
      {labels[level]}
    </span>
  )
}
'''
Path(r'c:\Users\user\Desktop\ai-know(1)\frontend\src\components\HeatBadge.tsx').write_text(
    heat.encode('utf-8').decode('unicode_escape'), encoding='utf-8'
)
print('done')
