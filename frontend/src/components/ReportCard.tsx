import { Link } from 'react-router-dom'
import type { Report } from '../types'
import TypeBadge from './TypeBadge'

interface ReportCardProps {
  report: Report
  index?: number
}

export default function ReportCard({ report, index = 0 }: ReportCardProps) {
  const date = new Date(report.created_at).toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  return (
    <Link
      to={`/reports/${report.id}`}
      className={`group block border-b border-ink py-5 animate-slide-up opacity-0 stagger-${Math.min(index + 1, 5)} hover:bg-mist transition-colors`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <TypeBadge type={report.type} />
            <span className="text-[10px] font-mono text-silver">{report.quality_label}</span>
          </div>
          <h3 className="font-serif text-lg font-medium leading-snug group-hover:underline underline-offset-4 decoration-1">
            {report.title}
          </h3>
          {report.source_name && (
            <p className="mt-1.5 text-xs text-silver font-mono">{report.source_name}</p>
          )}
        </div>
        <time className="text-xs font-mono text-silver whitespace-nowrap pt-1">{date}</time>
      </div>
    </Link>
  )
}
