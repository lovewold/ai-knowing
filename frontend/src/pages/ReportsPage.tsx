import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { Report } from '../types'
import ReportCard from '../components/ReportCard'
import EmptyState from '../components/EmptyState'
import CustomReportPanel from '../components/CustomReportPanel'

const filters = [
  { key: '', label: '\u5168\u90e8' },
  { key: 'custom', label: '\u81ea\u5b9a\u4e49' },
  { key: 'trend', label: '\u8d8b\u52bf' },
  { key: 'tool', label: '\u5de5\u5177' },
  { key: 'agent_survey', label: 'Agent\u5168\u666f' },
  { key: 'daily_briefing', label: '\u6bcf\u65e5\u6668\u62a5' },
  { key: 'scenario', label: '\u573a\u666f' },
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
        <h1 className="font-serif text-3xl font-semibold">{'\u62a5\u544a'}</h1>
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
        <p className="text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>
      ) : reports.length ? (
        <div className="border-t border-ink">{reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} />)}</div>
      ) : (
        <EmptyState
          title={'\u6682\u65e0\u62a5\u544a'}
          description={'\u8f93\u5165\u63cf\u8ff0\u751f\u6210\u68c0\u7d22\u5f0f\u62a5\u544a'}
        />
      )}
    </div>
  )
}
