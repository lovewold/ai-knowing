import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Report, Article, Stats } from '../types'
import StatBlock from '../components/StatBlock'
import ReportCard from '../components/ReportCard'
import ArticleRow from '../components/ArticleRow'
import EmptyState from '../components/EmptyState'

const PIPELINE = ['数据源抓取', '信噪比过滤', 'AI 报告生成', '场景衍生分析']

export default function HomePage() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [reports, setReports] = useState<Report[]>([])
  const [articles, setArticles] = useState<Article[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getStats(), api.getReports(), api.getArticles()])
      .then(([s, r, a]) => { setStats(s); setReports(r.slice(0, 6)); setArticles(a.slice(0, 8)) })
      .catch(console.error).finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <section className="border-b border-ink">
        <div className="max-w-6xl mx-auto px-6 py-16 md:py-24">
          <h1 className="font-serif text-4xl md:text-6xl font-semibold leading-tight">
            AI 全知<br /><span className="italic">行业</span>知识库
          </h1>
          <p className="mt-6 text-ash max-w-lg text-sm md:text-base leading-relaxed">
            自动抓取 AI 行业资讯，信噪比过滤后入库，AI 自动生成技术报告与场景分析，构建可检索的行业知识库。
          </p>
        </div>
      </section>
      {stats && (
        <section className="border-b border-ink bg-mist">
          <div className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBlock label="AI 报告" value={stats.reports} />
            <StatBlock label="资讯条目" value={stats.articles} />
            <StatBlock label="高信号" value={stats.high_signal} />
            <StatBlock label="数据源" value={stats.sources} />
          </div>
        </section>
      )}
      <section className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-2 border border-ink">
          <div className="border-b md:border-b-0 md:border-r border-ink p-6 md:p-8">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-ink">
              <h2 className="font-serif text-xl font-semibold">最新报告</h2>
              <Link to="/reports" className="text-xs font-mono text-ash hover:text-ink underline">查看全部</Link>
            </div>
            {loading ? <p className="text-sm text-silver font-mono">加载中...</p>
              : reports.length ? reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} />)
              : <EmptyState title="暂无报告" description="触发抓取后将自动生成 AI 报告" />}
          </div>
          <div className="p-6 md:p-8">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-ink">
              <h2 className="font-serif text-xl font-semibold">最新资讯</h2>
              <Link to="/articles" className="text-xs font-mono text-ash hover:text-ink underline">查看全部</Link>
            </div>
            {loading ? <p className="text-sm text-silver font-mono">加载中...</p>
              : articles.length ? articles.map((a, i) => <ArticleRow key={a.id} article={a} index={i} />)
              : <EmptyState title="暂无资讯" description="点击顶部立即抓取" />}
          </div>
        </div>
      </section>
      <section className="border-b border-ink bg-mist">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-1">每日晨报</p>
            <p className="text-sm text-ash">过去 24 小时高信噪比 AI 资讯 · 单次 LLM 生成导语</p>
          </div>
          <Link to="/hotspot" className="line-border px-4 py-2 text-sm font-medium hover:bg-ink hover:text-paper shrink-0">
            查看咨询汇总
          </Link>
        </div>
      </section>
      <section className="border-t border-ink bg-mist">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <h2 className="font-serif text-lg font-semibold mb-8 text-center">内容处理流水线</h2>
          <div className="flex flex-col md:flex-row">
            {PIPELINE.map((step, i) => (
              <div key={step} className="flex items-center flex-1">
                <div className="flex-1 border border-ink bg-paper p-4 text-center">
                  <span className="block font-mono text-[10px] text-silver mb-1">STEP {i + 1}</span>
                  <span className="block text-sm font-medium">{step}</span>
                </div>
                {i < PIPELINE.length - 1 && <span className="hidden md:block px-2 font-mono">&rarr;</span>}
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
