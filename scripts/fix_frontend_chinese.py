# -*- coding: utf-8 -*-
"""Fix frontend Chinese encoding (?? / mojibake) and verify all tsx files."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "frontend" / "src"
FRONTEND = ROOT.parent

HOME_PAGE = r'''import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Report, Article, Stats } from '../types'
import StatBlock from '../components/StatBlock'
import ReportCard from '../components/ReportCard'
import ArticleRow from '../components/ArticleRow'
import EmptyState from '../components/EmptyState'

const PIPELINE = ['\u6570\u636e\u6e90\u6293\u53d6', '\u4fe1\u566a\u6bd4\u8fc7\u6ee4', 'AI \u62a5\u544a\u751f\u6210', '\u573a\u666f\u884d\u751f\u5206\u6790']

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
            AI \u5168\u77e5<br /><span className="italic">\u884c\u4e1a</span>\u77e5\u8bc6\u5e93
          </h1>
          <p className="mt-6 text-ash max-w-lg text-sm md:text-base leading-relaxed">
            \u81ea\u52a8\u6293\u53d6 AI \u884c\u4e1a\u8d44\u8baf\uff0c\u4fe1\u566a\u6bd4\u8fc7\u6ee4\u540e\u5165\u5e93\uff0cAI \u81ea\u52a8\u751f\u6210\u6280\u672f\u62a5\u544a\u4e0e\u573a\u666f\u5206\u6790\uff0c\u6784\u5efa\u53ef\u68c0\u7d22\u7684\u884c\u4e1a\u77e5\u8bc6\u5e93\u3002
          </p>
        </div>
      </section>
      {stats && (
        <section className="border-b border-ink bg-mist">
          <div className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBlock label="AI \u62a5\u544a" value={stats.reports} />
            <StatBlock label="\u8d44\u8baf\u6761\u76ee" value={stats.articles} />
            <StatBlock label="\u9ad8\u4fe1\u53f7" value={stats.high_signal} />
            <StatBlock label="\u6570\u636e\u6e90" value={stats.sources} />
          </div>
        </section>
      )}
      <section className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid md:grid-cols-2 border border-ink">
          <motion.div className="border-b md:border-b-0 md:border-r border-ink p-6 md:p-8">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-ink">
              <h2 className="font-serif text-xl font-semibold">\u6700\u65b0\u62a5\u544a</h2>
              <Link to="/reports" className="text-xs font-mono text-ash hover:text-ink underline">\u67e5\u770b\u5168\u90e8</Link>
            </div>
            {loading ? <p className="text-sm text-silver font-mono">\u52a0\u8f7d\u4e2d...</p>
              : reports.length ? reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} />)
              : <EmptyState title="\u6682\u65e0\u62a5\u544a" description="\u89e6\u53d1\u6293\u53d6\u540e\u5c06\u81ea\u52a8\u751f\u6210 AI \u62a5\u544a" />}
          </div>
          <div className="p-6 md:p-8">
            <div className="flex items-center justify-between mb-6 pb-4 border-b border-ink">
              <h2 className="font-serif text-xl font-semibold">\u6700\u65b0\u8d44\u8baf</h2>
              <Link to="/articles" className="text-xs font-mono text-ash hover:text-ink underline">\u67e5\u770b\u5168\u90e8</Link>
            </div>
            {loading ? <p className="text-sm text-silver font-mono">\u52a0\u8f7d\u4e2d...</p>
              : articles.length ? articles.map((a, i) => <ArticleRow key={a.id} article={a} index={i} />)
              : <EmptyState title="\u6682\u65e0\u8d44\u8baf" description="\u70b9\u51fb\u9876\u90e8\u7acb\u5373\u6293\u53d6" />}
          </div>
        </div>
      </section>
      <section className="border-b border-ink bg-mist">
        <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-widest text-silver mb-1">\u6bcf\u65e5\u6668\u62a5</p>
            <p className="text-sm text-ash">\u8fc7\u53bb 24 \u5c0f\u65f6\u9ad8\u4fe1\u566a\u6bd4 AI \u8d44\u8baf \u00b7 \u5355\u6b21 LLM \u751f\u6210\u5bfc\u8bed</p>
          </div>
          <Link to="/hotspot" className="line-border px-4 py-2 text-sm font-medium hover:bg-ink hover:text-paper shrink-0">
            \u67e5\u770b\u54a8\u8be2\u6c47\u603b
          </Link>
        </div>
      </section>
      <section className="border-t border-ink bg-mist">
        <div className="max-w-6xl mx-auto px-6 py-12">
          <h2 className="font-serif text-lg font-semibold mb-8 text-center">\u5185\u5bb9\u5904\u7406\u6d41\u6c34\u7ebf</h2>
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
'''

LAYOUT = r'''import { NavLink, Outlet } from 'react-router-dom'
import { useState } from 'react'
import { api } from '../api/client'

const navItems = [
  { to: '/', label: '\u9996\u9875', end: true },
  { to: '/hotspot', label: '\u54a8\u8be2\u6c47\u603b', end: false },
  { to: '/articles', label: '\u8d44\u8baf', end: false },
  { to: '/agents', label: 'Agent\u5de5\u5177', end: false },
  { to: '/briefing', label: '\u6bcf\u65e5\u6668\u62a5', end: false },
  { to: '/reports', label: '\u62a5\u544a', end: false },
  { to: '/sources', label: '\u6570\u636e\u6e90', end: false },
  { to: '/admin', label: '\u7ba1\u7406', end: false },
]

export default function Layout() {
  const [crawlStatus, setCrawlStatus] = useState<string | null>(null)
  const [crawling, setCrawling] = useState(false)

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
      setCrawlStatus('\u6293\u53d6\u5931\u8d25\uff0c\u8bf7\u68c0\u67e5\u540e\u7aef')
    } finally {
      setCrawling(false)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <motion.div className="h-1 bg-ink" />
      <header className="border-b border-ink bg-paper sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <NavLink to="/" className="flex items-baseline gap-3">
              <span className="font-serif text-2xl font-semibold">AI\u5168\u77e5</span>
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
              {crawling ? '\u6293\u53d6\u4e2d...' : '\u6293\u53d6\u66f4\u65b0'}
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
          <span>AI\u5168\u77e5 / \u8d44\u8baf\u6293\u53d6 / \u4fe1\u606f\u8fc7\u6ee4 / AI \u62a5\u544a</span>
          <span>2026 AI KNOWLEDGE BASE</span>
        </motion.div>
      </footer>
    </div>
  )
}
'''

REPORTS_PAGE = r'''import { useEffect, useState } from 'react'
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
        <h1 className="font-serif text-3xl font-semibold">AI \u62a5\u544a</h1>
        <p className="mt-2 text-sm text-ash">
          \u81ea\u52a8\u751f\u6210\u7684\u6280\u672f\u62a5\u544a\uff0c\u6216\u7528\u81ea\u7136\u8bed\u8a00\u63cf\u8ff0\u751f\u6210\u4efb\u610f\u7c7b\u578b\u62a5\u544a
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
        <p className="text-sm text-silver font-mono">\u52a0\u8f7d\u4e2d...</p>
      ) : reports.length ? (
        <div className="border-t border-ink">{reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} />)}</div>
      ) : (
        <EmptyState
          title="\u6682\u65e0\u62a5\u544a"
          description="\u5728\u4e0a\u65b9\u586b\u5199\u62a5\u544a\u63cf\u8ff0\u751f\u6210\u81ea\u5b9a\u4e49\u62a5\u544a\uff0c\u6216\u89e6\u53d1\u6293\u53d6\u81ea\u52a8\u751f\u6210"
        />
      )}
    </div>
  )
}
'''

INDEX_HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI\u5168\u77e5 - AI \u884c\u4e1a\u77e5\u8bc6\u5e93</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=JetBrains+Mono:wght@400;500&family=Noto+Sans+SC:wght@300;400;500;600&family=Noto+Serif+SC:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet" />
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
'''

FILES = {
    "pages/HomePage.tsx": HOME_PAGE,
    "components/Layout.tsx": LAYOUT,
    "pages/ReportsPage.tsx": REPORTS_PAGE,
}

MOJIBAKE_RE = re.compile(r"[\u00c3\u00c2\u00e5\u00e6\u00e8\u00e9\u00ef]{2,}")
BAD_STRING_RE = re.compile(r"""['"`][^'"`]*\?{2,}""")


