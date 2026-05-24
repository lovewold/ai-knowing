import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Report, Stats } from '../types'
import StatBlock from '../components/StatBlock'
import ReportCard from '../components/ReportCard'
import EmptyState from '../components/EmptyState'
import HomeBriefingSection from '../components/HomeBriefingSection'

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [reports, setReports] = useState<Report[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getStats(), api.getReports()])
      .then(([s, r]) => { setStats(s); setReports(r.slice(0, 6)) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <section className="border-b border-ink">
        <div className="max-w-6xl mx-auto px-6 py-12 md:py-16">
          <h1 className="font-serif text-4xl md:text-5xl font-semibold leading-tight">AI全知</h1>
          <p className="mt-4 text-ash max-w-2xl text-sm md:text-base leading-relaxed">
            多源 AI 资讯聚合，按信噪比动态分层。每日晨报与深度报告，助你快速把握 AI 行业脉搏。
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/news"
              className="line-border px-6 py-2.5 text-sm font-medium hover:bg-ink hover:text-paper transition-colors"
            >
              浏览 AI 资讯
            </Link>
            <Link
              to="/reports"
              className="px-6 py-2.5 text-sm font-medium border border-smoke text-ash hover:border-ink hover:text-ink transition-colors"
            >
              查看报告
            </Link>
          </div>
        </div>
      </section>

      <HomeBriefingSection />

      {stats && (
        <section className="border-b border-ink bg-mist">
          <div className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBlock label="资讯" value={stats.articles} />
            <StatBlock label="高信号" value={stats.high_signal} />
            <StatBlock label="报告" value={stats.reports} />
            <StatBlock label="数据源" value={stats.sources} />
          </div>
        </section>
      )}

      <section className="max-w-6xl mx-auto px-6 py-14 md:py-16">
        <div className="flex items-center justify-between mb-8 pb-5 border-b border-ink">
          <h2 className="font-serif text-2xl font-semibold">最新报告</h2>
          <Link to="/reports" className="text-xs font-mono text-ash hover:text-ink underline">全部</Link>
        </div>
        {loading ? <p className="text-sm text-silver font-mono">加载中...</p>
          : reports.length ? (
            <div className="grid sm:grid-cols-2 gap-5 md:gap-6">
              {reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} variant="card" />)}
            </div>
          )
          : <EmptyState title="暂无报告" description="抓取更新后生成" />}
      </section>
    </div>
  )
}
