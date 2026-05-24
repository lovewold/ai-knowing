const typeLabels: Record<string, string> = {
  trend: '趋势',
  tool: '工具',
  scenario: '场景',
  agent_survey: 'Agent全景',
  custom: '自定义',
  daily_briefing: '每日晨报',
}

interface TypeBadgeProps {
  type: string
  className?: string
}

export default function TypeBadge({ type, className = '' }: TypeBadgeProps) {
  return (
    <span
      className={`inline-block border border-ink px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider ${className}`}
    >
      {typeLabels[type] ?? type}
    </span>
  )
}