def decode_unicode(content: str) -> str:
    return content.encode("utf-8").decode("unicode_escape")


def strip_motion_typos(content: str) -> str:
    out = content
    while "<motion.div" in out:
        out = out.replace("<motion.div", "<div")
    out = out.replace("</motion.div>", "</div>")
    return out


def write_utf8(path: Path, raw: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = strip_motion_typos(decode_unicode(raw))
    path.write_text(text, encoding="utf-8", newline="\n")


def try_fix_mojibake(text: str) -> str | None:
    try:
        fixed = text.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return None
    return fixed if fixed != text else None


def scan(path: Path) -> list[str]:
    issues: list[str] = []
    rel = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    for no, line in enumerate(text.splitlines(), 1):
        if BAD_STRING_RE.search(line) and "?? '" not in line and "?? ''" not in line and "?? 0" not in line:
            issues.append(f"{rel}:{no} corrupted: {line.strip()[:80]}")
        if MOJIBAKE_RE.search(line):
            issues.append(f"{rel}:{no} mojibake: {line.strip()[:80]}")
    return issues


def main() -> int:
    for rel, raw in FILES.items():
        write_utf8(ROOT / rel, raw)
        print(f"fixed: {rel}")

    write_utf8(FRONTEND / "index.html", INDEX_HTML)
    print("fixed: index.html")

    for path in sorted(ROOT.rglob("*.tsx")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in FILES:
            continue
        text = path.read_text(encoding="utf-8")
        if MOJIBAKE_RE.search(text):
            fixed = try_fix_mojibake(text)
            if fixed:
                path.write_text(fixed, encoding="utf-8", newline="\n")
                print(f"mojibake-fixed: {rel}")

    issues: list[str] = []
    for path in sorted(ROOT.rglob("*.tsx")):
        issues.extend(scan(path))

    if issues:
        print("\nRemaining issues:")
        for item in issues:
            print(" -", item)
        return 1

    print("\nAll frontend Chinese strings OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
