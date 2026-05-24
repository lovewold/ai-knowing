import { NavLink, Outlet } from 'react-router-dom'
import { useState } from 'react'
import { api } from '../api/client'

const navItems = [
  { to: '/', label: '首页', end: true },
  { to: '/hotspot', label: '咨询汇总', end: false },
  { to: '/articles', label: '资讯', end: false },
  { to: '/agents', label: 'Agent工具', end: false },
  { to: '/briefing', label: '每日晨报', end: false },
  { to: '/reports', label: '报告', end: false },
  { to: '/sources', label: '数据源', end: false },
  { to: '/admin', label: '管理', end: false },
]

export default function Layout() {
  const [crawlStatus, setCrawlStatus] = useState<string | null>(null)
  const [crawling, setCrawling] = useState(false)

  async function handleCrawl() {
    setCrawling(true)
    setCrawlStatus('抓取中...')
    try {
      const res = await api.triggerCrawl()
      setCrawlStatus(
        res.status === 'queued'
          ? `已排队: ${res.task_id?.slice(0, 8)}`
          : `完成: 新增 ${res.result?.saved ?? 0} 条`,
      )
    } catch {
      setCrawlStatus('抓取失败，请检查后端')
    } finally {
      setCrawling(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <div className="h-1 bg-ink" />
      <header className="border-b border-ink bg-paper sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <NavLink to="/" className="flex items-baseline gap-3">
              <span className="font-serif text-2xl font-semibold">AI全知</span>
              <span className="hidden sm:inline text-xs font-mono text-silver tracking-widest uppercase">Knowledge Base</span>
            </NavLink>
            <nav className="hidden md:flex items-center">
              {navItems.map(({ to, label, end }) => (
                <NavLink key={to} to={to} end={end}
                  className={({ isActive }) => `px-4 py-2 text-sm font-medium border-l border-ink ${isActive ? 'bg-ink text-paper' : 'text-ash hover:bg-mist'}`}
                >{label}</NavLink>
              ))}
            </nav>
            <button onClick={handleCrawl} disabled={crawling}
              className="line-border px-4 py-1.5 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40">
              {crawling ? '抓取中...' : '抓取更新'}
            </button>
          </div>
          <nav className="md:hidden flex border-t border-ink">
            {navItems.map(({ to, label, end }) => (
              <NavLink key={to} to={to} end={end}
                className={({ isActive }) => `flex-1 py-2.5 text-center text-xs font-medium border-r border-ink last:border-r-0 ${isActive ? 'bg-ink text-paper' : 'text-ash'}`}
              >{label}</NavLink>
            ))}
          </nav>
        </div>
        {crawlStatus && <div className="border-t border-ink bg-mist px-6 py-2 text-xs font-mono text-ash text-center">{crawlStatus}</div>}
      </header>
      <main className="flex-1"><Outlet /></main>
      <footer className="border-t border-ink">
        <div className="max-w-6xl mx-auto px-6 py-8 flex justify-between text-xs text-silver font-mono">
          <span>AI全知 / 资讯抓取 / 信息过滤 / AI 报告</span>
          <span>2026 AI KNOWLEDGE BASE</span>
        </div>
      </footer>
    </div>
  )
}
