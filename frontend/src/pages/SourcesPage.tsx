import { useEffect, useState } from 'react'
import { api } from '../api/client'
import type { Source } from '../types'

const typeLabels: Record<string, string> = { rss: 'RSS', arxiv: 'ArXiv', hackernews: 'Hacker News', github_trending: 'GitHub Trending' }

function weightLabel(w: number) {
  if (w >= 90) return 'S'
  if (w >= 70) return 'A'
  if (w >= 50) return 'B'
  if (w >= 30) return 'C'
  return 'D'
}

export default function SourcesPage() {
  const [sources, setSources] = useState<Source[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => { api.getSources().then(setSources).catch(console.error).finally(() => setLoading(false)) }, [])

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      <header className="mb-10 pb-6 border-b border-ink">
        <h1 className="font-serif text-3xl font-semibold">数据源</h1>

      </header>
      {loading ? <p className="text-sm text-silver font-mono">加载中...</p> : (
        <div className="border border-ink">
          <div className="grid grid-cols-12 bg-mist border-b border-ink text-[10px] font-mono uppercase text-silver">
            <div className="col-span-4 px-4 py-3 border-r border-ink">名称</div>
            <div className="col-span-2 px-4 py-3 border-r border-ink">类型</div>
            <div className="col-span-2 px-4 py-3 border-r border-ink">权重</div>
            <div className="col-span-1 px-4 py-3 border-r border-ink">语言</div>
            <div className="col-span-3 px-4 py-3">ID</div>
          </div>
          {sources.map((s, i) => (
            <div key={s.id} className={`grid grid-cols-12 text-sm ${i < sources.length - 1 ? 'border-b border-smoke' : ''} hover:bg-mist`}>
              <div className="col-span-4 px-4 py-4 border-r border-smoke font-medium">{s.name}</div>
              <div className="col-span-2 px-4 py-4 border-r border-smoke text-xs text-ash">{typeLabels[s.type] ?? s.type}</div>
              <div className="col-span-2 px-4 py-4 border-r border-smoke"><span className="font-mono">{s.weight}</span> <span className="text-[10px] font-mono border border-ink px-1 ml-1">{weightLabel(s.weight)}</span></div>
              <div className="col-span-1 px-4 py-4 border-r border-smoke font-mono text-xs">{s.language}</div>
              <div className="col-span-3 px-4 py-4 font-mono text-xs text-silver truncate">{s.id}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
