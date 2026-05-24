import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import type { KnowledgeEntry } from '../types'
import ReportMarkdown from '../components/ReportMarkdown'
import KnowledgeAskPanel from '../components/KnowledgeAskPanel'
import KnowledgeReportPanel from '../components/KnowledgeReportPanel'

export default function KnowledgeDetailPage() {
  const { id } = useParams()
  const [entry, setEntry] = useState<KnowledgeEntry | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    api.getKnowledge(Number(id)).then(setEntry).catch(() => setEntry(null)).finally(() => setLoading(false))
  }, [id])

  if (loading) return <p className="p-10 text-sm text-silver font-mono">{'\u52a0\u8f7d\u4e2d...'}</p>
  if (!entry) return <p className="p-10 text-sm">{'\u6761\u76ee\u4e0d\u5b58\u5728'}</p>

  return (
    <div className="max-w-7xl mx-auto px-6 py-10">
      <Link to="/knowledge" className="text-xs font-mono text-ash hover:text-ink underline">{'\u2190 \u77e5\u8bc6\u5e93'}</Link>
      <header className="mt-4 mb-8 pb-6 border-b border-ink xl:pr-[304px]">
        <div className="flex flex-wrap items-center gap-2 text-[10px] font-mono text-silver uppercase">
          <span>{entry.kind}</span>
          {entry.stale && <span className="text-amber-800 border border-amber-600 px-1.5">{'\u8d85 30 \u5929\u672a\u9a8c\u8bc1'}</span>}
          {entry.last_verified_at && <span>{'\u9a8c\u8bc1 '}{new Date(entry.last_verified_at).toLocaleDateString('zh-CN')}</span>}
        </div>
        <h1 className="text-3xl font-semibold mt-3">{entry.name}</h1>
        {entry.summary && <p className="text-base text-ash mt-3 leading-relaxed max-w-3xl">{entry.summary}</p>}
        {entry.external_url && (
          <a href={entry.external_url} target="_blank" rel="noopener noreferrer" className="inline-block mt-4 text-sm underline">
            {'\u5b98\u65b9\u94fe\u63a5 \u2197'}
          </a>
        )}
      </header>

      <div className="flex flex-col xl:flex-row xl:items-start xl:gap-8">
        <div className="flex-1 min-w-0 order-2 xl:order-1">
          {entry.content_md ? (
            <article className="prose-report border border-smoke p-6 md:p-8 bg-paper">
              <ReportMarkdown content={entry.content_md} />
            </article>
          ) : (
            <div className="border border-smoke p-8 bg-mist/30 text-sm text-ash leading-relaxed">
              <p>{'\u6682\u65e0\u6559\u7a0b\u6587\u6863\u3002\u8bf7\u5728\u7ba1\u7406\u540e\u53f0\u4f7f\u7528\u300cAI \u6279\u91cf\u751f\u6210\u6587\u6863\u300d\uff0c\u6216\u8fdb\u5165\u7f16\u8f91\u9875\u624b\u52a8\u64b0\u5199\u3002'}</p>
              <Link to={`/admin/knowledge/${entry.id}/edit`} className="inline-block mt-4 text-sm underline">{'\u7f16\u8f91\u6587\u6863 \u2192'}</Link>
            </div>
          )}
        </div>
        <aside className="w-full xl:w-[280px] xl:shrink-0 xl:sticky xl:top-6 space-y-4 order-1 xl:order-2 mb-6 xl:mb-0 xl:ml-auto">
          <KnowledgeAskPanel entryId={entry.id} entryName={entry.name} />
          <KnowledgeReportPanel entryId={entry.id} entryName={entry.name} />
        </aside>
      </div>
    </div>
  )
}
