import { NavLink, Outlet } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../api/client'

const SIDEBAR_KEY = 'aiknow_sidebar_collapsed'

const navItems = [
  { to: '/', label: '\u9996\u9875', icon: '\u2302', end: true },
  { to: '/news', label: 'AI \u8d44\u8baf', icon: '\u2261', end: false },
  { to: '/reports', label: '\u62a5\u544a', icon: '\u2709', end: false },
  { to: '/agents', label: 'Agent', icon: '\u2699', end: false },
  { to: '/models', label: '\u6a21\u578b\u5e7f\u573a', icon: '\u25c8', end: false },
  { to: '/knowledge', label: '\u77e5\u8bc6\u5e93', icon: '\u25a6', end: false },
]

export default function AppShell() {
  const [collapsed, setCollapsed] = useState(false)
  const [crawlStatus, setCrawlStatus] = useState<string | null>(null)
  const [crawling, setCrawling] = useState(false)

  useEffect(() => {
    setCollapsed(localStorage.getItem(SIDEBAR_KEY) === '1')
  }, [])

  function toggleSidebar() {
    setCollapsed((c) => {
      const next = !c
      localStorage.setItem(SIDEBAR_KEY, next ? '1' : '0')
      return next
    })
  }

  async function handleCrawl() {
    setCrawling(true)
    setCrawlStatus('\u6293\u53d6\u4e2d...')
    try {
      const res = await api.triggerCrawl()
      setCrawlStatus(
        res.status === 'queued'
          ? `\u5df2\u6392\u961f: ${res.task_id?.slice(0, 8)}`
          : `\u5b8c\u6210: \u65b0\u589e ${res.result?.saved ?? 0} \u6761`,
      )
    } catch {
      setCrawlStatus('\u6293\u53d6\u5931\u8d25')
    } finally {
      setCrawling(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-paper">
      <aside
        className={`shrink-0 border-r border-ink bg-mist/40 flex flex-col transition-all duration-200 ${
          collapsed ? 'w-[56px]' : 'w-[220px]'
        }`}
      >
        <div className={`border-b border-ink flex items-center h-14 ${collapsed ? 'justify-center px-2' : 'px-4'}`}>
          <NavLink to="/" className="font-semibold text-base truncate" title="AI\u5168\u77e5">
            {collapsed ? 'AI' : 'AI\u5168\u77e5'}
          </NavLink>
        </div>
        <nav className="flex-1 py-3 space-y-0.5 px-2">
          {navItems.map(({ to, label, icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              title={label}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-sm text-sm font-medium transition-colors ${
                  collapsed ? 'justify-center px-2 py-2.5' : 'px-3 py-2.5'
                } ${isActive ? 'bg-ink text-paper' : 'text-ash hover:bg-mist hover:text-ink'}`
              }
            >
              <span className="text-base w-5 text-center shrink-0" aria-hidden>{icon}</span>
              {!collapsed && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className={`border-t border-ink p-2 space-y-1 ${collapsed ? 'text-center' : ''}`}>
          <NavLink
            to="/admin"
            title="\u7ba1\u7406\u540e\u53f0"
            className={`block text-xs text-silver hover:text-ink ${collapsed ? 'py-2' : 'px-3 py-2 underline'}`}
          >
            {collapsed ? '\u2699' : '\u7ba1\u7406\u540e\u53f0'}
          </NavLink>
        </div>
      </aside>

      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-ink bg-paper flex items-center justify-between px-4 md:px-6 shrink-0">
          <button
            type="button"
            onClick={toggleSidebar}
            className="line-border px-3 py-1.5 text-sm font-medium hover:bg-mist"
            aria-label={collapsed ? '\u5c55\u5f00\u4fa7\u680f' : '\u6536\u8d77\u4fa7\u680f'}
          >
            {collapsed ? '\u2192' : '\u2190'}
          </button>
          <button
            onClick={handleCrawl}
            disabled={crawling}
            className="line-border px-4 py-1.5 text-sm font-medium hover:bg-ink hover:text-paper disabled:opacity-40"
          >
            {crawling ? '\u6293\u53d6\u4e2d...' : '\u6293\u53d6\u66f4\u65b0'}
          </button>
        </header>
        {crawlStatus && (
          <div className="border-b border-ink bg-mist px-4 py-2 text-xs font-mono text-ash text-center">{crawlStatus}</div>
        )}
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
