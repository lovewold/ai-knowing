import type { Hotspot } from '../types'
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
              {hotspot.cross_source_count + 1}源
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
