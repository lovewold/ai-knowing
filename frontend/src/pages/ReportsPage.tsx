import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { Report } from '../types'
import ReportCard from '../components/ReportCard'
import EmptyState from '../components/EmptyState'
import CustomReportPanel from '../components/CustomReportPanel'

const filters = [
  { key: '', label: '全部' },
  { key: 'custom', label: '自定义' },
  { key: 'trend', label: '趋势' },
  { key: 'tool', label: '工具' },
  { key: 'agent_survey', label: 'Agent全景' },
  { key: 'daily_briefing', label: '每日晨报' },
  { key: 'scenario', label: '场景' },
]

export default function ReportsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeType = searchParams.get('type') ?? ''
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    api.getReports(activeType || undefined).then(setReports).catch(console.error).finally(() => setLoading(false))
  }, [activeType])

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <header className="mb-8 pb-6 border-b border-ink">
        <h1 className="font-serif text-3xl font-semibold">AI 报告</h1>
        <p className="mt-2 text-sm text-ash">
          自动生成的技术报告，或用自然语言描述生成任意类型报告
        </p>
      </header>

      <CustomReportPanel />

      <div className="flex mb-8 border border-ink inline-flex flex-wrap">
        {filters.map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setSearchParams(key ? { type: key } : {})}
            className={`px-4 py-2 text-sm font-medium border-r border-ink last:border-r-0 ${activeType === key ? 'bg-ink text-paper' : 'hover:bg-mist text-ash'}`}
          >
            {label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-silver font-mono">加载中...</p>
      ) : reports.length ? (
        <div className="border-t border-ink">{reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} />)}</div>
      ) : (
        <EmptyState
          title="暂无报告"
          description="在上方填写报告描述生成自定义报告，或触发抓取自动生成"
        />
      )}
    </div>
  )
}
