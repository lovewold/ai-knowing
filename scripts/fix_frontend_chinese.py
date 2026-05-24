# -*- coding: utf-8 -*-
"""
Repair UTF-8 Chinese text in frontend files.
Run: py -3 scripts/fix_frontend_chinese.py
Always use this script (or \\u escapes) when writing Chinese to TSX — never rely on
PowerShell/heredoc which corrupts encoding on Windows.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

# Full file replacements (guaranteed correct UTF-8)
FILES: dict[str, str] = {}

FILES["src/pages/HomePage.tsx"] = r'''import { useEffect, useState } from 'react'
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
          <h1 className="font-serif text-4xl md:text-5xl font-semibold leading-tight">''' + "AI\u5168\u77e5" + r'''</h1>
          <p className="mt-4 text-ash max-w-2xl text-sm md:text-base leading-relaxed">
            ''' + "\u591a\u6e90 AI \u8d44\u8baf\u805a\u5408\uff0c\u6309\u4fe1\u566a\u6bd4\u52a8\u6001\u5206\u5c42\u3002\u6bcf\u65e5\u6668\u62a5\u4e0e\u6df1\u5ea6\u62a5\u544a\uff0c\u52a9\u4f60\u5feb\u901f\u628a\u63e1 AI \u884c\u4e1a\u8109\u640f\u3002" + r'''
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              to="/news"
              className="line-border px-6 py-2.5 text-sm font-medium hover:bg-ink hover:text-paper transition-colors"
            >
              ''' + "\u6d4f\u89c8 AI \u8d44\u8baf" + r'''
            </Link>
            <Link
              to="/reports"
              className="px-6 py-2.5 text-sm font-medium border border-smoke text-ash hover:border-ink hover:text-ink transition-colors"
            >
              ''' + "\u67e5\u770b\u62a5\u544a" + r'''
            </Link>
          </div>
        </div>
      </section>

      <HomeBriefingSection />

      {stats && (
        <section className="border-b border-ink bg-mist">
          <div className="max-w-6xl mx-auto px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatBlock label="''' + "\u8d44\u8baf" + r'''" value={stats.articles} />
            <StatBlock label="''' + "\u9ad8\u4fe1\u53f7" + r'''" value={stats.high_signal} />
            <StatBlock label="''' + "\u62a5\u544a" + r'''" value={stats.reports} />
            <StatBlock label="''' + "\u6570\u636e\u6e90" + r'''" value={stats.sources} />
          </div>
        </section>
      )}

      <section className="max-w-6xl mx-auto px-6 py-14 md:py-16">
        <div className="flex items-center justify-between mb-8 pb-5 border-b border-ink">
          <h2 className="font-serif text-2xl font-semibold">''' + "\u6700\u65b0\u62a5\u544a" + r'''</h2>
          <Link to="/reports" className="text-xs font-mono text-ash hover:text-ink underline">''' + "\u5168\u90e8" + r'''</Link>
        </div>
        {loading ? <p className="text-sm text-silver font-mono">''' + "\u52a0\u8f7d\u4e2d..." + r'''</p>
          : reports.length ? (
            <div className="grid sm:grid-cols-2 gap-5 md:gap-6">
              {reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} variant="card" />)}
            </div>
          )
          : <EmptyState title="''' + "\u6682\u65e0\u62a5\u544a" + r'''" description="''' + "\u6293\u53d6\u66f4\u65b0\u540e\u751f\u6210" + r'''" />}
      </section>
    </div>
  )
}
'''

FILES["src/pages/ReportsPage.tsx"] = r'''import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { api } from '../api/client'
import type { Report } from '../types'
import ReportCard from '../components/ReportCard'
import EmptyState from '../components/EmptyState'
import CustomReportPanel from '../components/CustomReportPanel'

const filters = [
  { key: '', label: ''' + "\u5168\u90e8" + r''' },
  { key: 'custom', label: ''' + "\u81ea\u5b9a\u4e49" + r''' },
  { key: 'trend', label: ''' + "\u8d8b\u52bf" + r''' },
  { key: 'tool', label: ''' + "\u5de5\u5177" + r''' },
  { key: 'agent_survey', label: ''' + "Agent\u5168\u666f" + r''' },
  { key: 'daily_briefing', label: ''' + "\u6bcf\u65e5\u6668\u62a5" + r''' },
  { key: 'scenario', label: ''' + "\u573a\u666f" + r''' },
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
        <h1 className="font-serif text-3xl font-semibold">''' + "\u62a5\u544a" + r'''</h1>
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
        <p className="text-sm text-silver font-mono">''' + "\u52a0\u8f7d\u4e2d..." + r'''</p>
      ) : reports.length ? (
        <div className="border-t border-ink">{reports.map((r, i) => <ReportCard key={r.id} report={r} index={i} />)}</div>
      ) : (
        <EmptyState
          title="''' + "\u6682\u65e0\u62a5\u544a" + r'''"
          description="''' + "\u8f93\u5165\u63cf\u8ff0\u751f\u6210\u68c0\u7d22\u5f0f\u62a5\u544a" + r'''"
        />
      )}
    </div>
  )
}
'''

FILES["index.html"] = f'''<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI\u5168\u77e5 - \u591a\u6e90 AI \u8d44\u8baf\u805a\u5408</title>
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

# Patch SignalBadge to use unicode escapes (immune to corruption)
FILES["src/components/SignalBadge.tsx"] = r'''const statusLabels: Record<string, string> = {
  high: '\u9ad8\u4fe1\u53f7',
  medium: '\u89c2\u5bdf',
  low: '\u4f4e\u4fe1\u53f7',
}

interface SignalBadgeProps {
  status: string | null
  score?: number | null
}

export default function SignalBadge({ status, score }: SignalBadgeProps) {
  if (!status) return null
  return (
    <span className="inline-flex items-center gap-1.5 font-mono text-[10px]">
      <span className="border border-ink px-1.5 py-0.5">{statusLabels[status] ?? status}</span>
      {score != null && <span className="text-silver">{`${Math.round(score)}\u5206`}</span>}
    </span>
  )
}
'''

CORRUPT_RE = re.compile(
    r"(label:\s*')(\?{2,})(')|"
    r"(title=\")(\?{2,})(\")|"
    r"(description=\")(\?{2,})(\")|"
    r"(<title>)AI\?+"
)


def scan_corruption() -> list[str]:
    issues: list[str] = []
    paths = list((FRONTEND / "src").rglob("*.tsx")) + list((FRONTEND / "src").rglob("*.ts")) + [FRONTEND / "index.html"]
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            issues.append(f"{p.relative_to(ROOT)}: invalid UTF-8")
            continue
        if re.search(r"['\"`][^'\"`]*\?\?[^'\"`]*['\"`]", text):
            if "?? 0" not in text and "?? ''" not in text and "?? null" not in text:
                issues.append(str(p.relative_to(ROOT)))
        if "AI??" in text or "AI??" in text:
            issues.append(str(p.relative_to(ROOT)))
    return issues


def main() -> int:
    fixed = 0
    for rel, content in FILES.items():
        path = FRONTEND / rel if not rel.startswith("src") else FRONTEND / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content.strip() + "\n", encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
        fixed += 1

    remaining = scan_corruption()
    if remaining:
        print("\nWARNING: possible corruption still in:")
        for r in remaining:
            print(" ", r)
        return 1
    print(f"\nOK: {fixed} files written, no ?? corruption detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
